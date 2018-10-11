import time
from django.db import models
from django.utils import timezone

# Create your models here.

class Order(models.Model):

    ordercode = models.BigAutoField(primary_key=True)
    trantype = models.IntegerField(verbose_name="类型:0-认筹股权,1-股权分红",default=0)
    amount = models.IntegerField(verbose_name="交易金额",default=0)
    userid = models.BigIntegerField(default=0)
    username=models.CharField(max_length=60,default='')
    userid_to = models.BigIntegerField(default=0)
    username_to = models.CharField(max_length=60,default='')
    status = models.IntegerField(verbose_name='状态:0-未匹配,1-匹配成功,待打款,2-已完成')
    createtime=models.BigIntegerField(default=0)
    updtime = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        t= time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        if not self.updtime:
            self.updtime = t
        return super(Order, self).save(*args, **kwargs)

    def __str__(self):
        if self.trantype == 0:
            return 'R{}'.format(str(self.ordercode).zfill(11))
        else:
            return 'G{}'.format(str(self.ordercode).zfill(11))

    class Meta:
        verbose_name = '订单表'
        verbose_name_plural = verbose_name
        db_table = 'order'

class Tranlist(models.Model):

    id = models.BigIntegerField(primary_key=True)
    trantype = models.IntegerField(verbose_name="类型: 1-认筹权转出,2-认筹权转入,3-幸运认筹消耗,4-激活码转出,5-激活码转入", default=0)
    userid = models.BigIntegerField(default=0)
    username=models.CharField(max_length=60,default='')
    userid_to = models.BigIntegerField(default=0)
    username_to = models.CharField(max_length=60,default='')
    bal = models.IntegerField()
    amount = models.IntegerField()
    createtime = models.BigIntegerField()

    def save(self, *args, **kwargs):
        t= time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        return super(Tranlist, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '交易明细表'
        verbose_name_plural = verbose_name
        db_table = 'tranlist'