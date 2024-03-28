from fastapi import FastAPI
from apis import dataanalisis_api




app = FastAPI()

#incluir las rutas
app.include_router(dataanalisis_api.router)

@app.get("/")
async def index():
    return {"status":"ok"}





