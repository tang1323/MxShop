from datetime import datetime

from django.db import models

# 获取用户的字段,就是UserProfile
from django.contrib.auth import get_user_model
from goods.models import Goods

# 返回此项目的用户模型（model）,这是内置的
User = get_user_model()


# 购物车
class ShoppingCart(models.Model):
    """
    购物车
    """
    # 用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u"用户")

    # 商品
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name=u"商品")

    # 商品数量
    nums = models.IntegerField(default=0, verbose_name="购买数量")

    # 添加时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "购物车"
        verbose_name_plural = verbose_name
        # 避免两次添加商品到订单里，只是在商品基础上的数量加1，联合唯一索引, 要去映射数据库的功能， 这个其实是数据库帮我们完成的
        # 如果我们收藏保存到数据库里重复了，数据库那就会组我们抛出一个异常
        unique_together = ["user", "goods"]

    def __str__(self):
        return "%s(%d)".format(self.goods.name, self.nums)


# 订单
class OrderInfo(models.Model):
    """
    订单
    """
    ORDER_STATUS = {
        ("TRADE_SUCCESS", "成功"),
        ("TRADE_CLOSED", "超时关闭"),
        ("WAIT_BUYER_PAY", "交易创建"),
        ("TRADE_FINISHED", "交易结束"),
        ("paying", "待支付"),
    }
    # PAY_TYPE = {
    #     ("alipay", "支付宝"),
    #     ("wechat", "微信")
    # }

    # 用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u"用户")

    # 订单编号，
    order_sn = models.CharField(max_length=30, null=True, blank=True, unique=True, verbose_name="订单号")

    # 在支付宝支付的时候会生成一个交易号
    trade_no = models.CharField(max_length=100, null=True, blank=True, verbose_name=u"交易号")

    # 支付订单的状态
    pay_status = models.CharField(choices=ORDER_STATUS, default="paying", max_length=30, null=True, blank=True, verbose_name="订单状态")

    # 订单留言
    post_script = models.CharField(max_length=200, null=True, blank=True, default="", verbose_name="订单留言")

    # 订单金额
    order_mount = models.FloatField(default=0.0, verbose_name="订单金额")

    # 支付时间
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")

    # 用户信息
    # 收货地址，这里为什么不指向一个外键呢，而是将这些值取出来保存在这些订单里边呢
    """
    比如说如果我们现在设置一个外键指向我们的订单，
    然后用户如果去修改了个人中心里面的一些资料，然后我们后台再看的时候，
    实际上就会发现这个订单的地址，实际上已经变了，
    对吧？为了防止这些出问题，
    对吧？所以说我们在最开始的时候让用户填写到这个订单的时候，我们就将她当时填写的这些状态，
    把它保存下来，这样的话，用户再去修理个人中心订单的资料的时候，他就不会影响到这里点，
    对吧，因为我们以后再查订单，比如说我值钱订购某个商品的时候，我想查一下，
    当时我填写的地址是什么的时候？如果我们只一个外界的话，用户去将这个外界的资料修改了，
    然后这边用户都不知道，当时自己提交订单的时候，当时的一个配送地址是什么？
    对吧？所以说这里边我们把这个字段给她提取出来，保存到我们的OrderInfo本身的信息里边，
    对吧，这是一个，然后这些知道跟这里边这段实际上是一样的，我把它提取出来就行了"""
    address = models.CharField(max_length=100, default="", verbose_name="收货地址")

    # 签收人名字
    singer_name = models.CharField(max_length=20, default="", verbose_name="签收人")

    # 签收人的手机号码
    singer_mobile = models.CharField(max_length=11, verbose_name="联系电话")

    # 添加时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = u'订单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.order_sn)


# 订单的商品详情
class OrderGoods(models.Model):
    """
    一个商品可以买多个,所以是一对多的关系
    订单的商品详情
    """
    # 订单, 设置related_name="goods"，是因为在OrderDetailSerializer里的model = OrderInfo，
    # 而我们是要获取订单详情，而这里的order是与OrderInfo相关联的，所以related_name="goods"
    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, verbose_name="订单信息", related_name="goods")

    # 商品的一个外键
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name="商品")

    # 商品的数量
    goods_num = models.IntegerField(default=0, verbose_name="商品数量")

    # 添加时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "订单商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.order.order_sn)















