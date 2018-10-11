FROM tangchen2018/python:3.6-alpine
ENV PYTHONUNBUFFERED 1

COPY . /project/fianceweb

WORKDIR /project/fianceweb

RUN apk add --no-cache --virtual=build-dependencies tzdata  mariadb-dev \
    g++ \
    build-base libffi-dev python3-dev \
    libffi openssl ca-certificates \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
    linux-headers pcre-dev  && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

RUN pip install -r requirements.txt \
    && mkdir -p /project/fianceweb/logs \
    && mkdir -p /project/fianceweb/media

CMD ["uwsgi", "/project/fianceweb/education/wsgi/uwsgi.ini"]
