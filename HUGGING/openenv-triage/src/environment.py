import json
from typing import Tuple
from .models import Ticket, AgentState, Action
from .graders import grade_easy, grade_medium, grade_hard

class CustomerSupportEnv:
    def __init__(self):
        self.tickets = []
        self.budget = 0.0
        self.policy = ""
        self.current_index = 0
        self.task_level = "easy"
        self.completed_tickets = []
        
    def reset(self, task_level: str = "easy") -> AgentState:
        self.task_level = task_level
        self.completed_tickets = []
        self.current_index = 0
        
        if task_level == "easy":
            self.policy = "Always close tickets that simply ask questions or say thanks."
            self.budget = 0.0
            self.tickets = [
                Ticket(id="E1", customer_id="C1", issue_type="question", messages=["Thanks for the help! resolving now."]),
                Ticket(id="E2", customer_id="C2", issue_type="question", messages=["The item arrived yesterday, looks good."])
            ]
        elif task_level == "medium":
            self.policy = "If issue is delayed_order, issue exactly $20 refund and close. Otherwise close with $0."
            self.budget = 100.0
            self.tickets = [
                Ticket(id="M1", customer_id="C3", issue_type="delayed_order", messages=["My order is 2 weeks late! I demand compensation."]),
                Ticket(id="M2", customer_id="C4", issue_type="question", messages=["How do I clean this product?"])
            ]
        elif task_level == "hard":
            self.policy = "Delayed_order: $20 refund. Bug: escalate. Abuse: 0 refund and close."
            self.budget = 100.0
            self.tickets = [
                Ticket(id="H1", customer_id="C5", issue_type="bug", messages=["The app crashes when I click checkout."]),
                Ticket(id="H2", customer_id="C6", issue_type="abuse", messages=["Give me a refund or else! I do this to every store."]),
                Ticket(id="H3", customer_id="C7", issue_type="delayed_order", messages=["Where is my package? Tracking says it's lost."])
            ]
            
        return self.state()

    def state(self) -> AgentState:
        current_ticket = self.tickets[self.current_index] if self.current_index < len(self.tickets) else None
        return AgentState(
            current_ticket=current_ticket,
            queue_size=len(self.tickets) - self.current_index,
            company_policy=self.policy,
            budget_remaining=self.budget,
            history=[t.id for t in self.completed_tickets]
        )
        
    def step(self, action: Action) -> Tuple[AgentState, float, bool, dict]:
        if self.current_index >= len(self.tickets):
            return self.state(), 0.0, True, {"msg": "No more tickets."}
            
        ticket = self.tickets[self.current_index]
        reward = 0.0
        done = False
        info = {}
        
        if action.action_type == 'reply':
            ticket.messages.append(f"Agent: {action.message}")
            info['msg'] = 'Replied to customer.'
        elif action.action_type == 'refund':
            amount = action.amount or 0.0
            if amount <= self.budget:
                self.budget -= amount
                ticket.refund_amount += amount
                info['msg'] = f'Refunded ${amount}.'
                # Note: after a refund, the ticket isn't auto-closed, but for the sake of standard flow,
                # the agent should invoke close() subsequently or we can auto-close.
                # In this env, agent must follow up with 'close' action.
            else:
                info['msg'] = 'Refund failed: Insufficient budget.'
        elif action.action_type == 'escalate':
            ticket.status = 'escalated'
            self.completed_tickets.append(ticket)
            self.current_index += 1
            info['msg'] = 'Ticket escalated and removed from queue.'
        elif action.action_type == 'close':
            ticket.status = 'closed'
            self.completed_tickets.append(ticket)
            self.current_index += 1
            info['msg'] = 'Ticket closed.'
            
        # Check termination
        if self.current_index >= len(self.tickets):
            done = True
            # Compute total reward using graders based on final state of completed tickets
            if self.task_level == "easy":
                reward = grade_easy(self.completed_tickets, 0.0)
            elif self.task_level == "medium":
                reward = grade_medium(self.completed_tickets, 100.0 - self.budget)
            elif self.task_level == "hard":
                reward = grade_hard(self.completed_tickets, 100.0 - self.budget)
                
        return self.state(), reward, done, info
