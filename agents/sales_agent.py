# agents/sales_agent.py
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_community.tools.base import Tool as LangChainTool
from tools.mcp_registry import mcp_registry

llm = Ollama(model="llama3")

sales_prompt_template = """
You are a sales and customer relations specialist. Your task is to help users with everything related to customers, leads, orders, and tickets.
You have access to the following tools:
{tools}

If the user wants to create, update, or delete data, you must use the sales_sql_write tool.
If the user wants to retrieve data, you must use the sales_sql_read tool.
After completing the task, provide a friendly and clear answer.

Conversation timeline:
{history}
Human: {input}
Agent:

class SalesAgent:
    def __init__(self):
        self.read_tool = mcp_registry.get_tool("sales_sql_read")
        self.write_tool = mcp_registry.get_tool("sales_sql_write")
        
        self.langchain_tools = [
            LangChainTool(name=self.read_tool.name, func=self.read_tool.run, description=self.read_tool.description),
            LangChainTool(name=self.write_tool.name, func=self.write_tool.run, description=self.write_tool.description)
        ]
        
        self.prompt = PromptTemplate.from_template(sales_prompt_template)
        self.agent = create_react_agent(llm, self.langchain_tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.langchain_tools, verbose=True)

    def run(self, user_prompt: str, memory_context: dict) -> str:
        return self.executor.invoke({"input": user_prompt, "history": memory_context.get("history", "")})['output']
