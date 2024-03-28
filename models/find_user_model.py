from  pydantic import BaseModel


class find_user_model(BaseModel):
    user:str
    id_user_count: int
    numberRecords:int
    
