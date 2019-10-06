FROM pytorch/pytorch:1.2-cuda10.0-cudnn7-runtime

RUN apt-get update -y && \
    apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender-dev wget curl

RUN pip install albumentations==0.3.2
RUN pip install opencv-python==4.1.1.26
RUN pip install numpy==1.17.2
RUN pip install imageio==2.5.0
RUN pip install catalyst==19.9.3
RUN pip install aiotg==1.0.0

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONPATH=/src

WORKDIR /src

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN wget https://www.dropbox.com/s/sl0fbzeo2fgbmum/classifier-190915.tar && \
    tar -xvf classifier-190915.tar && \
    rm classifier-190915.tar && \
    mv classifier-190915 /model

COPY . .
RUN python setup.py install && rm -rf *

COPY example/ .
