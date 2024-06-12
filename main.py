from datetime import datetime
from fastapi import FastAPI
import uvicorn

from db import sqlite_setup
from db.load_data import load_data
from routers.property import property_router



app = FastAPI()

#add routers to main app
app.include_router(property_router)

@app.get("/")
def health():
    return {"status" : "this service is healthy @ " + datetime.now().__str__()}

if __name__ == "__main__":
    # initialize db before starting the api server
    sqlite_setup.create_db_tables()
    ## Load data
    load_data('./zoomprop_data_engineering.csv')
    uvicorn.run(app, host="0.0.0.0", port=8000)