FROM tangchen2018/python:3.6-alpine
ENV PYTHONUNBUFFERED 1

COPY . /project/fianceweb

WORKDIR /project/fianceweb

RUN apk add --no-cache tzdata  && \
    apk add linux-headers && \
    apk add gcc-core && \
    apk add libjpeg-devel && \
    apk add zlib-devel && \
    apk add python3-devel && \
    apk add python3-setuptools && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

RUN pip install -r requirements.txt \
    && mkdir -p /project/fianceweb/logs \
    && mkdir -p /project/fianceweb/media

CMD ["uwsgi", "/project/fianceweb/education/wsgi/uwsgi.ini"]
