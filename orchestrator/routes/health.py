"""
Health check endpoint — cek status Orchestrator & jumlah Worker aktif.
"""

from fastapi import APIRouter, Request

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(request: Request):
    manager = request.app.state.manager
    return {
        "status": "ok",
        "service": "TheWeech Orchestrator",
        "version": "0.1.0",
        "active_workers": manager.active_count,
        "workers": [
            {
                "id": w.worker_id,
                "busy": w.is_busy,
                "tasks_completed": w.tasks_completed,
                "specs": w.specs,
            }
            for w in manager.get_all_workers()
        ],
    }
