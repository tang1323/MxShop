from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from user_operation.models import UserFav

"""点击数和收藏数都用信号量来做，delete和save操作可以信号量signals来做
想要使用信号量，就在app里添加一些操作"""


# 这是一个装饰器，而sender就是接收哪个models传递过来的
@receiver(post_save, sender=UserFav)
def create_userfav(sender, instance=None, created=False, **kwargs):      # created=False是不是新建的用户
    # 新创建用户的时候才能对密码加密
    if created:
        # 收藏数量加1，点击数和收藏数都用信号量来做，delete和save操作可以信号量signals来做
        # 这个instance.goods是UserFavSerializers/UserFav里的goods
        goods = instance.goods
        # 收藏数加1
        goods.fav_num += 1
        goods.save()


@receiver(post_delete, sender=UserFav)
def delete_usefav(sender, instance=None, created=False, **kwargs):      # created=False是不是新建的用户
    # 新创建用户的时候才能对密码加密
    # 收藏数量减1，点击数和收藏数都用信号量来做，delete和save操作可以信号量signals来做
    # 这个instance.goods是UserFavSerializers/UserFav里的goods
    goods = instance.goods
    # 收藏数加1
    goods.fav_num -= 1
    goods.save()
"""
使用django自己内置的 Model signals信号,它会自己发送
如果设置其它的信号，就要自己去发送，再接收
"""









