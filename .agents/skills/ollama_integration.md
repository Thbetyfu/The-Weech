---
name: ollama_integration
description: >
  Panduan lengkap integrasi Ollama di Worker Node TheWeech. Berisi cara
  memanggil API, pull model, cek ketersediaan, handle error, dan pattern
  streaming token untuk Fase 2+.
---

# Ollama Integration Skill

## Ollama REST API Reference

Base URL: `http://localhost:11434`

| Endpoint | Method | Fungsi |
|----------|--------|--------|
| `/api/generate` | POST | Generate teks (non-streaming) |
| `/api/chat` | POST | Chat format dengan history |
| `/api/tags` | GET | Daftar model yang sudah di-pull |
| `/api/pull` | POST | Download model baru |
| `/api/show` | POST | Detail info model |
| `/api/ps` | GET | Model yang sedang loaded di memory |

---

## Cara Cek Ollama Aktif (Health Check)

```python
import httpx


async def check_ollama(base_url: str = "http://localhost:11434") -> bool:
    """Return True jika Ollama berjalan dan dapat diakses."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/api/tags")
            return resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False
```

---

## Cara Dapatkan Daftar Model yang Tersedia

```python
async def list_models(base_url: str) -> list[str]:
    """Kembalikan list nama model yang sudah di-pull."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{base_url}/api/tags")
        resp.raise_for_status()
        data = resp.json()
        return [m["name"] for m in data.get("models", [])]
```

---

## Inference Non-Streaming (Fase 1)

```python
async def run_inference(
    prompt: str,
    model: str,
    base_url: str,
    timeout: float = 120.0,
) -> tuple[str, float]:
    """
    Jalankan inference dan kembalikan (output_text, duration_detik).
    Raises: httpx.HTTPError jika Ollama error.
    """
    import time

    url = f"{base_url}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 512,   # batas token output
        },
    }

    start = time.monotonic()
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()

    elapsed = time.monotonic() - start
    output = resp.json().get("response", "").strip()
    return output, elapsed
```

---

## Inference Streaming — Token by Token (Fase 2+)

```python
import json
from collections.abc import AsyncIterator


async def stream_inference(
    prompt: str,
    model: str,
    base_url: str,
) -> AsyncIterator[str]:
    """
    Generator async yang yield satu token per iterasi.
    Untuk diteruskan ke WebSocket client secara real-time.
    """
    url = f"{base_url}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": True}

    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break
```

---

## Error Handling — Hierarki Exception

```python
import httpx
import logging

logger = logging.getLogger(__name__)


async def safe_inference(prompt: str, model: str, base_url: str) -> str | None:
    try:
        output, _ = await run_inference(prompt, model, base_url)
        return output

    except httpx.ConnectError:
        logger.error("❌ Ollama tidak berjalan. Pastikan 'ollama serve' aktif.")

    except httpx.TimeoutException:
        logger.error("⏱️ Inference timeout — prompt terlalu panjang atau model terlalu berat.")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.error(f"❌ Model '{model}' tidak ditemukan. Jalankan: ollama pull {model}")
        else:
            logger.error(f"❌ Ollama HTTP error: {e.response.status_code}")

    return None
```

---

## Pull Model Programatically

```python
async def pull_model(model: str, base_url: str) -> bool:
    """Download model jika belum ada. Return True jika berhasil."""
    url = f"{base_url}/api/pull"
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:  # pull bisa lama
            resp = await client.post(url, json={"name": model})
            resp.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Gagal pull model {model}: {e}")
        return False
```

---

## Rekomendasi Model per Use Case (Fase 1 PoC)

| Model | Size | VRAM | Cocok untuk |
|-------|------|------|------------|
| `llama3.2:3b` | ~2GB | ~3GB | CPU/GPU, default PoC |
| `qwen2.5:3b` | ~2GB | ~3GB | Alternatif, bahasa Indonesia lebih baik |
| `gemma3:4b` | ~3GB | ~4GB | Kualitas lebih tinggi, butuh RAM lebih |
| `llama3.2:1b` | ~1GB | ~2GB | Mesin sangat terbatas (worst-case test) |

---

## Cek Setup Ollama di Windows (Perintah Terminal)

```powershell
# Cek versi
ollama --version

# Lihat model yang sudah ada
ollama list

# Pull model untuk PoC
ollama pull llama3.2:3b

# Test inference manual
ollama run llama3.2:3b "Halo, siapa kamu?"

# Cek status server API
curl http://localhost:11434/api/tags
```

---

## Yang Harus Dihindari

| ❌ Masalah | ✅ Solusi |
|-----------|----------|
| Timeout 30 detik default | Set `timeout=120.0` untuk inference |
| Tidak cek apakah model tersedia | Panggil `list_models()` di startup |
| Stream dan non-stream dicampur | Pilih satu mode per session |
| Prompt > 4000 token | Potong di Orchestrator sebelum kirim |
