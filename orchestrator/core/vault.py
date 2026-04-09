"""
The Vault - Phase 2 Privacy Infrastructure.
Namespace per-SessionID to prevent state leak.
Masking uses SpaCy (id_core_news_sm) untuk Ekstraksi Entitas Named Entity Recognition (NER).
"""
import uuid
import time
import asyncio
import logging
from typing import Dict

logger = logging.getLogger(__name__)

try:
    import spacy
    logger.info("Initializing SpaCy with id_core_news_sm...")
    nlp = spacy.load("id_core_news_sm")
    logger.info("✅ NER Engine loaded.")
except ImportError:
    logger.warning("⚠️ Spacy not installed. Vault will run in bypass mode.")
    nlp = None
except Exception as e:
    logger.warning(f"⚠️ Spacy id_core_news_sm not found ({e}). Vault will run in bypass mode.")
    nlp = None

class VaultSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = time.time()
        self.entity_map: Dict[str, str] = {}  # cth: { "Thoriq": "[KREATOR_1]" }
        self.token_map: Dict[str, str] = {}   # cth: { "[KREATOR_1]": "Thoriq" }

class TheVault:
    def __init__(self, ttl_seconds: int = 300):
        # Struktur Map<SessionID, ...> untuk isolasi sesi yang ketat (Zero-State Leak)
        self._sessions: Dict[str, VaultSession] = {}
        self.ttl_seconds = ttl_seconds
        self.entity_counter = 0

    def create_session(self) -> str:
        """Buat namespace sesi baru untuk request dari web."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = VaultSession(session_id)
        return session_id
        
    def mask_text(self, session_id: str, text: str) -> str:
        """Masking data sensitif sebelum dikirim ke Worker publik."""
        if session_id not in self._sessions:
            raise ValueError(f"Sesi {session_id} tidak valid atau sudah expired.")
            
        session = self._sessions[session_id]
        masked_text = text
        
        if nlp:
            # Tokenisasi dan Identifikasi Entitas NLP
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ("PERSON", "ORG", "GPE", "LOC"):
                    original_text = ent.text
                    # Hindari duplikasi token untuk entitas yang sama
                    if original_text not in session.entity_map:
                        self.entity_counter += 1
                        token = f"[{ent.label_}_{self.entity_counter}]"
                        session.entity_map[original_text] = token
                        session.token_map[token] = original_text
                        
            # String replacement sesuai map yang terbangun
            # Mengurutkan by length desc untuk menghindari partial replace overlapping
            sorted_entities = sorted(session.entity_map.keys(), key=len, reverse=True)
            for orig in sorted_entities:
                token = session.entity_map[orig]
                masked_text = masked_text.replace(orig, token)
        
        logger.debug(f"🔒 Vault Masking {session_id}: {len(session.entity_map)} entities hidden.")
        return masked_text

    def unmask_text(self, session_id: str, text: str) -> str:
        """De-masking data anonim kembali ke bentuk aslinya saat diterima dari Worker."""
        if session_id not in self._sessions:
            logger.warning(f"⚠️ Vault session {session_id} not found or expired during De-masking.")
            return text
            
        session = self._sessions[session_id]
        unmasked = text
        
        # Sort tokens if necessary, but standard UUIDs or rigid tags don't overlap easily
        for token, orig in session.token_map.items():
            unmasked = unmasked.replace(token, orig)
            
        return unmasked

    def cleanup_session(self, session_id: str):
        """Hapus namespace segera setelah transaksi selesai."""
        if self._sessions.pop(session_id, None):
            logger.debug(f"🧹 Vault Cleaned: {session_id}")

    async def auto_cleanup_loop(self):
        """Background task di main (opsional) untuk menghapus sesi yang hang lebih dari 5 menit."""
        while True:
            await asyncio.sleep(60)
            now = time.time()
            expired = [sid for sid, s in self._sessions.items() if now - s.created_at > self.ttl_seconds]
            for sid in expired:
                self.cleanup_session(sid)
                if expired:
                    logger.info(f"🧹 Vault Auto-cleanup cleared {len(expired)} hanging sessions.")

# Singleton instance exported
vault = TheVault()
