import time
from django.db import models
from django.utils import timezone

# Create your models here.


class ServerAdminUser(models.Model):

    userid=models.BigAutoField(primary_key=True)
    mobile=models.CharField(max_length=11,verbose_name='手机号',default='')
    username=models.CharField(max_length=60,verbose_name="名称",default='',null=True)
    passwd=models.CharField(max_length=60,verbose_name='密码',default='')
    createtime=models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        t=time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        if not self.username:
            self.username = self.mobile
        return super(ServerAdminUser, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        db_table = 'serveradminuser'