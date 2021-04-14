from datetime import datetime

from django.db import models
# 获取用户的字段,就是UserProfile
from django.contrib.auth import get_user_model

from goods.models import Goods
User = get_user_model()


# 用户收藏
class UserFav(models.Model):
    """
    用户收藏
    """
    # 外键用户，所以在数据库表中出现user_id字段
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")

    # 外键商品，所以在数据库表中出现goods_id字段
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name="商品", help_text="商品ID")

    # 添加时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = "用户收藏"
        verbose_name_plural = verbose_name
        # 避免两次收藏，联合唯一索引, 要去映射数据库的功能， 这个其实是数据库帮我们完成的
        # 如果我们收藏保存到数据库里重复了，数据库那就会组我们抛出一个异常
        unique_together = ["user", "goods"]

    def __str__(self):
        return self.user.username


# 用户留言信息
class UserLeavingMessage(models.Model):
    """
    用户留言信息
    """
    MESSAGE_CHOICES = (
        (1, "留言"),
        (2, "投诉"),
        (3, "询问"),
        (4, "售后"),
        (5, "求购"),
    )

    # 用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")

    # 留言类型,有投诉,询问,售后,求购, 留言
    message_type = models.IntegerField(default=1, choices=MESSAGE_CHOICES, verbose_name="留言类型", help_text=u"留言类型: 1(留言), 2(投诉), 3(询问), 4(售后), 5(求购)")

    # 主题
    subject = models.CharField(max_length=100, default="", verbose_name="主题")

    # 内容主体
    message = models.TextField(default="", verbose_name="留言内容", help_text="留言内容")

    # 文件
    file = models.FileField(upload_to="message/images/", verbose_name="上传的文件", help_text="上传的文件")

    # 添加时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用户留言"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.subject


# 用户的收货地址信息
class UserAddress(models.Model):
    """
    用户的收货地址
    """
    # 用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")

    # 省份
    province = models.CharField(max_length=100, default="", verbose_name="省份")

    # 城市
    city = models.CharField(max_length=100, default="", verbose_name="城市")

    # 收货区域
    district = models.CharField(max_length=100, default="", verbose_name="区域")

    # 收货人地址
    address = models.CharField(max_length=100, default="", verbose_name="详细地址")

    # 收货人姓名
    singer_name = models.CharField(max_length=100, default="", verbose_name="签收人")

    # 收货人手机号码
    singer_mobile = models.CharField(max_length=11, default="", verbose_name="电话")

    # 添加时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "收货地址"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.address


















