import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from core.database import Base

class LedgerLog(Base):
    """
    Fase 3 Task B:
    Buku besar (Ledger) pencatatan riwayat komputasi untuk Compute-to-Earn.
    Hanya menggunakan tipe data Integer untuk saldo komputasi.
    """
    __tablename__ = "ledger_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(36), index=True)
    worker_id: Mapped[str] = mapped_column(String(50), index=True)
    
    # Nilai ekonomis murni Integer
    credits_earned: Mapped[int] = mapped_column(Integer, default=0)
    complexity: Mapped[str] = mapped_column(String(10), default="EASY")
    
    completed_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
