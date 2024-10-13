from pydantic import BaseModel

import mdls


class ImgPreferenceBody(BaseModel):
    state: mdls.State
