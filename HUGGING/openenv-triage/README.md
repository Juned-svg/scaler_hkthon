---
title: OpenEnv Customer Support Triage
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---
# OpenEnv: Customer Support Triage

This repository provides a standard **OpenEnv** framework environment designed to simulate a real-world task: **Customer Support Ticket Triage**, designed for Reinforcement Learning and autonomous Agent testing.

## Scenario Mechanics
The agent receives an influx of incoming customer support tickets. 
The agent has:
- A constrained $ budget.
- Explicit company policies defining rules on who gets refunds.
- The ability to perform explicit actions against the ticketing queue:
  - `reply`: Ask for more information or attempt to deescalate.
  - `refund`: Give money back.
  - `escalate`: Send complex issues or software bugs to the Dev/Managers.
  - `close`: Archive a completed, processed or invalid request.

## Action & Observation Spaces
The Environment is formulated using explicit strict-typing with Pydantic:

### 1) Action Space
```python
class Action(BaseModel):
    action_type: Literal['reply', 'refund', 'escalate', 'close']
    amount: Optional[float] = None
    message: Optional[str] = None
```

### 2) Observation Space (AgentState)
```python
class AgentState(BaseModel):
    current_ticket: Optional[Ticket] 
    queue_size: int
    company_policy: str
    budget_remaining: float
    history: List[str]
```

## Evaluated Tasks
There are multiple gradient levels of difficulty graded on a strict `0.0` - `1.0` metric system:
1. **Easy**: Pre-resolved cases. Agent just has to close them properly.
2. **Medium**: Partial issues that require refunds adhering perfectly to company policy limits.
3. **Hard**: Complex mix of aggressive abusers, escalated technical bugs, and standard delays requiring intelligent queuing and multi-strategy responses while balancing a budget.

## Usage
Deployable right onto Hugging Face Spaces using the included Dockerfile.

```bash
git clone remote_path openenv-triage
cd openenv-triage
pip install -r requirements.txt

# Validate grading and execution via baseline
python inference.py
```
