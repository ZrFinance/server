import binascii
import os
import time
from django.db import models
from django.utils import timezone

class Token(models.Model):

    key = models.CharField(max_length=160, primary_key=True)
    userid  = models.BigIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Token'
        verbose_name_plural = verbose_name
        db_table="user_token"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(80)).decode()

    def __str__(self):
        return self.key

class Login(models.Model):

    mobile=models.CharField(max_length=11,verbose_name='手机号',null=False)
    createtime=models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(Login, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '用户登录表'
        verbose_name_plural = verbose_name
        db_table = 'login'

class Users(models.Model):

    userid=models.BigAutoField(primary_key=True)
    mobile=models.CharField(max_length=11,verbose_name='手机号',default='')
    username=models.CharField(max_length=60,verbose_name="名称",default='',null=True)
    passwd=models.CharField(max_length=60,verbose_name='密码',default='')
    pay_passwd=models.CharField(max_length=60,verbose_name='支付密码',default='')
    referee_name=models.CharField(max_length=60,verbose_name='推荐人手机号',default='')
    createtime=models.BigIntegerField(default=0)
    agent = models.TextField(verbose_name='所有下线代理,逗号分隔',null=True,default='')
    lastindex = models.IntegerField(default=0,verbose_name='上一次指定转盘奖品索引',null=True)
    status = models.IntegerField(default='1',verbose_name="状态:0-正常,1-未激活,2-禁用",null=True)
    blockcount = models.IntegerField(default=0,verbose_name="被封次数")
    activation = models.IntegerField(verbose_name="激活码",default=0,null=True)
    buypower = models.IntegerField(verbose_name="认筹权",default=0,null=True)
    integral = models.IntegerField(verbose_name='VIP分',default=0,null=True)
    bonus =  models.IntegerField(verbose_name="股权分红",default=0,null=True)
    spread = models.IntegerField(verbose_name="推广股权",default=0,null=True)
    spreadstop = models.IntegerField(verbose_name="推广股权冻结",default=0,null=True)
    idcard=models.CharField(max_length=20,verbose_name="身份证号",default='',null=True)
    name=models.CharField(max_length=60,verbose_name="真实姓名",null=True,default='')
    alipay=models.CharField(max_length=60,verbose_name="支付宝",default='',null=True)
    wechat=models.CharField(max_length=60,verbose_name="微信",default='',null=True)
    bank=models.CharField(max_length=60,verbose_name="银行名称",default='',null=True)
    bank_account=models.CharField(max_length=60,verbose_name="银行账户",default='',null=True)

    def save(self, *args, **kwargs):
        t=time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        if not self.username:
            self.username = self.mobile
        return super(Users, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        db_table = 'user'

class Agent(models.Model):
    id = models.BigAutoField(primary_key=True)
    mobile = models.CharField(max_length=20)
    mobile1 = models.CharField(max_length=20,verbose_name="代理",default="")
    level = models.IntegerField(default=1,verbose_name='代理等级')
    createtime=models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(Agent, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '代理表'
        verbose_name_plural = verbose_name
        db_table = 'agent'
