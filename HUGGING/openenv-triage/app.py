from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.environment import CustomerSupportEnv
from src.models import Action

app = FastAPI()
env = CustomerSupportEnv()

class ResetRequest(BaseModel):
    task_level: str = "easy"

@app.get("/")
@app.get("/health")
def health():
    return {"status": "ready"}

@app.post("/reset")
def reset_env(req: Optional[ResetRequest] = None):
    try:
        level = req.task_level if req and req.task_level else "easy"
        state = env.reset(level)
        return state.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def get_state():
    return env.state().model_dump()

@app.post("/step")
def step_env(action: Action):
    try:
        state, reward, done, info = env.step(action)
        return {
            "state": state.model_dump(),
            "reward": reward,
            "done": done,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
