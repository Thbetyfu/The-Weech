"""
TheWeech Worker Node — Entry Point
Fase 1: Konek ke Orchestrator via WebSocket, proses prompt dengan Ollama lokal.
"""

import asyncio
import json
import platform
import uuid
import logging
from datetime import datetime

import httpx
import websockets
from dotenv import load_dotenv
import os

# Rich untuk output terminal yang cantik
try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    use_rich = True
except ImportError:
    use_rich = False

load_dotenv()

# --------------------------------------------------------------------------- #
# Config dari .env
# --------------------------------------------------------------------------- #
ORCHESTRATOR_WS_URL = os.getenv("ORCHESTRATOR_WS_URL", "ws://localhost:8000/ws/worker")
WORKER_ID = os.getenv("WORKER_ID", f"worker-{uuid.uuid4().hex[:8]}")
WORKER_NAME = os.getenv("WORKER_NAME", platform.node())
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Skema Ekstensi B2B (MCN Node)
IS_ENTERPRISE = os.getenv("ENTERPRISE_MODE", "false").lower() == "true"
AGENCY_API_KEY = os.getenv("AGENCY_API_KEY", "")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Ollama inference
# --------------------------------------------------------------------------- #
async def run_inference(prompt: str) -> str:
    """Kirim prompt ke Ollama lokal, kembalikan hasil teks."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()


# --------------------------------------------------------------------------- #
# Worker specs (untuk register ke Orchestrator)
# --------------------------------------------------------------------------- #
import psutil

def get_specs() -> dict:
    """Mengumpulkan telemetry spesifikasi hardware mesin node worker."""
    specs = {
        "worker_id": WORKER_ID,
        "name": WORKER_NAME,
        "os": platform.system(),
        "python": platform.python_version(),
        "ollama_model": OLLAMA_MODEL,
        "cpu_cores": "Unknown",
        "ram_gb": "Unknown"
    }

    try:
        if psutil:
            specs["cpu_cores"] = psutil.cpu_count(logical=True)
            specs["ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 2)
    except Exception as e:
        logger.warning(f"⚠️ Gagal membaca spec hardware lokal: {e}")

    return specs


# --------------------------------------------------------------------------- #
# Main WebSocket loop
# --------------------------------------------------------------------------- #
async def run_worker():
    ws_url = f"{ORCHESTRATOR_WS_URL}/{WORKER_ID}?token=WEECH-NODE-SECRET-2026"
    if IS_ENTERPRISE:
        ws_url += f"&is_enterprise=true&agency_api_key={AGENCY_API_KEY}"
        
    logger.info(f"🔗 Connecting to Orchestrator: {ws_url}")

    while True:  # auto-reconnect loop
        try:
            async with websockets.connect(ws_url) as ws:
                logger.info(f"✅ Connected as '{WORKER_ID}'")

                # Kirim register message dengan specs perangkat
                await ws.send(json.dumps({
                    "type": "register",
                    "specs": get_specs(),
                }))

                async for raw_msg in ws:
                    try:
                        msg = json.loads(raw_msg)
                    except json.JSONDecodeError:
                        logger.warning(f"Non-JSON received: {raw_msg}")
                        continue

                    msg_type = msg.get("type")

                    if msg_type == "ping":
                        # Balas ping dengan pong (heartbeat) & echo timestamp
                        pong_msg = {"type": "pong"}
                        if "ts" in msg:
                            pong_msg["ts"] = msg["ts"]
                        await ws.send(json.dumps(pong_msg))
                        logger.debug("💓 Pong sent")

                    elif msg_type == "task":
                        task_id = msg.get("task_id", "unknown")
                        prompt = msg.get("prompt", "")
                        logger.info(f"📥 Task received [{task_id}]: {prompt[:60]}...")

                        try:
                            start = datetime.now()
                            output = await run_inference(prompt)
                            elapsed = (datetime.now() - start).total_seconds()

                            logger.info(f"✅ Task [{task_id}] done in {elapsed:.2f}s")

                            await ws.send(json.dumps({
                                "type": "result",
                                "task_id": task_id,
                                "output": output,
                                "duration_seconds": elapsed,
                            }))

                        except Exception as e:
                            logger.error(f"❌ Inference error: {e}")
                            await ws.send(json.dumps({
                                "type": "error",
                                "task_id": task_id,
                                "message": str(e),
                            }))

                    else:
                        logger.debug(f"Unknown message type: {msg_type}")

        except (websockets.exceptions.ConnectionClosed,
                ConnectionRefusedError,
                OSError) as e:
            logger.warning(f"⚠️ Connection lost: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"💥 Unexpected error: {e}. Reconnecting in 10s...")
            await asyncio.sleep(10)


# --------------------------------------------------------------------------- #
# Entry
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    print("=" * 50)
    print(f"  TheWeech Worker Node")
    print(f"  ID     : {WORKER_ID}")
    print(f"  Model  : {OLLAMA_MODEL}")
    print(f"  Target : {ORCHESTRATOR_WS_URL}")
    print("=" * 50)

    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        print("\n🛑 Worker stopped by user.")
