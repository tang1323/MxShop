from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    # 在xadmin后台的标题改为中文
    verbose_name = "用户管理"

    # 信号量做完之后得加上这个在app.py里面
    def ready(self):
        import users.signals
