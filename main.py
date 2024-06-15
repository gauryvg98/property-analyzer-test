from datetime import datetime
import os
from typing import Optional
from fastapi import FastAPI, Query
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

@app.get("/load/")
def load_data_file(is_filtered: Optional[bool] = Query(False)):
    load_data('./zoomprop_data_engineering.csv', is_filtered)
    return {"status" : "loaded data successfully"}

if __name__ == "__main__":
    # initialize db before starting the api server
    sqlite_setup.create_db_tables()
    ## Load data
    ### comment out the line below if you want sync load before app start (break heroku dyno due to timeouts)
    ##load_data('./zoomprop_data_engineering.csv', is_filtered=True)

    # Use the PORT environment variable provided by Heroku
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)