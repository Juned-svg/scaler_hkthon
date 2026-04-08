from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Ticket(BaseModel):
    id: str
    customer_id: str
    issue_type: str
    messages: List[str]
    status: Literal['open', 'closed', 'escalated'] = 'open'
    refund_amount: float = 0.0

class AgentState(BaseModel):
    current_ticket: Optional[Ticket] = None
    queue_size: int = 0
    company_policy: str = ""
    budget_remaining: float = 0.0
    history: List[str] = Field(default_factory=list)

class Action(BaseModel):
    action_type: Literal['reply', 'refund', 'escalate', 'close']
    amount: Optional[float] = None
    message: Optional[str] = None
