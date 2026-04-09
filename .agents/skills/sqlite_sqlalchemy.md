---
name: sqlite_sqlalchemy
description: >
  Pattern SQLAlchemy 2.x async dengan SQLite untuk database Orchestrator
  TheWeech. Berisi cara membuat model, migration manual, dan query pattern
  yang dipakai di project ini.
---

# SQLite + SQLAlchemy Async Skill

## Cara Membuat Model Baru

Semua model disimpan di `orchestrator/models/`. Setiap model = satu file.

```python
# orchestrator/models/task.py
"""
Model Task — merepresentasikan satu unit pekerjaan AI inference.
"""

from datetime import datetime
from sqlalchemy import String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prompt: Mapped[str] = mapped_column(String(8000))
    worker_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    output: Mapped[str | None] = mapped_column(String(16000), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
```

### Daftarkan model di `orchestrator/models/__init__.py` agar auto-created:

```python
# orchestrator/models/__init__.py
from .task import Task  # noqa: F401 — import agar Base.metadata tahu model ini
```

---

## Cara CRUD dengan Session

```python
# Contoh di dalam route FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.task import Task
import uuid


async def create_task(db: AsyncSession, prompt: str) -> Task:
    task = Task(id=str(uuid.uuid4()), prompt=prompt, status="pending")
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: str) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def update_task_result(
    db: AsyncSession,
    task_id: str,
    output: str,
    duration: float,
) -> None:
    from datetime import datetime
    from sqlalchemy import update

    await db.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(
            status="completed",
            output=output,
            duration_seconds=duration,
            completed_at=datetime.utcnow(),
        )
    )
    await db.commit()
```

---

## Cara Inject Session ke Route

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db


@router.post("/api/v1/tasks")
async def dispatch(db: AsyncSession = Depends(get_db)):
    task = await create_task(db, prompt="...")
    return {"task_id": task.id}
```

---

## Migrasi Skema (Manual, tanpa Alembic)

Di Fase 1 kita tidak pakai Alembic. Cara update skema:

1. Modifikasi model di `models/xxx.py`
2. Hapus file `theweech.db` (hanya di development!)
3. Restart Orchestrator — `init_db()` akan buat ulang semua tabel

**Di Fase 2+ saat data sudah ada di production**, kita wajib pakai Alembic.
Tambahkan di `requirements.txt`: `alembic==1.13.x`

---

## Upgrade ke PostgreSQL (Fase 2+)

Cukup ubah satu baris di `.env`:

```env
# Dari:
DATABASE_URL=sqlite+aiosqlite:///./theweech.db

# Menjadi:
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/theweech
```

Dan tambahkan di `requirements.txt`:
```
asyncpg==0.29.0
```

Tidak ada perubahan kode lain karena SQLAlchemy menangani abstraksi DB.
