import random
import logging

logger = logging.getLogger(__name__)

class CheatGuard:
    """
    Fase 3 Task D: Anti-Spoofing & Kriptografi Ringan (Cheat Guard).
    Sistem pencegahan kecurangan Worker yang sekadar membalas teks palsu
    tanpa melakukan inferensi LLM sungguhan demi farming poin secara ilegal.
    """
    def __init__(self):
        # Struktur: task_id_jebakan -> (worker_id, expected_answer)
        self.active_traps = {}

    def generate_trap(self) -> tuple[str, str]:
        """Menghasilkan dummy prompt (Trap) dan jawaban ekspektasinya."""
        traps = [
            ("Ulangi kata 'Apel' tepat tiga kali, pisahkan dengan spasi. Jangan tulis kata lain.", "apel apel apel"),
            ("Berapa hasil penjumlahan 2 ditambah 3? Tuliskan satu angka saja.", "5"),
            ("Apa ibukota dari Indonesia? Tulis satu kata saja tanpa titik.", "jakarta")
        ]
        return random.choice(traps)

    def register_trap(self, task_id: str, worker_id: str, expected_answer: str):
        """Mencatat kail pancingan untuk divalidasi nanti."""
        self.active_traps[task_id] = {
            "worker_id": worker_id,
            "expected": expected_answer.lower()
        }

    def is_trap(self, task_id: str) -> bool:
        """Memeriksa apakah sebuah task_id adalah task jebakan."""
        return task_id in self.active_traps

    def verify_trap(self, task_id: str, actual_response: str) -> bool:
        """
        Validasi respons Worker terhadap jebakan.
        Jika lolos, dapat bonus trust factor. Jika gagal, indikasi spoofing!
        """
        trap_data = self.active_traps.pop(task_id, None)
        if not trap_data:
            return False
            
        expected = trap_data["expected"]
        response_clean = actual_response.strip().lower()
        
        # Validasi natural: ekspektasi kata harus muncul persis dalam respons worker
        # Untuk mengantisipasi LLM yang suka membubuhi "Berikut adalah..."
        if expected in response_clean:
            logger.info(f"🛡️ CHEAT GUARD: Worker {trap_data['worker_id']} LULUS uji inferensi asli.")
            return True
        else:
            logger.warning(f"🚨 CHEAT GUARD ALERT: Worker {trap_data['worker_id']} terindikasi SPOOFING! "
                           f"Expected '{expected}', tapi membalas '{response_clean}'")
            return False

cheat_guard = CheatGuard()
