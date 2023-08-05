FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt-get update && apt-get install -y g++
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/

ENV TZ=Asia/Shanghai
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata

COPY run.sh ./
COPY app ./app

RUN mkdir logs

ENTRYPOINT ["./run.sh"]