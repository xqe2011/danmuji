FROM python:3
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/

ENV TZ=Asia/Shanghai
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata

COPY run.sh ./
COPY app ./app

RUN mkdir logs

ENTRYPOINT ["./run.sh"]