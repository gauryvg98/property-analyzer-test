from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from db import sqlite_setup
from db.load_data import load_data
from routers.property import property_router
from routers.visualization import visualization_router
from sqlalchemy_schemas.property import Property


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="./static"), name="static")

#add routers to main app
app.include_router(property_router, prefix="/property")
app.include_router(visualization_router, prefix="/visualization")

@app.get("/")
def health():
    return {"status" : "this service is healthy @ " + datetime.now().__str__()}

if __name__ == "__main__":
    # initialize db before starting the api server
    created_new_table = sqlite_setup.create_db_tables()
    ## Load data
    load_data('./zoomprop_data_engineering.csv')
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)