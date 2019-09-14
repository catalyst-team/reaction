import asyncio
import json
import logging
import os
from typing import List, Any

import cv2
import torch
from albumentations import Compose, Normalize, LongestMaxSize, PadIfNeeded
from albumentations.torch import ToTensor

from common import rpc_uri
from reaction.rpc import RabbitRPC as RPC


@RPC(rpc_uri)
def recognize(*imgs) -> List[Any]:
    return [i.shape for i in imgs]


@RPC(rpc_uri)
def recognize_passport(*imgs) -> List[Any]:
    return [i.shape[0] / i.shape[1] for i in imgs]


@RPC(rpc_uri, timeout=3)
async def square(*values) -> List[float]:
    await asyncio.sleep(1)
    return [v ** 2 for v in values]


class SimpleModel:
    def load(self, path='model'):
        self.model = torch.jit.load(os.path.join(path, 'model.pth'))
        with open(os.path.join(path, 'tag2class.json')) as fin:
            self.tag2class = json.load(fin)
            self.class2tag = {v: k for k, v in self.tag2class.items()}
            logging.info(f'class2tag: {self.class2tag}')

    @RPC(rpc_uri, name='simple_model')
    def predict(self, *imgs) -> List[str]:
        res = []
        for img in imgs:
            logging.info(f'image: {img.shape}')

            transofrm = Compose([
                LongestMaxSize(max_size=224),
                PadIfNeeded(224, 224, border_mode=cv2.BORDER_CONSTANT),
                Normalize(),
                ToTensor()
            ])

            input_t = transofrm(image=img)["image"].unsqueeze_(0)
            logging.info(f'input_t: {input_t.shape}')
            output_t = self.model(input_t).squeeze_(0)
            logging.info(f'output_t: {output_t.shape}')

            tag = self.class2tag[output_t.argmax().item()]
            logging.info(f'result: {tag}')
            res.append(tag)
        return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(square.consume())
    loop.create_task(recognize.consume())
    loop.create_task(recognize_passport.consume())

    # m = SimpleModel()
    # m.load()
    # loop.create_task(m.predict.bind(m).consume())

    loop.run_forever()
