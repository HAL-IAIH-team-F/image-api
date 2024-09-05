from fastapi import FastAPI, File, UploadFile,Depends, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pymongo import MongoClient, errors
from bson import Binary
import uuid
import base64
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.responses import FileResponse
import io
from datetime import timedelta, datetime, timezone
from app.data import JwtTokenData
from app.tokens import *
from datetime import datetime
from typing import Union


print("init")
#build 
# uvicorn main:app

app = FastAPI()

#MongoDB Client 
client = MongoClient("mongodb://localhost:27017/")
db = client["image_database"]
collection = db["images"]
templates = Jinja2Templates(directory="templates")

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

    return templates.TemplateResponse("app//index.html", {"request": request, "images": image_list})




@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), token : JwtTokenData | None = Depends(get_token_or_none)):
    print(token)
    try:
        if token.token_type == "Upload":
            file_content = await file.read()
            dt_now = datetime.now()
            
            image_data = {
                "uuid": token.uuid,
                "original_filename": file.filename,
                "file_data": Binary(file_content),
                "upload_date" : dt_now,
                "state" : "Temp"
            }
            try:
                collection.insert_one(image_data)
            except errors.PyMongoError as e:
                return {"status": [str(e)]}

            return {"status":"OK"}
        else:
            return {"status":"error TOKEN type"}
    except:
        return {"status":"error TOKEN none"}
    
@app.put("/image_preference/{image_uuid}")
async def post_image(image_uuid: str, state: str = Form(...)):  # Formを使ってstateを受け取る
    try:
        image_data = collection.find_one({"uuid": image_uuid})
        
        if image_data:
            collection.update_one(
                {"uuid": image_uuid},
                {"$set": {"state": state}}
            )
            return {"status": "State updated", "new_state": state}
        else:
            return {"status": "Image not found"}

    except errors.PyMongoError as e:
        return {"status": [str(e)]}
    
@app.get("/image/{image_uuid}")
async def get_image(image_uuid: str,q: Union[str, None] = Query(default=None, max_length=50)):
    image_data = collection.find_one({"uuid": image_uuid})
    
    if image_data is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image_state = image_data['state']
    
    if image_state == 'Public':
        return _stream_image(image_data)
        
    elif image_state == 'Private':
        if q is None:
            raise HTTPException(status_code=400, detail="Token required")
        
        token = data.JwtTokenData(**jwt.decode(q, SECRET_KEY, algorithms=[ALGORITHM]))
        if token.token_type == 'Access':
            return _stream_image(image_data)
        else:
            raise HTTPException(status_code=403, detail="Invalid token type")
    
    return {"status": "Image not Public", "state": image_state}


def _stream_image(image_data):
    file_data = image_data['file_data']
    file_extension = image_data['original_filename'].split('.')[-1]
    file_stream = io.BytesIO(file_data)
    media_type = f"image/{file_extension}"
    return StreamingResponse(file_stream, media_type=media_type)

@app.get("/test/token")
async def test_token():
    return create_token(token_type="Upload",expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))

@app.get("/test/get")
async def test_get(token : JwtTokenData | None = Depends(get_token)):
    return "test_get"


