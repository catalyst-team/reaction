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


class DocType(Enum):
    passport_main = "passport_main"
    inn_person = "inn_person"


class RecognizeResult(BaseModel):
    doc_type: DocType
    result: Tuple[int, int, int]


class RecognizePassportField(BaseModel):
    text: str
    confidence: float


class RecognizePassportResult(BaseModel):
    first_name: Optional[RecognizePassportField]
    second_name: Optional[RecognizePassportField]
    sex: Optional[RecognizePassportField]


class SimpleModelResult(BaseModel):
    tag: str


@app.get("/square/{value}", response_model=SquareResult)
async def get_square(value: float):
    return SquareResult(
        result=await services.square.call(value)
    )


@app.post("/recognize", response_model=RecognizeResult)
async def recognize(
        doc_type: DocType,
        image: UploadFile = File(...),
):
    img = imageio.imread(await image.read())
    return RecognizeResult(
        doc_type=doc_type,
        result=await services.recognize.call(img)
    )


@app.post("/recognize/passport_main", response_model=RecognizePassportResult)
async def recognize_passport(image: UploadFile = File(...)):
    img = imageio.imread(await image.read())
    return RecognizePassportResult(
        first_name=RecognizePassportField(
            text='qwe2',
            confidence=await services.recognize_passport.call(img)
        ),
        second_name=RecognizePassportField(
            text='qwe2',
            confidence=await services.recognize_passport.call(img)
        ),
        sex=RecognizePassportField(
            text='qwe2',
            confidence=await services.recognize_passport.call(img)
        ),
    )


@app.post("/recognize/simple_model", response_model=SimpleModelResult)
async def recognize_simple_model(image: UploadFile = File(...)):
    img = imageio.imread(await image.read())
    return SimpleModelResult(
        tag=await services.SimpleModel().predict.call(img),
    )
