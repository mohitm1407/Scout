from abc import ABC , abstractmethod
from pydantic import BaseModel

class Agent(ABC):
    
    @abstractmethod
    async def invoke(cls , input_params : BaseModel):
        pass 
    
    