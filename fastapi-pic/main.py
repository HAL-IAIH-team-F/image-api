from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pymongo import MongoClient, errors
from bson import Binary
import uuid
import base64
import os

app = FastAPI()

#MongoDB Client 
client = MongoClient("mongodb://localhost:27017/")
db = client["image_database"]
collection = db["images"]
@app.get("/")
async def index():
    content = """
    <body>
    <h1>Image Upload API</h1>
    <button class="Index" type="button" onclick="window.location.href='/'">index</button>
    <button class="Docs" type="button" onclick="window.location.href='/docs'">Docs</button>
    <button class="Main" type="button" onclick="window.location.href='/main'">Main</button>
    </body>
    """
    return HTMLResponse(content=content)
    

@app.get("/main")
async def main(request: Request):
    images = collection.find()
    image_list = []
    for image in images:
        encoded_image = base64.b64encode(image['file_data']).decode('utf-8')
        file_extension = image['original_filename'].split('.')[-1]
        uuid = image['uuid'].split('.')[-1]
        image_list.append({
            "data": encoded_image,
            "extension": file_extension,
            "filename": image['original_filename'],
            "uuid": uuid
        })

    return templates.TemplateResponse("index.html", {"request": request, "images": image_list})


templates = Jinja2Templates(directory="templates")

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    file_content = await file.read()
    generated_uuid = str(uuid.uuid4())

    image_data = {
        "uuid": generated_uuid,
        "original_filename": file.filename,
        "file_data": Binary(file_content)
    }
    try:
        collection.insert_one(image_data)
    except errors.PyMongoError as e:
        return {"error": str(e)}

    return {"info": f"file '{file.filename}' saved with uuid '{generated_uuid}'"}


@app.get("/image/{image_uuid}")
async def get_image(image_uuid: str):
    image_data = collection.find_one({"uuid": image_uuid})
    if image_data is None:
        return {"error": "Image not found"}
    encoded_image = base64.b64encode(image_data['file_data']).decode('utf-8')
    file_extension = image_data['original_filename'].split('.')[-1]
    return HTMLResponse(content=f"<img src='data:image/{file_extension};base64,{encoded_image}'/>")

