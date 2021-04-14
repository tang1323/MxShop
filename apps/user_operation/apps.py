from django.apps import AppConfig


class UserOperationConfig(AppConfig):
    name = 'user_operation'

    # 在xadmin后台的标题改为中文
    verbose_name = "用户操作管理"

    # 信号量做完之后得加上这个在app.py里面
    def ready(self):
        import user_operation.signals
