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

class Agency(Base):
    """
    Fase 5 Task A: Multi-Tenant B2B Architecture
    Menyimpan data Entitas Agensi/MCN tingkat atas.
    """
    __tablename__ = "agencies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    api_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    
    # Skema Diskon / Status Langganan B2B
    license_tier: Mapped[str] = mapped_column(String(20), default="BASIC") 
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    """
    Fase 5 Task A: RBAC (Role-Based Access Control)
    Pengguna (Kreator) yang bisa berada di bawah bendera Agency.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(20), default="CREATOR") # CREATOR, AGENCY_ADMIN
    
    # Kunci Relasi ke tabel Agensi jika user ini adalah anak asuh MCN
    agency_id: Mapped[int] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
