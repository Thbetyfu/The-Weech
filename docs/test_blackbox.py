import asyncio
import httpx
import websockets
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("BlackboxTest")

ORCHESTRATOR_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000"

async def test_api_health():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{ORCHESTRATOR_URL}/health")
        assert res.status_code == 200, "Health check failed!"
        data = res.json()
        logger.info(f"✅ [API] Health Check OK - Active Workers: {len(data['workers'])}")

async def test_wallet_apis():
    dummy_worker = "worker-dummy-999"
    async with httpx.AsyncClient() as client:
        # 1. Check Balance
        res = await client.get(f"{ORCHESTRATOR_URL}/api/v1/wallet/{dummy_worker}")
        assert res.status_code == 200
        balance = res.json()["verified_balance"]
        logger.info(f"✅ [API] Wallet Read OK - Balance: {balance}")

        # 2. Attempt Invalid Package Redeem
        res2 = await client.post(f"{ORCHESTRATOR_URL}/api/v1/wallet/redeem", json={
            "worker_id": dummy_worker,
            "package": "INVALID_PACK"
        })
        assert res2.status_code == 400
        logger.info("✅ [API] Wallet Redeem Validation (Invalid Package) OK - Expected 400")

        # 3. Attempt Valid Package but Insufficient Balance
        res3 = await client.post(f"{ORCHESTRATOR_URL}/api/v1/wallet/redeem", json={
            "worker_id": dummy_worker,
            "package": "PRO_MONTHLY"
        })
        # If balance >= 5000 it will return 200, else 402
        if balance < 5000:
            assert res3.status_code == 402, f"Expected 402, got {res3.status_code}"
            logger.info("✅ [API] Wallet Redeem Guard (Insufficient Balance) OK - Expected 402")
        else:
            assert res3.status_code == 200
            logger.info("✅ [API] Wallet Redeem SUCCESS")

async def test_websocket_connectivity():
    try:
        async with websockets.connect(f"{WS_URL}/ws/client/test-task-123") as ws:
            logger.info("✅ [WS] Client WebSocket Connection OK")
            
        # Simulate worker connecting
        async with websockets.connect(f"{WS_URL}/ws/worker/test-worker-1?token=WEECH-NODE-SECRET-2026") as ws:
            logger.info("✅ [WS] Worker WebSocket Connection OK")
            
            # Send intro payload
            await ws.send(json.dumps({
                "type": "hardware_specs",
                "os": "BlackBoxTestOS",
                "cpu_cores": 16,
                "ram_gb": 32,
                "ollama_model": "test-model"
            }))
            logger.info("✅ [WS] Worker Hardware Telemetry transmission OK")
    except Exception as e:
        logger.error(f"❌ [WS] WebSocket test failed! The Orchestrator might be offline. Error: {e}")
        sys.exit(1)

async def test_b2b_agency_apis():
    async with httpx.AsyncClient() as client:
        # 1. Blind Spot: Akses B2B tanpa API_KEY yang terdaftar di DB (RBAC Test)
        res_invalid = await client.get(f"{ORCHESTRATOR_URL}/api/v1/agency/discount-status?agency_api_key=FAKE_KEY")
        assert res_invalid.status_code == 403, "🚨 Blind Spot: RBAC Agensi bobol! Fake Key lolos."
        logger.info("✅ [API] B2B Guard MCN (Invalid API Key) OK - Expected 403")
        
        # 2. Matchmaking Radar Blind Spot (Parameter API)
        res_match = await client.get(f"{ORCHESTRATOR_URL}/api/v1/agency/matchmaking?agency_api_key=FAKE_KEY")
        assert res_match.status_code == 403, "🚨 Blind Spot: Matchmaking terbaca tanpa lisensi Agensi!"
        logger.info("✅ [API] B2B Matchmaking Shield OK - Expected 403")

async def main():
    logger.info("=== 🧪 STARTING BLACKBOX & INTEGRATION TEST (Fase 1-5) ===")
    try:
        await test_websocket_connectivity()
        await test_api_health()
        await test_wallet_apis()
        await test_b2b_agency_apis()
        logger.info("🎉 SEMUA TEST LULUS! Sistem Anti-Rapuh terverifikasi.")
    except AssertionError as e:
        logger.error(f"❌ ASSERTION FAILED: {e}")
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
