import os
import pymongo

from typing import Optional, List

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator

from typing_extensions import Annotated

from bson import ObjectId
import motor.motor_asyncio



app = FastAPI(
    title="API for MongoDB",
    )

myclient = pymongo.MongoClient("mongodb://localhost:27017/")


# Check if database and collection exists
dblist = myclient.list_database_names()
if "trustscore_db" not in dblist:
    mydb = myclient["trustscore_db"]
    collist = mydb.list_collection_names()
    if "trustscore_reviews" not in collist:
        mydb = myclient["trustscore_db"]
        mycol = mydb["trustscore_reviews"]

# username = os.environ.get("MONGODB_USER")
# password = os.environ.get("MONGODB_PASSWORD")
# url = os.environ.get("MONGODB_HOST")
# db = os.environ.get("MONGODB_DATABASE")

# url = f"mongodb+srv://{username}:{password}@{url}/{db}?retryWrites=true&w=majority"
# client = motor.motor_asyncio.AsyncIOMotorClient(url)
db = client.trustscore_reviews
review_collection = db.get_collection("trustscore_reviews")