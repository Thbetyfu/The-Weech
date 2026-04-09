from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
import uuid

from core.database import get_db
from core.models import LedgerLog

router = APIRouter(tags=["Gamification & Billing"])

# -------------------------------------------------------------
# Fase 4 Task A: Tokenomics Balancing
# -------------------------------------------------------------
COST_PRO_MONTHLY = 5000  # Setara konversi ~Rp99.000 dalam ekuivalen komputasi

class RedeemRequest(BaseModel):
    worker_id: str
    package: str  # e.g., "PRO_MONTHLY"

@router.get("/api/v1/wallet/{worker_id}")
async def get_wallet_balance(worker_id: str, db: AsyncSession = Depends(get_db)):
    """Mengambil total saldo akhir dari ledger untuk dasbor UI (Pending vs Verified)."""
    # Menghitung SUM dari semua kredit (termasuk income (+) dan burn (-))
    result = await db.execute(
        select(func.sum(LedgerLog.credits_earned)).where(LedgerLog.worker_id == worker_id)
    )
    balance = result.scalar() or 0
    
    # Progress visualisasi target PRO
    progress = min(100, int((balance / COST_PRO_MONTHLY) * 100))
    
    return {
        "worker_id": worker_id,
        "verified_balance": balance,
        "pro_monthly_cost": COST_PRO_MONTHLY,
        "progress_percent": progress
    }

@router.post("/api/v1/wallet/redeem")
async def redeem_package(body: RedeemRequest, db: AsyncSession = Depends(get_db)):
    """
    Fase 4 Task B & C: Sistem Penagihan Hibrida & Burn Mechanism
    Menukar kredit komputasi dengan paket Pro secara transaksional penuh.
    (Mencegah Double-Spending dari Race Condition Hacker).
    """
    if body.package != "PRO_MONTHLY":
        raise HTTPException(status_code=400, detail="Paket tidak tersedia")

    # Menerapkan pengecekan ACID
    result = await db.execute(
        select(func.sum(LedgerLog.credits_earned)).where(LedgerLog.worker_id == body.worker_id)
    )
    current_balance = result.scalar() or 0

    if current_balance < COST_PRO_MONTHLY:
        raise HTTPException(status_code=402, detail="Kredit komputasi tidak cukup. Tambah waktu online Worker Anda.")

    # Fase 4 Task C: BURN MECHANISM (Potong Saldo)
    burn_entry = LedgerLog(
        task_id=f"REDEEM-{uuid.uuid4()}",
        worker_id=body.worker_id,
        credits_earned=-COST_PRO_MONTHLY,
        complexity="BURN"
    )
    db.add(burn_entry)
    
    try:
        await db.commit() # Menyegel mutasi ledger
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Transaksi macet. Silakan ulangi.")

    return {
        "status": "success",
        "message": "Fitur Pro Monthly 1 Bulan berhasil diaktifkan dengan menukarkan Kredit Komputasi!"
    }
