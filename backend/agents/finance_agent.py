# agents/finance_agent.py
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool as LangChainTool
from .tools import mcp_registry, llm

finance_prompt_template = """
You are a specialized financial agent. Your task is to automate financial operations such as invoice processing, ledger updates, and payment tracking.

You have access to the following tools:
{tools}

Tool names you can call: {tool_names}

If the user wants to create, update, or delete financial data (such as invoices, payments), you must use the finance_sql_write tool.
If the user wants to retrieve data, you must use the finance_sql_read tool.

Conversation timeline:
{history}

Human: {input}
AI (scratchpad): {agent_scratchpad}
"""

class FinanceAgent:
    def __init__(self):
        self.read_tool = mcp_registry.get_tool("finance_sql_read")
        self.write_tool = mcp_registry.get_tool("finance_sql_write")

        self.langchain_tools = [
            LangChainTool(name=self.read_tool.name, func=self.read_tool.run, description=self.read_tool.description),
            LangChainTool(name=self.write_tool.name, func=self.write_tool.run, description=self.write_tool.description)
        ]

        self.prompt = PromptTemplate.from_template(finance_prompt_template)
        self.agent = create_react_agent(llm, self.langchain_tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.langchain_tools, verbose=True, handle_parsing_errors=True)

    def run(self, user_prompt: str, memory_context: dict) -> str:
        return self.executor.invoke({"input": user_prompt, "history": memory_context.get("history", "")})['output']
