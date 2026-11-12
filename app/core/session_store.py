from typing import Dict, Any, Optional

_SESSION_CACHE: Dict[str, Dict[str, Any]] = {}

def save_room_session(room_id: str, data: Dict[str, Any]) -> None:
    if room_id:
        _SESSION_CACHE[room_id] = data

def get_room_session(room_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not room_id:
        return None
    return _SESSION_CACHE.get(room_id)

def has_active_session(room_id: Optional[str]) -> bool:
    return bool(room_id and room_id in _SESSION_CACHE)
