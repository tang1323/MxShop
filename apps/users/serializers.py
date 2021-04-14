import re
from rest_framework import serializers
# 获取用户的字段,就是UserProfile
from django.contrib.auth import get_user_model
from datetime import datetime
from datetime import timedelta
from rest_framework.validators import UniqueValidator
from users.models import VerifyCode  # 用来查询验证码是否到了一分钟，一分钟后才能再发送

from MxShop.settings import REGEX_MOBILE    # 手机是否合法，正则表达式

# 返回此项目的用户模型（model）,这是内置的
User = get_user_model()


# 还有一个ModelSerializer，为什么不用呢
# 因为在users/VerifyCode的code是必填字段，而之前前端是没有传递过来到这里
# 我们只需要把手机传到数据库做检查就行，所以用Serializer
class SmsSerializer(serializers.Serializer):
    # 自定义一个手机字段
    mobile = serializers.CharField(max_length=11)

    # 验证moblie，重载这个函数,validate与字段拼接成一个函数名称
    def validate_mobile(self, mobile):
        """
        验证手机号码
        :param data:
        :return:
        """
        # 手机是否注册，我们查询一下UserProfile数据表，看一下这个用户是否存在，导入User = get_user_model()
        # count()就是大于0的话
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户己经存在")

        # 验证手机号码是否合法，放在settings中
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码非法")

        # 验证码发送频率, timedelta就是设置时间间隔，当前时间一分钟，就是有了一分钟
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        # 有了一分钟的时间one_mintes_ago， 我们就能查询记录了
        # __gtd大于一分钟的时间one_mintes_ago，验证码己经进入数据库的时间必须大于当前时间间隔（一分钟后）
        # 如果等于小于一分钟，那就进入逻辑
        # .count()如果有这么一条数据存在了，那就证明己经发送过验证码了
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, mobile=mobile).count():
            raise serializers.ValidationError("距离上一次发送未超过60s")

        # 如果验证通过一定要返回去
        return mobile


class UserDetailSerializer(serializers.ModelSerializer):
    """
    返回用户详情序列化类
    这样我们想要序列化哪一个字段就都可以，在fields中写入相要序列化的字段
    """
    class Meta:
        model = User
        fields = ["name", "gender", "birthday", "email", "mobile"]


# 上面的SmsSerializer说过为什么不用ModelSerializer
# 那在这里的注册页面也有个code(验证码)，为什么这里就能用ModelSerializer
# 其实是有技巧的，我们可以用技巧来突破这里的限制，以后我们就能随机应变了
# 这样我们就能享受到ModelSerializer给我们带来的好处
class UserRegSerialize(serializers.ModelSerializer):
    """手机注册页面的字段序列化"""
    # 验证码在UserProfile中没有，所以在这里重新定义一个, required=True是必填的字段
    # 这是不会保存到数据库中的，在下面我们会del删除掉，help_text="验证码"在drf登录调试页面的框框下面就有验证码这3个字
    # label="验证码"是框框左边的一个友好中文提示，而不再是code
    # write_only=True是序列化的时候不再返回前端做序列化了，这样它就不会出错，所以这个字段有没有都无所谓了，因为我们在下面己经del attrs["code"]
    # error_messages 是一些错误提示
    code = serializers.CharField(required=True, write_only=True, max_length=6, min_length=6, label="验证码",
                                 error_messages={
                                     # 比如用户不填这个字段，就显示请输入验证码,required是针对这个code字段都没有才有效，直接写它会把code带过去，所以要加"blank":"请输入验证码"
                                     "required": "请输入验证码",
                                     "blank": "请输入验证码",

                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误",
                                 },
                                 help_text="验证码")

    # 我们也要验证username是否存在，所以建一个字段
    # 假设用户己经用这个用户名（手机号码）刚刚发送过验证码，则发完验证码，用户又改用户名（手机号码）
    # 这时候我们用validators=[UniqueValidator]来做，验证是否唯一，如果己经存在：message="用户己经存在"
    """
    还有是他里边的一个验证，就是我们post回去之后他回来的个格式是什么？
    他首先会用serializers来验证， 然后验证的时候，他的一个返回是比如说这个username这个字段出错了，
    他告诉你这个错误是什么？比如说code的这个字段出错了，它会告诉你code字段出错了 
    对吧，大家想一想，如果我们这里边这两个字段都没有错，而是他们两个联合起来就错了呢，
    大家试想一下，如果是联合出错了呢？实际上，它会返回另外一个字段，这个我们后面会介绍大家
    """
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户己经存在")])

    # 密码做一个密文的处理，write_only=True就是不把密码返回前端，如果返回前端容易给人截获
    password = serializers.CharField(
        style={'input_type': 'password'}, label="密码", help_text="密码", write_only=True,
    )

    # # 重载create函数，在ModelSerializer也有这个函数
    # def create(self, validated_data):
    #     # 调用创建成功之后是能取到user的
    #     user = super(UserRegSerialize, self).create(validated_data=validated_data)
    #     # user是我们django继承的对象，就是AbstractUser类，
    #     # AbstractUser类里有一个set_password()函数，专门对密码加密的，这样在数据库就是加密的一段密码了，而且是不能反解的
    #     user.set_password(validated_data["password"])
    #     user.save()
    #     """也就是说重载了create函数，对密码进行加密作用，用的是AbstractUser类里的set_password"""
    #     return user
    # 这里的密码加密我们用django的信号量来做，放在signals.py文件里做，百度django post_save(),然后在drf文档里找到Authentication，搜索post_save()

    # 验证code，重载这个函数,validate与字段拼接成一个函数名称,验证验证码是否正解
    # 验证码有几种出错的可能
    def validate_code(self, code):
        """
        这里为什么不用get呢
        因为要捕获两种错误：第一种如果用户连续发了3次验证码，中间的两次验证码恰好相等
        还有一个是用户两边不匹配的时候，说不存在这条记录的
        如果用的是filter，没有数据的话，那就返回一个空数组，而且处理验证码过期等问题也是比较麻烦的
        :param code:
        :return:
        """
        # try:
        #     verify_records = VerifyCode.objects.get(mobile=self.initial_data["username"])
        # except VerifyCode.DoesNotExist as e:
        #     pass
        # except VerifyCode.MultipleObjectsReturned as e:
        #     pass

        # 先看看有没有这个验证码,从VerifyCode先找到这个手机号码是否一致,
        # self.initial_data用户post过来的值都是在initial_data里边，mobile也在里边,在这个项目，username等价mobile
        # order_by("-add_time")做一个排序，从最新的时间先查询
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        # 如果有这个手机
        if verify_records:
            # 如果存在这个手机，那就是最后一条
            last_records = verify_records[0]

            # 验证码发送频率, timedelta就是设置时间间隔，当前时间间隔5分钟，这样我们就获取到了5分钟前的时间了
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)

            """这里注意，我们先验证验证码是否过期，再验证传过来的对不对"""
            # 如果数据库的手机号码的时间段大于5分钟时间了，那就是过期了
            if five_mintes_ago > last_records.add_time:
                raise serializers.ValidationError("验证码过期")

            # 如果传过来的验证码不等于你传过来的验证码
            if last_records.code != code:
                raise serializers.ValidationError("验证码错误")

            # 如果返回，那就是要存到数据库中了，这里没必要存
            # return code

        # 否则手机传过来的验证码就是不正确
        else:
            raise serializers.ValidationError("验证码错误")

    # 作用于所有字段之上， 在这里我们做一个全盘的设计，其他的validate_you执行后，会返回所有的字段到attrs中，我们再执行这个函数做处理
    # attrs是validate_code()，包括所有的validate_you(), 返回总的所有字段的date
    def validate(self, attrs):
        # 我们不需要前端传递mobile过来，这里我们在attrs中新加一个mobile
        attrs["mobile"] = attrs["username"]

        # 然后把验证码给删除了，响应上面的code字段，这里删除了
        del attrs["code"]
        return attrs

    class Meta:
        model = User

        # 这里的字段要看注册页面有哪些字段，但是为什么有个username呢，因为这里我们用的是UserProfile，而UserProfile是继承django自带的User
        # 所以这里的username是必填字段,一定要写到这里来，而code在UserProfile是没有这个字段的，所以要在这个函数里重新加一个code的字段

        # 我们在定义user/models的时候，mobile是必填的
        # 在注册的时候，我们这个网站是不要你填用户名的，所以注册的时候手机号码就是用户名
        # 所以我们在user/models里把mobile设置为可以为空的，null=True, blank=True,这样写，将它传的来的username自动放在mobile里
        # 为什么user/mobile设置成可以为空呢，是因为我们这里设置必填字段的话，然后在这里验证的时候
        # 用户不post mobile过来，然后这里做serializers的is_valid时候,会抛异常，说mobile是必填的
        # 现在这个字段mobile我们通过后端自己控制进来，所以不能在做is_valid的时候让它给验证了
        # 而好的习惯是将username和mobile都post进来数据库
        fields = ["username", "code", "mobile", "password"]     # 在drf的登录调试页面里有这3个字段，mobile不是必填的（因为我们改过）















