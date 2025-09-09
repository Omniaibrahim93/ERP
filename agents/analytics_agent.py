# agents/analytics_agent.py
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_community.tools.base import Tool as LangChainTool
from tools.mcp_registry import mcp_registry

llm = Ollama(model="llama3")

analytics_prompt_template = """
You are a specialized agent in analytics and reporting. Your task is to answer questions using data from the ERP system.
You have access to the following tools:
{tools}

To answer any data-related question, you must first use the text_to_sql_tool.
If the user asks for a definition of a term, use the glossary_read tool.
After obtaining the result, provide a clear and explanatory answer of the findings.

Conversation timeline:
{history}
Human: {input}
Agent:
"""

class AnalyticsAgent:
    def __init__(self):
        self.sql_tool = mcp_registry.get_tool("text_to_sql_tool")
        self.glossary_tool = mcp_registry.get_tool("glossary_read")
        
        self.langchain_tools = [
            LangChainTool(name=self.sql_tool.name, func=self.sql_tool.run, description=self.sql_tool.description),
            LangChainTool(name=self.glossary_tool.name, func=self.glossary_tool.run, description=self.glossary_tool.description)
        ]
        
        self.prompt = PromptTemplate.from_template(analytics_prompt_template)
        self.agent = create_react_agent(llm, self.langchain_tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.langchain_tools, verbose=True)

    def run(self, user_prompt: str, memory_context: dict) -> str:
        return self.executor.invoke({"input": user_prompt, "history": memory_context.get("history", "")})['output']
