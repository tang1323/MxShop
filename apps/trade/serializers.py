from rest_framework import serializers

from goods.models import Goods
from .models import ShoppingCart, OrderInfo, OrderGoods
from goods.serializers import GoodsSerializer
from utils.alipay import AliPay
from MxShop.settings import private_key_path, ali_pub_key_path


# 动态获取商品详情放在购物车上
class ShopCartDetailSerializer(serializers.ModelSerializer):
    # 内嵌套一个，在ShoppingCart里也有一个goods是一个外键，这里又有一个，所以要加上many=False
    goods = GoodsSerializer(many=False)

    class Meta:
        model = ShoppingCart
        # 把在ShoppingCart的字段全部返回到前端
        fields = "__all__"


# 这里我们继承的是Serializer
# 而点击进来在BaseSerializer有个update()方法，必须重载它，但是在Serializer继承BaseSerializer没有重载update()，所以抛出异常
# 而ModelSerializer己经重载过，所以不会抛异常
class ShopCartSerializer(serializers.Serializer):
    # 获取当前用户，这样就知道用户收藏什么商品了，在drf里post过去后在数据库里就能在user_operation_userfav里看到收藏goods_id
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    # 对models上的字段进行设置
    # error_messages 是一些错误提示
    # required=True是必填的字段
    nums = serializers.IntegerField(required=True, label="数量", min_value=1,
                                    error_messages={
                                        "min_value": "商品数量不能小于1",
                                        "required": "请选择购买数量"
                                    })
    # 这个serializers有没有外键字段呢，在models里可以知道是一个外键
    # 这个字段是属于外键的关系型，得到django-rest-framework官方文档下的Serializer relations里找到
    # 在这个类里我们继承的是Serializer,不是ModelSerializer，所以要加上queryset这个参数
    # required=True是必填的字段
    goods = serializers.PrimaryKeyRelatedField(queryset=Goods.objects.all(), required=True, label="商品")

    # 就必须重载这个create方法了，这个类用的Serializer实际上是和我们的django上的form是一样的
    def create(self, validated_data):
        """
        用户创建
        就是用户把商品加入购物车
        :param validated_data:
        :return:
        """
        # 加入购购车，他是有两种状态的，对吧？
        # 第一购物车本身是没有这条记录的？第二他本身是有这条记录的，
        # 所以说这里边就判断他这个记录是否存不存在，
        # 但是在获取了之前，我们必须要拿到这里的数据吧，就是nums，goods一些字段的数据
        # 我们在调这个create方法，这个validated_data，这里边每个字段变量己经做过validated_data处理过后的数据了，比如数据类型转换
        # 在serializers里还有一个initial_data，这个initial_data是调用validated_data之前没有处理过的数据
        # initial_data初始数据

        # 获取当前用户
        # 在view里面能(user=self.request.user)这样获取用户，但在serializers就不能这样
        # 而用户是放在context里边
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]

        # 查询下有没有这些字段数据
        existed = ShoppingCart.objects.filter(user=user, goods=goods)

        # 如果有这些数据，那就获取第一条数据, 然后加1
        if existed:
            # 先获取第一条数据
            existed = existed[0]
            # 再如果商品己经存在，那就加1
            existed.nums += nums
            existed.save()
        else:
            # 如果之前没有这个商品在购物车，那就创建一条数据在购物车上
            # existed是返回的结果，这个我们要做反序列化交给前端的
            existed = ShoppingCart.objects.create(**validated_data)
        return existed

    # 这个类继承的是Serializer，而在Serializer没有重载BaseSerializer里的update()方法
    # 所以要在这里重载一下
    def update(self, instance, validated_data):
        # 修改商品数量
        instance.nums = validated_data["nums"]
        instance.save()
        return instance


# 序列化OrderGoods订单的商品详情
class OrderGoodsSerializer(serializers.ModelSerializer):
    # 内嵌套一个，在OrderGoods里也有一个goods是一个外键，这里又有一个，所以要加上
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = "__all__"


# 订单商品详情,这个类是反序列化OrderGoodsSerializer
class OrderDetailSerializer(serializers.ModelSerializer):
    # many=True，为什么要加这个，因为这个是一类目录，一类目录下有很多二类目录，所以要加
    goods = OrderGoodsSerializer(many=True)

    # 在个人中心的订单详情里也有"立即用支付宝支付"的按钮,所以这里也加入以下语句
    # 给某个字段生成一个url界面，在drf官方文档下的Serializer fields/SerializerMethodField
    # read_only=True不能是用户提交，是服务器生成返回的
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # 这个函数是规则是get_加上字段名alipay_url, obj就是serializers对象
    def get_alipay_url(self, obj):
        """这里面就可以生成支付宝的一个url"""
        alipay = AliPay(
            # 沙箱的appid
            appid="2021000117625426",

            # app_notify_url="http://39.102.98.66:8000/alipay/return/",
            app_notify_url="http://127.0.0.1:8000/alipay/return/",

            # 私钥的相对路径
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            # 如果为True那就是用沙箱环境
            debug=True,  # 默认False,
            # 这是同步的接口
            # return_url="http://39.102.98.66:8000/alipay/return/",
            return_url = "http://127.0.0.1:8000/alipay/return/"
        )

        url = alipay.direct_pay(
            subject=obj.order_sn,
            # 订单号
            out_trade_no=obj.order_sn,
            # 要支付多少钱
            total_amount=obj.order_mount,
            # 这个就是用户支付后要跳转的页面
            # return_url="http://39.102.98.66:8000/"

        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
        return re_url

    class Meta:
        model = OrderInfo
        fields = "__all__"


# 订单管理
class OrderSerializer(serializers.ModelSerializer):

    # 获取当前用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # read_only订单状态只能读不能写（post）
    pay_status = serializers.CharField(read_only=True)

    # 在支付宝支付的时候会生成一个交易号只能读不能写（post）
    trade_no = serializers.CharField(read_only=True)

    # 订单号只能读不能写（post）
    order_sn = serializers.CharField(read_only=True)

    # 支付时间只能读不能写（post）
    pay_time = serializers.DateTimeField(read_only=True)

    # 给某个字段生成一个url界面，在drf官方文档下的Serializer fields/SerializerMethodField
    # read_only=True不能是用户提交，是服务器生成返回的
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # 这个函数是规则是get_加上字段名alipay_url, obj就是serializers对象
    def get_alipay_url(self, obj):
        """这里面就可以生成支付宝的一个url"""
        alipay = AliPay(
            # 沙箱的appid
            appid="2021000117625426",

            # app_notify_url="http://39.102.98.66:8000/alipay/return/",
            app_notify_url="http://127.0.0.1:8000/alipay/return/",

            # 私钥的相对路径
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            # 如果为True那就是用沙箱环境
            debug=True,  # 默认False,
            # 这是同步的接口
            # return_url="http://39.102.98.66:8000/alipay/return/",
            return_url="http://127.0.0.1:8000/alipay/return/"
        )

        url = alipay.direct_pay(
            subject=obj.order_sn,
            # 订单号
            out_trade_no=obj.order_sn,
            # 要支付多少钱
            total_amount=obj.order_mount,
            # 这个就是用户支付后要跳转的页面
            # return_url="http://39.102.98.66:8000/"

        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
        return re_url


    # 我们要生成独一无二的订单号
    def generate_order_sn(self):
        # 当前时间+userid+随机数
        import time
        from random import Random
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context["request"].user.id, ranstr=random_ins.randint(10, 99))
        return order_sn

    # 把订单号拿过来验证
    def validate(self, attrs):
        attrs["order_sn"] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"



"""
第10章16节
它直接关系到我们后边到底采用哪种部署方式，
如果大家采用讲稿来代理页面的方式的话，就一定要认真，接下来讲的每一个步骤

vue有两种开发模式
第一种是：cnpm run dev
第二种是：cnpm run build
    # 这样就生成静态文件，这个就放在templaets文件中就可以访问
    # 会生成html,js以及我们的一些资源文件，生成放在dist文件目录下的
"""








