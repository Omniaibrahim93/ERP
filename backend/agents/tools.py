import os
from typing import Dict, Type
from abc import ABC, abstractmethod
import sqlite3
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM


DB_PATH = 'database/erp.db'

base_url = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

# llm = OllamaLLM(model="llama3")

llm = OllamaLLM(
    model="llama3",
    base_url=base_url
)


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs):
        pass

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool
        print(f"Tool '{tool.name}' registered.")

    def get_tool(self, tool_name: str) -> BaseTool:
        tool = self._tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found.")
        return tool

mcp_registry = ToolRegistry()

class IntentClassifierTool(BaseTool):
    name = "intent_classifier"
    description = "Classifies a user's prompt to determine the correct domain agent (e.g., sales, finance, analytics)."

    def run(self, user_prompt: str) -> str:
        user_prompt_lower = user_prompt.lower()
        if any(k in user_prompt_lower for k in ["customer", "lead", "order", "sale", "crm"]):
            return "sales_agent"
        elif any(k in user_prompt_lower for k in ["report", "analytics", "data", "insights"]):
            return "analytics_agent"
        elif any(k in user_prompt_lower for k in ["invoice", "payment", "finance", "ledger"]):
            return "finance_agent"
        elif any(k in user_prompt_lower for k in ["inventory", "stock", "product", "reorder"]):
            return "inventory_agent"
        else:
            return "general_purpose"

class TextToSQLTool(BaseTool):
    name = "text_to_sql_tool"
    description = "Converts a natural language question into a SQLite SQL query and executes it."

    sql_prompt = PromptTemplate.from_template("""
    Given the database schema below, write a concise, valid SQLite SQL query that answers the user's question.
    Tables: customers, orders, order_items, invoices, payments, glossary, stock.
    Question: {question}
    SQL Query: 
    """)

    def run(self, user_question: str) -> str:
        try:
            chain = self.sql_prompt | llm
            sql_query = chain.invoke({"question": user_question}).strip().replace("```sql", "").replace("```", "")

            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            return df.to_markdown(index=False)
        except Exception as e:
            return f"Error translating or executing SQL: {e}"

class GlossaryReadTool(BaseTool):
    name = "glossary_read"
    description = "Retrieves the definition of a specific business term from the glossary table."

    def run(self, term: str) -> str:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT definition FROM glossary WHERE term = ?", (term,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else f"Term '{term}' not found."
        except sqlite3.Error as e:
            return f"SQL Error: {e}"

class FinanceSQLReadTool(BaseTool):
    name = "finance_sql_read"
    description = "Executes read-only SQL queries on financial tables (invoices, payments, ledger_entries)."

    def run(self, query: str) -> str:
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df.to_markdown(index=False)
        except sqlite3.Error as e:
            return f"SQL Error: {e}"

class FinanceSQLWriteTool(BaseTool):
    name = "finance_sql_write"
    description = "Executes write SQL operations on financial tables (INSERT, UPDATE, DELETE). Requires approval for sensitive actions."

    def run(self, query: str) -> str:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
            return f"SQL write operation successful. Rows affected: {cursor.rowcount}"
        except sqlite3.Error as e:
            return f"SQL Error: {e}"

class InventorySQLReadTool(BaseTool):
    name = "inventory_sql_read"
    description = "Executes read-only SQL queries on inventory tables (products, stock, purchase_orders)."

    def run(self, query: str) -> str:
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df.to_markdown(index=False)
        except sqlite3.Error as e:
            return f"SQL Error: {e}"

class InventorySQLWriteTool(BaseTool):
    name = "inventory_sql_write"
    description = "Executes write SQL operations (INSERT, UPDATE, DELETE) on inventory tables. Requires approval for sensitive actions."

    def run(self, query: str) -> str:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
            return f"SQL write operation successful. Rows affected: {cursor.rowcount}"
        except sqlite3.Error as e:
            return f"SQL Error: {e}"

class SalesSQLReadTool(BaseTool):
    name = "sales_sql_read"
    description = "Executes read-only SQL queries on sales tables (customers, leads, orders, order_items)."

    def run(self, query: str) -> str:
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df.to_markdown(index=False)
        except sqlite3.Error as e:
            return f"SQL Error: {e}"

class SalesSQLWriteTool(BaseTool):
    name = "sales_sql_write"
    description = "Executes write SQL operations (INSERT, UPDATE, DELETE) on sales tables. Requires approval for sensitive actions."

    def run(self, query: str) -> str:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
            return f"SQL write operation successful. Rows affected: {cursor.rowcount}"
        except sqlite3.Error as e:
            return f"SQL Error: {e}"

# Register the new tools

mcp_registry.register(FinanceSQLReadTool())
mcp_registry.register(FinanceSQLWriteTool())
mcp_registry.register(InventorySQLReadTool())
mcp_registry.register(InventorySQLWriteTool())
mcp_registry.register(TextToSQLTool())
mcp_registry.register(GlossaryReadTool())
mcp_registry.register(IntentClassifierTool())
mcp_registry.register(SalesSQLReadTool())
mcp_registry.register(SalesSQLWriteTool())

