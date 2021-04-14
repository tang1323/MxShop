from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import UserFav
from .models import UserLeavingMessage, UserAddress
from goods.serializers import GoodsSerializer


# 用户显示收藏商品列表
class UserFavDetailSerializers(serializers.ModelSerializer):
    # 这个是嵌套的Serializer，正好用这个，这个GoodsSerializer是把商品的全部字段拿出来
    # 我们也可以自己重新定义一个Serializer，不把全部字段拿出来
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ["goods", "id"]


# 用户提交收藏序列化数据
class UserFavSerializers(serializers.ModelSerializer):
    # 获取当前用户，这样就知道用户收藏什么商品了，在drf里post过去后在数据库里就能在user_operation_userfav里看到收藏goods_id
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        # 在Models里写避免两次收藏也是可以，在这里写也是可以的
        model = UserFav

        # 这是可以作用于某个字段上的，避免两次收藏，可以自己定义消息
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=['user', 'goods'],
                message="己经收藏该商品"
            )
        ]
        # 如果要添加删除的功能就要在fields里添加"id"
        fields = ["user", "goods", "id"]


# 用户留言序列化
class LeavingMessageSerializer(serializers.ModelSerializer):
    # 获取当前用户，
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # 对时间进行处理，read_only=True只返回不提交，在注册的时候用的也多, format是格式化时间成我们想要的格式
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    class Meta:
        model = UserLeavingMessage

        fields = ["user", "message_type", "subject", "message", "file", "add_time", "id"]


# 用户收货地址数据序列化
class AddressSerializer(serializers.ModelSerializer):
    # 获取当前用户，
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # 对时间进行处理，read_only=True只返回不提交，在注册的时候用的也多, format是格式化时间成我们想要的格式
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    class Meta:
        model = UserAddress

        fields = ["id", "user", "province", "city", "district", "address", "singer_name", "singer_mobile", "add_time"]















