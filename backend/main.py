# backend/main.py

from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.memory import ConversationBufferWindowMemory
from starlette.middleware.cors import CORSMiddleware

from backend.agents.router_agent import RouterAgent
from backend.agents.sales_agent import SalesAgent
from backend.agents.analytics_agent import AnalyticsAgent
from backend.agents.finance_agent import FinanceAgent
from backend.agents.inventory_agent import InventoryAgent

# Import all tools to register them
import tools.classifier
import tools.sales_sql
import tools.analytics_sql
import tools.finance_sql
import tools.inventory_sql


# from agents import RouterAgent, SalesAgent, AnalyticsAgent, FinanceAgent, InventoryAgent

# Initialize FastAPI application
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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
