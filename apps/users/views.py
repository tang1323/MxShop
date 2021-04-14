from django.shortcuts import render

# Create your views here.
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin  # 这是短信发送要用的，要对表进行操作，实际是创建的过程
from rest_framework import mixins   # 重载mixins.RetrieveModelMixin，正好满足获取某个用户信息的详情
from rest_framework import viewsets     # 这是短信注册模块
from rest_framework.response import Response
from rest_framework import status
from random import choice
from rest_framework import permissions
from rest_framework import authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

# 这是接收刚刚用户注册后的token，而这些方法在jwt中的serializers中
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

from users.serializers import SmsSerializer, UserRegSerialize, UserDetailSerializer      # 这是手机检测是否合法之类的
from MxShop.settings import APIKEY  # 云片网的apikey
from utils.yunpian import YunPian   # 云片网的发送接口逻辑
from users.models import VerifyCode

# 返回此项目的用户模型（model）,这是内置的
User = get_user_model()


# 通过手机和用户名登录认证模块，加入到settings中的AUTHENTICATION_BACKENDS
class CustomBackend(ModelBackend):
    """
    自定义用户验证
    """
    # 这里的password是前端传过来的，是明文的
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 在这里就能找到我们的手机mobile，通过手机号也能登录
            # 只通过username和mobile才能找到User
            user = User.objects.get(Q(username=username)|Q(mobile=username))
            # 在这里的check_password是django的password，在这里经过是加密的了
            if user.check_password(password):
                return user
        except Exception as e:
            return None


# 短信发送注册，在users下的models定义了一个VerifyCode，这个模块实际是要对这个表进行操作
class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):
    """发送短信验证码"""
    # 用户传过来的手机我们要做验证，1：比如是否合法的手机，2：是否注册过
    # serializer实际上django里的form和models_form是一样的，所以这个验证是放在users下的serializer来做
    # 在定义serializers好了SmsSerializer之后就能写我们和views了
    serializer_class = SmsSerializer

    # 生成我们的验证码
    def generate_code(self):
        """生成6位数字的验证码"""
        # 这是一个种子，什么是种子，就是从这里面随机拿自己想要的数字出来
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))

        # 因为这里边是数组，我们要join成字符串
        return "".join(random_str)

    # 这里我重载create
    def create(self, request, *args, **kwargs):
        # 这一句是拿到了这个SmsSerializer
        serializer = self.get_serializer(data=request.data)
        # is_valid就是检查值是否正确，raise_exception=True是什么意思，就是如果这个值有错误，那就直接抛出异常了，就不会进入下面那三句的逻辑了
        # 那设置raise_exception=True有什么好处，如果is_valid抛出异常，那就会drf捕获到，给我们前端返回一个400的状态
        serializer.is_valid(raise_exception=True)

        # 从users/serializers模块中获取过来的mobile，因为上面的is_valid己经验过mobile了，能跑到这一步，那证明这里能直接拿出来了
        mobile = serializer.validated_data["mobile"]

        # 经过上面的users/serializers模块合法性，还有is_valid的验证，那就可以通过云片网发送了
        yun_pian = YunPian(APIKEY)
        code = self.generate_code()
        # 在utils/yunpian中返回re_dict，这里用sms_status接着这些状态
        sms_status = yun_pian.send_sms(code=code, mobile=mobile)

        # 云片网的官方文档有返回一些参数，我们拿这些参数做判断，比如官方说code返回为0就等于成功
        if sms_status["code"] != 0:
            return Response({
                # 如果不成功,其实我们是通过status返回的状态码来判断是否成功，
                "mobile": sms_status["msg"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 如果成功，那就保存到数据库中,记得是成功才能保存到数据中
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            # 如果成功,其实我们是通过status返回的状态码来判断是否成功，
            return Response({
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)


class UserViewset(CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    # 重载mixins.RetrieveModelMixin，正好满足获取某个用户信息的详情
    """
    restful api说过：url是对资源的操作
    那注册的资源是我们的用户，我们就理解为post一个用户到后台数据库里边
    所以我们就是对user操作
    因为是post的数据到后台数据库，那就用CreateModelMixin，顾名思议，就是创建
    用户
    """
    # 先去serializers里写我们的UserSerialize()
    # 定义好了之后，我们再来做views
    serializer_class = UserRegSerialize
    queryset = User.objects.all()   # 要继承这些的时候必须要用queryset来做，注册功能基本完成
    # 配置这两个模式，是不需要用户输入密码的，这样在浏览器里能方便的调试，它是要在浏览器里添加session或者在headers里面添加token
    authentication_classes = [JSONWebTokenAuthentication, authentication.SessionAuthentication]

    # 不管用户是get还是post还是del，必须是登录的，这里是权限验证
    # 设置这个如果用户想要注册也要登录才能注册，显然不合理，去GenericViewSet里研究源码
    # permission_classes = [permissions.IsAuthenticated, ]

    # 重载这个函数，这个函数就能返回我们定义的serializer_class
    # 这个函数在GenericViewSet/GenericAPIView/get_serializer_class()
    def get_serializer_class(self):
        """
        动态获取serializer
        retrieve检索
        create创建注册
        :return:
        """
        # 想要使用动态获取serializer，self.action,只有使用了viewsets才能用，使用APIView是没有这个好处的
        if self.action == "retrieve":
            # 如果是检索的话，那就用获取用户详情的serializer
            return UserDetailSerializer
        elif self.action == "create":
            # 否则的话用这个serializer
            return UserRegSerialize

        return UserDetailSerializer

    # 重载这个函数, 它会遍历permission_classes，返回一个permission实例，放在一个数组里边
    # 这个函数在GenericViewSet/GenericAPIView/APIView/get_permissions()
    def get_permissions(self):
        """
        动态获取permissions(权限)
        :return:
        """
        # 想要使用动态获取permissions(权限)self.action,只有使用了viewsets才能用，使用APIView是没有这个好处的
        if self.action == "retrieve":   # 这个retrieve是RetrieveModelMixin里的一个函数
            return [permissions.IsAuthenticated()]
        elif self.action == "create":   # 这个create是CreateModelMixin里的一个函数
            return []

        # 其他情况一定要返回空，这个一定要写，不然就容易出错
        return []

    # 重点！！！！后期自己想添加任何东西都可以自己添加进来，这个函数很重要！！！！！
    # 如果用户注册完了之后我们帮用户登录的话，那就要把jwt的token返回到前端，这里就是要把jwt_token返回前端去
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 注意这里的perform_create，它没有返回User对象，所以要重载它
        user = self.perform_create(serializer)

        # 而token返回是返回serializer.data中，里面就有token, 我们取出来
        re_dict = serializer.data

        # 得User对象后，把User进行一个处理
        payload = jwt_payload_handler(user)

        # 而token返回是返回serializer.data中，里面就有token, 我们取出来
        # 这个token名和name名要和前端保持一致
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username
        # 这样前端就可以拿到这些字段保存到cookies中，这样我们就完成数据token的定制化
        # 重点！！！！后期自己想添加任何东西都可以自己添加进来，这个函数很重要！！！！！

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    # 获取当前用户，必须是登录的状态
    def get_object(self):
        return self.request.user

    # 因为我们刚刚注册用户的时候必须要拿到User对象，这个对象在UserRegSerialize中的model = User
    def perform_create(self, serializer):
        """
        这里返回的是  UserRegSerialize 下的model = User对象
        class Meta:
            model = User
        """
        # 在源码里是没有return的
        return serializer.save()











