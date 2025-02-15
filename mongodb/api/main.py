import os
from typing import Optional, List

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator

from typing_extensions import Annotated

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument


app = FastAPI(
    title="Student Course API",
    summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)
url = f"mongodb+srv://{username}:{password}@{url}/{db}?retryWrites=true&w=majority"
client = motor.motor_asyncio.AsyncIOMotorClient(url)
db = client.trustscore_reviews
review_collection = db.get_collection("trustscore_reviews")