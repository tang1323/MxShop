from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

# 返回此项目的用户模型（model）,这是内置的
User = get_user_model()


# 这是一个装饰器，而sender就是接收哪个models传递过来的
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):      # created=False是不是新建的用户
    # 新创建用户的时候才能对密码加密
    if created:
        password = instance.password
        # instance翻译过来就是实例，而instance就是我们的User,里面有一个set_password方法，专门对密码加密的
        instance.set_password(password)
        # 做完信号量以后得到app.py里做一个def ready(self): import users.signals
        instance.save()

        # 因为我们用民jwt。所以不再用token
        # Token.objects.create(user=instance)


"""
使用django自己内置的 Model signals信号,它会自己发送
如果设置其它的信号，就要自己去发送，再接收
"""









