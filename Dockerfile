FROM tangchen2018/python:3.6-alpine
ENV PYTHONUNBUFFERED 1

COPY . /project/fianceweb

WORKDIR /project/fianceweb

RUN pip install -r requirements.txt \
    && mkdir -p /project/fianceweb/logs \
    && mkdir -p /project/fianceweb/media

RUN apk add --no-cache tzdata  && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

CMD ["uwsgi", "/project/fianceweb/education/wsgi/uwsgi.ini"]
