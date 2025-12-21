from typing import Annotated, List, TypedDict, Union, Optional, Literal, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os, sys
from typing import Literal
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from pathlib import Path    
from dotenv import load_dotenv
import json
load_dotenv()

current_path = Path(__file__).resolve()
PROJECT_ROOT = current_path.parent.parent.parent

class JobseekerRcsUpdateAgent:
    def __init__(self):
        pass
    def run(self):
        pass

