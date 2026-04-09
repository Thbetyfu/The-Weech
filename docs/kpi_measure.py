import asyncio
import time
import httpx
import psutil
import os


async def measure_ttft(prompt: str, ollama_url: str, model: str) -> float:
    """Time To First Token — waktu hingga token pertama muncul."""
    url = f"{ollama_url}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": True}

    start = time.monotonic()
    first_token_time = None

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, json=payload) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        import json
                        chunk = json.loads(line)
                        if chunk.get("response") and first_token_time is None:
                            first_token_time = time.monotonic() - start
                        if chunk.get("done"):
                            break
    except Exception as e:
        print(f"Ollama stream error: {e}")
        return 0.0

    return first_token_time or 0.0


def measure_memory_mb() -> float:
    """RAM yang dipakai proses Python saat ini (MB)."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


async def run_kpi_test():
    OLLAMA_URL = "http://127.0.0.1:11434"
    MODEL = "gemma:2b"
    TEST_PROMPT = "Jelaskan strategi konten untuk kreator teknologi di Indonesia dalam 3 poin."

    print("📊 Mengukur KPI Fase 1...")

    # Memastikan psutil tersedia (jika tidak akan throw saat import)

    # TTFT
    ttft = await measure_ttft(TEST_PROMPT, OLLAMA_URL, MODEL)
    if ttft == 0.0:
        print("❌ TTFT: Gagal! Ollama tidak merespon. Pastikan ollama serve dan llama3.2:3b aktif.")
    else:
        ttft_status = "✅" if ttft < 1.5 else "❌"
        print(f"{ttft_status} TTFT: {ttft:.2f}s (target: < 1.5s)")

    # Memory
    mem_mb = measure_memory_mb()
    mem_status = "✅" if mem_mb < 4096 else "❌"
    print(f"{mem_status} Memory (Testing script RSS): {mem_mb:.0f} MB (target: < 4096 MB)")

    print("\nSimpan hasil ini untuk laporan KPI Sprint 1F.")


if __name__ == "__main__":
    asyncio.run(run_kpi_test())
