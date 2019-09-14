FROM pytorch/pytorch:1.2-cuda10.0-cudnn7-runtime

RUN pip install catalyst==19.9.3
RUN pip install albumentations==0.3.2
RUN pip install opencv-python==4.1.1.26
RUN pip install numpy==1.17.2
RUN pip install imageio==2.5.0

RUN pip install fastapi[all]==0.38.1
RUN pip install aio-pika==6.1.1

RUN apt-get update -y && apt-get install -y libglib2.0-0

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONPATH=/src

WORKDIR /src

COPY . .
RUN python setup.py install && rm -rf *

COPY example/ /src/
