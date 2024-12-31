import uuid

import bodies
import reses
from main import app, collection
from util import err


@app.put("/preference/{image_uuid}")
async def img_preference(
        image_uuid: uuid.UUID,
        body: bodies.ImgPreferenceBody
) -> reses.ImgPreferenceRes:
    image_data = collection.find_one({"uuid": image_uuid.__str__()})

    if image_data is None:
        raise err.ErrorIds.IMAGE_NOT_FOUND.to_exception("image data not found")
    filename = image_data.get("original_filename")
    collection.update_one(
        {"uuid": image_uuid.__str__()},
        {"$set": {"state": body.state.value}}
    )
    return reses.ImgPreferenceRes.create(filename)


@app.get("/preference/{image_uuid}")
async def img_preference(
        image_uuid: uuid.UUID,
) -> reses.ImgPreferenceRes:
    image_data = collection.find_one({"uuid": image_uuid.__str__()})

    if image_data is None:
        raise err.ErrorIds.IMAGE_NOT_FOUND.to_exception("image data not found")
    filename = image_data.get("original_filename")

    return reses.ImgPreferenceRes.create(filename)
