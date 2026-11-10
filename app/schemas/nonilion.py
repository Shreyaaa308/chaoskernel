from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class NonilionIncomingMessage(BaseModel):
    room_id: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = "Engineer"
    text: str
    attachments: Optional[List[Dict[str, Any]]] = []

class NonilionAttachment(BaseModel):
    type: str  # 'image' or 'file'
    filename: str
    data_base64: Optional[str] = None
    url: Optional[str] = None

class NonilionOutgoingReply(BaseModel):
    reply: str
    attachments: Optional[List[NonilionAttachment]] = []
