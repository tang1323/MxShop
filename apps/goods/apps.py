from django.apps import AppConfig


class GoodsConfig(AppConfig):
    name = 'goods'

    # 在xadmin后台的标题改为中文
    verbose_name = "商品"



