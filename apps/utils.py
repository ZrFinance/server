from rest_framework import (viewsets)

from apps.public.task.api import task1

class GenericViewSetCustom(viewsets.ViewSet):
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.start()

    # def test():
    #     print("11111111111111")
    #
    # scheduler.add_job(test, 'interval', seconds=5)

    scheduler.add_job(task1,'interval',minutes=1 )