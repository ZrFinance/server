from django.db import models
import random
import time
import datetime
from django.utils import timezone

class SysParam(models.Model):

    bfb1000=models.IntegerField(default=0,verbose_name='幸运转盘1000百分比')
    bfb2000=models.IntegerField(default=0,verbose_name='幸运转盘2000百分比')
    bfb5000=models.IntegerField(default=0,verbose_name='幸运转盘5000百分比')
    bfb10000=models.IntegerField(default=0,verbose_name='幸运转盘10000百分比')
    bfbwzj=models.IntegerField(default=0,verbose_name='幸运转盘未中奖百分比')

    class Meta:
        verbose_name = 'SysParam'
        verbose_name_plural = verbose_name
        db_table = "sysparam"

class Lucky(models.Model):
    userid = models.BigIntegerField(default=0)
    index = models.IntegerField(default=0)
    name = models.CharField(max_length=60,default='')
    createtime=models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        t=time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        return super(Lucky, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '抽奖表'
        verbose_name_plural = verbose_name
        db_table = 'lucky'

class PicVerCode(models.Model):

    filename  = models.CharField(max_length=60)
    vercode = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'PicVerCode'
        verbose_name_plural = verbose_name
        db_table="picvercode"

class Verification(models.Model):
    mobile = models.CharField(max_length=11)
    code = models.CharField(max_length=4,default='')
    validtime = models.BigIntegerField(default=0)
    createtime = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        valid = 3  # min
        if not self.code:
            self.code = str(random.randint(1000, 9999))
        t=timezone.now()
        if not self.createtime:
            self.createtime = time.mktime(t.timetuple())
        if not self.validtime :
            self.validtime = t + datetime.timedelta(minutes=valid)
            self.validtime = time.mktime(self.validtime.timetuple())
        return super(Verification, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '验证码表'
        verbose_name_plural = verbose_name
        db_table = 'verification'

class Banner(models.Model):


    id  = models.BigAutoField(primary_key=True)
    url = models.CharField(max_length=60)

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = verbose_name
        db_table="banner"

class Notice(models.Model):

    title = models.CharField(max_length=255)
    content = models.TextField()
    createtime = models.BigIntegerField(default=0)

    class Meta:
        verbose_name = 'Notice'
        verbose_name_plural = verbose_name
        db_table="notice"