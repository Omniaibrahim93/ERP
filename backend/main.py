# backend/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from agents.router_agent import RouterAgent
from agents.sales_agent import SalesAgent
from agents.analytics_agent import AnalyticsAgent
from agents.finance_agent import FinanceAgent
from agents.inventory_agent import InventoryAgent  # تم إضافة وكيل المخزون
from langchain.memory import ConversationBufferWindowMemory

# Initialize FastAPI application
app = FastAPI()

# Initialize all agents and a shared memory buffer
router_agent = RouterAgent()
sales_agent = SalesAgent()
analytics_agent = AnalyticsAgent()
finance_agent = FinanceAgent()
inventory_agent = InventoryAgent() # تهيئة وكيل المخزون

# Use a memory buffer to store conversation history
memory = ConversationBufferWindowMemory(memory_key="history", k=5)

# Pydantic model for request body validation
class UserRequest(BaseModel):
    prompt: str

@app.post("/chat/")
def chat_with_erp(request: UserRequest):
    """
    Handles user prompts and routes them to the correct domain agent.
    """
    user_prompt = request.prompt
    
    # Get current conversation history from memory
    history = memory.load_memory_variables({})

    # 1. Route the request using the Router Agent
    routed_agent_name = router_agent.route_request(user_prompt)

    # 2. Select the correct agent and run the task
    response = "Sorry, that agent is not yet implemented."
    
    if "sales_agent" in routed_agent_name.lower():
        response = sales_agent.run(user_prompt, history)
    elif "analytics_agent" in routed_agent_name.lower():
        response = analytics_agent.run(user_prompt, history)
    elif "finance_agent" in routed_agent_name.lower():
        response = finance_agent.run(user_prompt, history)
    elif "inventory_agent" in routed_agent_name.lower(): # إضافة شرط وكيل المخزون
        response = inventory_agent.run(user_prompt, history)
    else:
        response = f"I couldn't find an agent for that task. The request was routed to: '{routed_agent_name}'."

    # 3. Save the interaction to memory
    memory.save_context({"input": user_prompt}, {"output": response})

    return {"response": response, "agent_used": routed_agent_name}

# Simple endpoint for health check
@app.get("/")
def read_root():
    return {"message": "Helios Dynamics ERP Agent System is running!"}
