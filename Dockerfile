FROM tangchen2018/python:3.6-alpine
ENV PYTHONUNBUFFERED 1

COPY . /project/sso

WORKDIR /project/sso

RUN apk add --no-cache tzdata  && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

RUN pip install -r requirements.txt \
    && mkdir -p /project/sso/logs \
    && mkdir -p /project/sso/media \
    && mkdir -p /var/logs/sso \
    && echo "" > /var/logs/sso/cron.log


CMD crond && uwsgi /project/sso/education/wsgi/uwsgi.ini
#CMD ["python", "/project/sso/manage.py crontab remove"]
#CMD ["python", "/project/sso/manage.py crontab add"]
