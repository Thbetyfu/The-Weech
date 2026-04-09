import logging
from sqlalchemy import select
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

from core.database import SessionLocal
from core.models import Agency, User

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Skema Request untuk Batch B2B
class BatchDispatchRequest(BaseModel):
    agency_api_key: str
    prompts: List[str]

@router.get("/agency", response_class=HTMLResponse)
async def agency_dashboard(request: Request):
    """
    Menampilkan dasbor manajemen Agensi (Portal Eksekutif B2B).
    Menyoroti gaya UX/UI Premium Glassmorphism.
    """
    return templates.TemplateResponse("agency.html", {"request": request})

@router.post("/api/v1/agency/batch")
async def agency_batch_dispatch(payload: BatchDispatchRequest, request: Request):
    """
    Endpoint khusus Agensi untuk melibas 50+ user profile assessment sekaligus.
    Akan memecah dan mendistribusikan array prompt ke Mesh Network Orhcestrator.
    """
    # 1. Validasi Keaslian API Key Agensi (RBAC & Auth)
    async with SessionLocal() as db:
        stmt = select(Agency).where(Agency.api_key == payload.agency_api_key)
        result = await db.execute(stmt)
        agency = result.scalar_one_or_none()
        
        if not agency:
            raise HTTPException(status_code=403, detail="Invalid Agency API Key")
            
    manager = request.app.state.manager
    dispatched_tasks = []
    
    # 2. Loop dan sebarkan ke Worker Nodes yang tersedia
    for prompt in payload.prompts:
        # Tentukan kompleksitas heuristik sederhana
        complexity = "HARD" if len(prompt) > 200 else "EASY"
        worker = manager.get_best_idle_worker(complexity=complexity)
        
        if not worker:
            # Jika mesh network sedang full load, kita kembalikan status backlog
            logger.warning("Network Full: Tidak ada node kosong untuk sisa payload BATCH.")
            break
            
        from core.vault import vault
        task_id = vault.create_session()
        worker.is_busy = True
        worker.current_complexity = complexity
        worker.task_started_at = __import__('time').time()
        
        # Pipa The Vault Masking
        masked_prompt = vault.mask_text(task_id, prompt)
        
        # Opsi: gunakan background task agar tidak block HTTP response
        import asyncio
        import json
        asyncio.create_task(worker.websocket.send_text(json.dumps({
            "type": "task",
            "task_id": task_id,
            "prompt": masked_prompt,
            "complexity": complexity
        })))
        
        dispatched_tasks.append({"task_id": task_id, "worker_id": worker.worker_id})

    # Mengembalikan daftar task yang berhasil diserap oleh mesh
    return {
        "status": "success",
        "agency": agency.name,
        "dispatched_count": len(dispatched_tasks),
        "backlog_count": len(payload.prompts) - len(dispatched_tasks),
        "tasks": dispatched_tasks
    }

@router.get("/api/v1/agency/discount-status")
async def agency_discount_status(agency_api_key: str):
    """
    Fase 5B: Mengkalkulasi diskon potongan harga perpanjangan Lisensi Tahunan TheWeech
    berdasarkan total kontribusi Enterprise Node milik Agensi.
    Rasio: 1.000 Kredit Komputasi = Diskon Lisensi Rp150.000
    """
    from sqlalchemy.sql import func
    from core.models import LedgerLog
    
    async with SessionLocal() as db:
        # Validasi Agensi
        stmt_agency = select(Agency).where(Agency.api_key == agency_api_key)
        agency_res = await db.execute(stmt_agency)
        agency = agency_res.scalar_one_or_none()
        if not agency:
            raise HTTPException(status_code=403, detail="Invalid Agency Key")

        # Hitung poin dari node enterprise
        b2b_identifier = f"B2B:{agency_api_key}"
        stmt = select(func.sum(LedgerLog.credits_earned)).where(LedgerLog.worker_id == b2b_identifier)
        result = await db.execute(stmt)
        total_enterprise_credits = result.scalar() or 0
        
        # Konversi: Pure Integer Logic to avoid floating-point loss
        discount_units = total_enterprise_credits // 1000
        discount_rupiah = discount_units * 150000
        
        return {
            "agency_name": agency.name,
            "license_tier": agency.license_tier,
            "total_enterprise_credits": total_enterprise_credits,
            "discount_earned_idr": discount_rupiah,
            "progress_to_next_discount": total_enterprise_credits % 1000
        }

@router.get("/api/v1/agency/matchmaking")
async def agency_matchmaking(agency_api_key: str):
    """
    Fase 5B: Ekosistem B2B (Logika Matchmaking Kreator TheWeech)
    Agensi bisa memantau "Talent" / Worker berkinerja tertinggi di jaringan
    untuk direkrut ke dalam agensinya (Skema Success Fee TheWeech).
    """
    from sqlalchemy.sql import func
    from core.models import LedgerLog
    
    async with SessionLocal() as db:
        # Pengecekan API sah
        stmt_agency = select(Agency).where(Agency.api_key == agency_api_key)
        if not (await db.execute(stmt_agency)).scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Akses ditolak")

        # Cari Top 5 Kreator Reguler (Filter keluar B2B Nodes)
        stmt = (
            select(LedgerLog.worker_id, func.sum(LedgerLog.credits_earned).label("total_score"))
            .where(~LedgerLog.worker_id.like("B2B:%"))
            .group_by(LedgerLog.worker_id)
            .order_by(func.sum(LedgerLog.credits_earned).desc())
            .limit(5)
        )
        
        result = await db.execute(stmt)
        top_talents = [{"worker_id": row[0], "computing_score": row[1]} for row in result.all()]
        
        return {
            "title": "🔥 Top Creator Matchmaking Radar",
            "top_talents": top_talents
        }
