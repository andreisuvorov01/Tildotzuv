import json
import os
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, storage_path: str = "app/sessions.json"):
        self.storage_path = storage_path
        self.sessions = {}
        self.lock = asyncio.Lock()
        self.load_sessions()
    
    def load_sessions(self):
        """Load sessions from persistent storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
                logger.info(f"Loaded {len(self.sessions)} sessions from storage")
            else:
                logger.info("No existing sessions file found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            self.sessions = {}
    
    def save_sessions(self):
        """Save sessions to persistent storage"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2, default=str)
            logger.info(f"Saved {len(self.sessions)} sessions to storage")
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
    
    def create_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Create a new session"""
        try:
            self.sessions[session_id] = {
                "data": data,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            self.save_sessions()
            return True
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session has expired
        try:
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.now() > expires_at:
                self.delete_session(session_id)
                return None
        except Exception as e:
            logger.warning(f"Failed to check session expiration: {e}")
        
        # Update last accessed time
        session["last_accessed"] = datetime.now().isoformat()
        self.save_sessions()
        
        return session["data"]
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update existing session data"""
        if session_id not in self.sessions:
            return False
        
        try:
            self.sessions[session_id]["data"].update(data)
            self.sessions[session_id]["last_accessed"] = datetime.now().isoformat()
            self.save_sessions()
            return True
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.save_sessions()
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            try:
                expires_at = datetime.fromisoformat(session["expires_at"])
                if current_time > expires_at:
                    expired_sessions.append(session_id)
            except Exception as e:
                logger.warning(f"Failed to parse expiration time for session {session_id}: {e}")
                expired_sessions.append(session_id)  # Remove invalid sessions
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self.save_sessions()
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        total_sessions = len(self.sessions)
        active_sessions = 0
        expired_sessions = 0
        
        current_time = datetime.now()
        
        for session in self.sessions.values():
            try:
                expires_at = datetime.fromisoformat(session["expires_at"])
                if current_time <= expires_at:
                    active_sessions += 1
                else:
                    expired_sessions += 1
            except Exception:
                expired_sessions += 1
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions
        }

# Global session manager instance
session_manager = SessionManager()