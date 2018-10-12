from rest_framework import viewsetsfrom rest_framework.decorators import list_routefrom core.decorator.response import Core_connectorfrom utils.exceptions import PubErrorCustomfrom apps.user.serializers import UsersSerializerfrom apps.public.utils import check_verification_code,check_picvercodefrom apps.user.utils import add_referee_namefrom apps.user.models import Usersclass UserAPIView(viewsets.ViewSet):    @list_route(methods=['POST'])    @Core_connector(transaction=True,serializer_class=UsersSerializer,model_class=Users)    def register(self, request,*args,**kwargs):        check_verification_code(self.request.data)        #check_picvercode(self.request.data)        add_referee_name(self.request.data)        serializer = kwargs.pop('serializer')        isinstance=serializer.save()        token=Token.objects.create(userid=isinstance.userid)        header={"Authorization": token.key}        data = {            'username': isinstance.username        }        return {"data":data,"header":header,"msg":"注册成功！"}    @list_route(methods=['POST'])    @Core_connector(transaction=True)    def login(self, request, *args, **kwargs):        userlogin=Login()        userlogin.mobile=self.request.data.get('mobile')        #check_picvercode(self.request.data)        try:            user=Users.objects.get(mobile=userlogin.mobile)        except Users.DoesNotExist:            raise PubErrorCustom("手机号错误！")        if user.passwd != self.request.data.get('passwd'):            raise PubErrorCustom("密码错误！")        userlogin.save()        token = Token.objects.create(userid=user.userid)        header = {"Authorization": token.key}        data = {            'username': user.username        }        return {"data": data, "header": header,"msg":"登录成功！"}    @list_route(methods=['POST'])    @Core_connector(transaction=True)    def reset_passwd(self,request,*args,**kwargs):        mobile=self.request.data.get("mobile")        new_passwd=self.request.data.get("new_passwd")        if not new_passwd:            raise PubErrorCustom("新密码为空！")        check_verification_code(self.request.data)        try:            user=Users.objects.get(mobile=mobile)        except Users.DoesNotExist:            raise PubErrorCustom("用户不存在！")        user.passwd = new_passwd        user.save()        return None# class UserDetailsAPIView(viewsets.ViewSet):##     @Core_connector(transaction=True, serializer_class=UsersDetailSerializer, model_class=UserDetail)#     def create(self,request,*args,**kwargs):#         serializer = kwargs.pop('serializer')#         serializer.save()#         return None