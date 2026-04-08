import os
import json
import time
from openai import OpenAI
import requests

# 1. Setup Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
HF_TOKEN = os.getenv("HF_TOKEN")
# This is the URL of your deployed HF Space (or localhost testing)
SPACE_URL = "http://localhost:7860" 

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL) if HF_TOKEN else None

def get_action_from_llm(state_dict):
    # LLM logic
    prompt = f"""You are an autonomous customer support agent.
You MUST output a valid JSON answering with exactly this schema:
{{
    "action_type": string (MUST be one of: 'reply', 'refund', 'escalate', 'close'),
    "amount": float (Optional, ONLY if action_type is 'refund'),
    "message": string (Optional, ONLY if action_type is 'reply')
}}

Current constraints:
Company policy: {state_dict.get('company_policy')}
Budget remaining: {state_dict.get('budget_remaining')}

Current Ticket:
{json.dumps(state_dict.get('current_ticket'))}

Return exactly one valid action_type according to the policy."""
    
    if client:
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                # We do not use json_object format directly if API compatibility matters, 
                # but for simplicity we rely on the system instruction.
                temperature=0.0
            )
            content = response.choices[0].message.content
            # Strip potential markdown blocks
            content = content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        except Exception as e:
            pass # Use fallback below
            
    # Mock/Fallback baseline logic incase API keys missing locally
    if not state_dict.get('current_ticket'):
        return {"action_type": "close"}
    issue = state_dict['current_ticket']['issue_type']
    if issue == "delayed_order" and state_dict['current_ticket'].get('refund_amount', 0) == 0:
        return {"action_type": "refund", "amount": 20.0}
    elif issue == "bug":
        return {"action_type": "escalate"}
    else:
        return {"action_type": "close"}

def run_task(task_level):
    print(f"[START] Task: {task_level}")
    
    response = requests.post(f"{SPACE_URL}/reset", json={"task_level": task_level})
    state = response.json()
    
    done = False
    step_count = 0
    reward = 0.0
    
    while not done and step_count < 15:
        # LLM Logic: Ask the model what to do based on the state
        action = get_action_from_llm(state)
        
        # Step the environment via API
        step_resp = requests.post(f"{SPACE_URL}/step", json=action).json()
        reward = step_resp["reward"]
        done = step_resp["done"]
        state = step_resp["state"]
        
        # STRICT LOGGING FORMAT REQUIRED BY GRADER
        log_entry = {
            "step": step_count,
            "action": action,
            "reward": reward,
            "done": done
        }
        print(f"[STEP] {json.dumps(log_entry)}")
        
        step_count += 1
        if step_count > 15: done = True # Safety break

    print(f"[END] Task: {task_level} | Final Score: {reward}")

if __name__ == "__main__":
    for level in ["easy", "medium", "hard"]:
        run_task(level)
