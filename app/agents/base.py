from abc import ABC, abstractmethod
from typing import Callable
from pydantic import BaseModel

from langchain.agents import create_agent


class Reference(BaseModel):
    reference_url: str
    reference_title: str
    reference_description: str
    reference_summary: str = ""


class Agent(ABC):

    def __init__(self, llm: Callable, tools: list[str]) -> None:
        self.llm = llm
        self.tools = tools
        self.llm_response = {}

    # @abstractmethod
    # async def invoke(self, input_params: BaseModel):
    #     pass

    def build(self, response_format: BaseModel = None):
        if response_format:
            return create_agent(model=self.llm, tools=self.tools, response_format=response_format)
        return create_agent(model=self.llm, tools=self.tools)
