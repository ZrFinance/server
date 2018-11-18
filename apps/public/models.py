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

    help_amount = models.CharField(default='',max_length=100,verbose_name='提供帮助金额',null=True)
    morning_amount = models.IntegerField(default=0,verbose_name='每天上午可排单资金总额',null=True)
    after_amount = models.IntegerField(default=0,verbose_name='每天下午可排单资金总额',null=True)
    limit = models.IntegerField(default=0,verbose_name='超出该时间未打款可投诉',null=True)
    amount_term = models.IntegerField(default=0,verbose_name='匹配后最后打款期限',null=True)
    amount_term1 = models.IntegerField(default=0,verbose_name='打款后收款期限',null=True)
    morning = models.CharField(max_length=60,default='',verbose_name='每天排单（提供帮助）开时间段',null=True)
    after = models.CharField(max_length=60,default='',verbose_name='每天排单（提供帮助）开时间段2',null=True)
    term = models.IntegerField(default=0,verbose_name='提供帮助排队期',null=True)
    term1 = models.IntegerField(default=0, verbose_name='提现匹配排队期',null=True)
    interset = models.IntegerField(default=0,verbose_name='（排单）两小时内打款利息',null=True)
    interset1 = models.IntegerField(default=0,verbose_name='（排单）两小时后打款利息',null=True)
    time1 = models.IntegerField(default=0,verbose_name='排队时间提醒',null=True)
    count1 = models.IntegerField(default=0,verbose_name='每天最多能提供帮助(排单)的次数',null=True)
    count2 = models.IntegerField(default=0,verbose_name='每天最多能申请帮助的次数',null=True)
    count3 = models.IntegerField(default=0,verbose_name='可存在的最大未完成提供帮助单数',null=True)
    amount1 = models.IntegerField(default=0,verbose_name='申请帮助(股权分红)最低金额(收益申请)',null=True)
    amount2 = models.IntegerField(default=0,verbose_name='申请帮助股权分红*的倍数(收益申请)',null=True)
    amount3 = models.IntegerField(default=0,verbose_name='申请帮助股权分红最高限制金额(收益申请)',null=True)
    amount4 = models.IntegerField(default=0, verbose_name='申请帮助推广股权最低金额',null=True)
    amount5 = models.IntegerField(default=0,verbose_name='申请帮助推广股权*的倍数(收益申请)',null=True)
    amount6 = models.IntegerField(default=0,verbose_name='申请帮助（推广股权）每天最高限额',null=True)
    amount7 = models.IntegerField(default=0,verbose_name='一代领导奖(%)',null=True)
    amount8 = models.IntegerField(default=0,verbose_name='二代领导奖(%)',null=True)
    amount9 = models.IntegerField(default=0,verbose_name='满足条件一代领导奖(%)',null=True)
    amount10 = models.IntegerField(default=0,verbose_name='满足条件二代领导奖(%)',null=True)

    flag1 = models.IntegerField(default=0,verbose_name="推广奖冻结比例%",null=True)

    class Meta:
        verbose_name = 'SysParam'
        verbose_name_plural = verbose_name
        db_table = "sysparam"

class Lucky(models.Model):
    id = models.BigAutoField(primary_key=True)
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