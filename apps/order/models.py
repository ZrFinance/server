import time
from django.db import models
from django.utils import timezone

# Create your models here.

class Order(models.Model):

    ordercode = models.BigAutoField(primary_key=True)
    trantype = models.IntegerField(verbose_name="类型:0-认筹股权,1-股权分红",default=0)
    subtrantype = models.IntegerField(verbose_name="类型:0-认筹股权,1-推广股权,2-股权权益",default=0)
    amount = models.IntegerField(verbose_name="交易金额",default=0)
    userid = models.BigIntegerField(default=0)
    username=models.CharField(max_length=60,default='')
    userid_to = models.CharField(max_length=512,default=0)
    username_to = models.CharField(max_length=512,default='')
    ordercode_to = models.CharField(max_length=512,default='')
    status = models.IntegerField(verbose_name='状态:0-未匹配,1-匹配成功,2-已完成')
    statusname = models.IntegerField(default=0,verbose_name='0-待打款/待收款,1-确认打款/确认收款-(该字段放弃使用)')
    confirm = models.IntegerField(default=0,verbose_name='0-未确认,2-已确认-(该字段放弃使用)')
    createtime=models.BigIntegerField(default=0)
    updtime = models.BigIntegerField(default=0)
    img = models.CharField(max_length=255)

    mobile=None
    name=None
    count=None
    alipay=None
    wechat=None
    bank=None
    referee_name=None
    bank_account=None

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
    trantype = models.IntegerField(
        verbose_name="""类型: 
            1-认筹权转出,
            2-认筹权转入,
            3-幸运认筹消耗,
            4-激活码转出,
            5-激活码转入，
            6-转盘投资赠送 VIP分,
            7-系统赠送股权分红,
            8-系统赠送推广股权,
            9-投资本金,
            10-投资利息,
            11-提取收益扣款(推广股权),
            12-提取收益扣款(股份分红),
            13-一代奖金,
            14-二代奖金,
            15-系统赠送激活码,
            16-系统赠送认筹权,
            17-提供帮助认筹消耗
            18-提供帮助赠送 VIP分,
            19-激活码激活用户,
            20-规定时间内无匹配,推荐奖作废,
            21-规定时间内无匹配,推荐奖作废(冻结),
            22-一代奖金(冻结),
            23-二代奖金(冻结),
            24-订单拆分
            """, default=0)
    tranname = models.CharField(max_length=100,default='')
    userid = models.BigIntegerField(default=0)
    username=models.CharField(max_length=60,default='')
    userid_to = models.BigIntegerField(default=0)
    username_to = models.CharField(max_length=60,default='')
    bal = models.IntegerField()
    amount = models.IntegerField()
    createtime = models.BigIntegerField()
    ordercode = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        t= time.mktime(timezone.now().timetuple())
        if self.trantype == 1:
            self.tranname = '转出{}'.format(self.username_to)
        elif self.trantype == 2:
            self.tranname = '{}转入'.format(self.username_to)
        elif self.trantype == 3:
            self.tranname = '幸运排单消耗'
        elif self.trantype == 4:
            self.tranname = '转出{}'.format(self.username_to)
        elif self.trantype == 5:
            self.tranname = '{}转入'.format(self.username_to)
        elif self.trantype == 6:
            self.tranname = '转盘投资赠送'
        elif self.trantype == 7:
            self.tranname = '系统赠送股权分红'
        elif self.trantype == 8:
            self.tranname = '系统赠送推广股权'
        elif self.trantype == 9:
            self.tranname = '投资本金'
        elif self.trantype == 10:
            self.tranname = '投资利息'
        elif self.trantype == 11:
            self.tranname = '提取收益扣款(推广股权)'
        elif self.trantype == 12:
            self.tranname = '提取收益扣款(股份分红)'
        elif self.trantype == 13:
            self.tranname = '一代奖金'
        elif self.trantype == 14:
            self.tranname = '二代奖金'
        elif self.trantype == 15:
            self.tranname = '系统赠送激活码'
        elif self.trantype == 16:
            self.tranname = '系统赠送认筹权'
        elif self.trantype == 17:
            self.tranname = '提供帮助认筹消耗'
        elif self.trantype == 18:
            self.tranname = '提供帮助赠送'
        elif self.trantype == 19:
            self.tranname = '激活{}'.format(self.username_to)
        elif self.trantype == 20:
            self.tranname = '规定时间内无匹配,推荐奖作废'
        elif self.trantype == 21:
            self.tranname = '规定时间内无匹配,推荐奖作废(冻结)'
        elif self.trantype == 22:
            self.tranname = '一代奖金(冻结)'
        elif self.trantype == 23:
            self.tranname = '二代奖金(冻结)'
        if not self.createtime:
            self.createtime = t
        return super(Tranlist, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '交易明细表'
        verbose_name_plural = verbose_name
        db_table = 'tranlist'

class MatchPool(models.Model):
    id = models.BigIntegerField(primary_key=True)
    ordercode = models.BigIntegerField()
    trantype = models.IntegerField(verbose_name='0:提供帮助列表, 1-接受帮助列表')
    createtime = models.BigIntegerField()
    flag = models.IntegerField(verbose_name='0-未匹配,1-已匹配')
    matchtime = models.BigIntegerField(verbose_name='匹配时间')

    def save(self, *args, **kwargs):
        t= time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        return super(MatchPool, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '匹配池'
        verbose_name_plural = verbose_name
        db_table = 'matchpool'