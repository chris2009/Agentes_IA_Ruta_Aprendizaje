from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from datetime import date
from dotenv import load_dotenv
load_dotenv()  # Cargar variables de entorno desde .env

class agent_openai:
    def __init__(self):
        self.model = "gpt-4o-mini"
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.sysprompt = """Eres un agente de WebRTC por lo que todas tus respuestas con concisas y cortas, sin uso de emojis.
             Tu objetivo es usar las herramientas que tienes disponibles para responder las preguntas que te hagan"""
        self.tools = [self.get_systemtime]

    @tool
    def get_systemtime():
        """
        Returns today's system date
        """
        return date.today()
    
    @tool
    def search_theweb():
        """
        Returns a TavilySearchResults object in order to search the web
        """
        return TavilySearchResults()