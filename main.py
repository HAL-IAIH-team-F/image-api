import io
from typing import Union

from bson import Binary
from fastapi import FastAPI, HTTPException
from fastapi import File, UploadFile, Form, Query
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient, errors

from app.data import JwtTokenData
from app.tokens import *

print("init")
#build 
# uvicorn main:app

app = FastAPI()

#MongoDB Client 
client = MongoClient("mongodb://localhost:27017/")
db = client["image_database"]
collection = db["images"]
templates = Jinja2Templates(directory="templates")

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

            return {"status":"OK","image_uuid": token.uuid}
        else:
            return {"status":"Error token type"}
    except:
        return {"status":"Error token none"}
    
@app.put("/image_preference/{image_uuid}")
async def post_image(image_uuid: str, state: str = Form(...)):
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


