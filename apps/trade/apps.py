from django.apps import AppConfig


class TradeConfig(AppConfig):
    name = 'trade'

    # 在xadmin后台的标题改为中文
    verbose_name = "交易管理"
