

from apscheduler.schedulers.background import BackgroundScheduler


class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

def test():
    print("11111111111111")


def test1():
    print("2222222222222222")


