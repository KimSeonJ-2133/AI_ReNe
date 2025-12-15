import os
import json
from typing import Optional, List, Dict

class P2PBufferManager:
    def __init__(self, base_dir: str = "data/p2p_sessions"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)

    def _get_session_dir(self, session_id: str) -> str:
        session_dir = os.path.join(self.base_dir, session_id)
        if not os.path.exists(session_dir):
            os.makedirs(session_dir, exist_ok=True)
        return session_dir

    def _get_buffer_path(self, session_id: str) -> str:
        return os.path.join(self._get_session_dir(session_id), "buffer.pcm")

    def _get_meta_path(self, session_id: str) -> str:
        return os.path.join(self._get_session_dir(session_id), "meta.json")

    def _get_transcript_path(self, session_id: str) -> str:
        return os.path.join(self._get_session_dir(session_id), "transcript.json")

    def get_last_speaker(self, session_id: str) -> Optional[str]:
        meta_path = self._get_meta_path(session_id)
        if not os.path.exists(meta_path):
            return None
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("last_speaker")
        except Exception:
            return None

    def update_last_speaker(self, session_id: str, speaker: str):
        meta_path = self._get_meta_path(session_id)
        data = {}
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        
        data["last_speaker"] = speaker
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def append_audio(self, session_id: str, audio_bytes: bytes):
        buffer_path = self._get_buffer_path(session_id)
        with open(buffer_path, "ab") as f:
            f.write(audio_bytes)

    def read_and_clear_buffer(self, session_id: str) -> Optional[bytes]:
        buffer_path = self._get_buffer_path(session_id)
        if not os.path.exists(buffer_path):
            return None
        
        with open(buffer_path, "rb") as f:
            data = f.read()
        
        # 파일 삭제 (Clear)
        os.remove(buffer_path)
        return data

    def save_transcript(self, session_id: str, speaker: str, text: str):
        transcript_path = self._get_transcript_path(session_id)
        logs = []
        if os.path.exists(transcript_path):
            try:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                pass
        
        logs.append({"speaker": speaker, "text": text})
        
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def get_full_transcript(self, session_id: str) -> str:
        transcript_path = self._get_transcript_path(session_id)
        if not os.path.exists(transcript_path):
            return ""
        
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
                return "\n".join([f"{log['speaker']}: {log['text']}" for log in logs])
        except Exception:
            return ""

    def clear_session(self, session_id: str):
        import shutil
        session_dir = self._get_session_dir(session_id)
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)

    def set_session_user(self, session_id: str, username: str):
        """세션에 매핑된 사용자 ID 저장"""
        meta_path = self._get_meta_path(session_id)
        data = {}
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        
        # 이미 설정되어 있고 변경되지 않았다면 저장 생략 (I/O 최적화)
        if data.get("username") == username:
            return

        data["username"] = username
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def get_session_user(self, session_id: str) -> Optional[str]:
        """세션에 매핑된 사용자 ID 조회"""
        meta_path = self._get_meta_path(session_id)
        if not os.path.exists(meta_path):
            return None
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("username")
        except Exception:
            return None

buffer_manager = P2PBufferManager()
