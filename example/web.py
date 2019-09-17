from enum import Enum
from typing import Optional
from typing import Tuple

import imageio
from fastapi import File, UploadFile
from pydantic import BaseModel

import services
from common import app


class SquareResult(BaseModel):
    result: float


class Orientation(Enum):
    portrait = "portrait"
    album = "album"


class ImageResult(BaseModel):
	label: str
	square: int
	orientation: Orientation
    shape: Tuple[int, int]


class ClassifyModelResult(BaseModel):
    tag: str


@app.get("/square/{value}", response_model=SquareResult)
async def get_square(value: float):
    return SquareResult(
        result=await services.square.call(value)
    )


@app.post("/image_info", response_model=ImageResult)
async def get_image_info(
        label: str,
        image: UploadFile = File(...),
):
    img = imageio.imread(await image.read())
    w, h = await services.get_shape.call(img)[:2]
    o = orientation.album if w > h else Orientation.portrait
    return ImageResult(
        label=label,
        square=w * h,
        orientation=o,
        shape=(w, h)
    )


@app.post("/classify", response_model=ClassifyModelResult)
async def classify(image: UploadFile = File(...)):
    img = imageio.imread(await image.read())
    return ClassifyModelResult(
        tag=await services.ClassifyModel().predict.call(img),
    )
