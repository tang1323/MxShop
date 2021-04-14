from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


# 用户的一些字段设计
class UserProfile(AbstractUser):
    """
    用户的一些字段设计
    """
    # 姓名
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")

    # 生日
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")

    # 现在如果是必填字段用户如果不post mobile过来，然后这里做serializers的is_valid时候,会抛异常
    # 手机，null=True, blank=True,是不必填的，当然不建议这样做，我们在这里这样做只是为了更好展示serializers
    # 我们建议前端也有个username，而不是和这个用户名和mobile是一样的进来数据库
    mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="电话")

    # 性别
    gender = models.CharField(max_length=6, choices=(("male", u"男"), ("female", "女")), default="female", verbose_name="性别")

    # 邮箱
    email = models.CharField(max_length=100, null=True, blank=True, verbose_name="邮箱")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


# 短信验证码写在数据库
class VerifyCode(models.Model):
    """
    短信验证码写在数据库
    """
    # 验证码
    code = models.CharField(max_length=10, verbose_name="验证码")

    # 手机号码
    mobile = models.CharField(max_length=11, verbose_name="电话")

    # 添加时间是什么时候的
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间 ")

    class Meta:
        verbose_name = "短信验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code




















