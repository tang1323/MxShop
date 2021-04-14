
# 独立使用django的models
import sys
import os


# 获取(就是这个文件脚本)当前的文件路径
pwd = os.path.dirname(os.path.realpath(__file__))

# 整个项目的根目录加入python根搜索路径之下
# MxShop的这个文件
sys.path.append(pwd+"../")

# 会自动找到settings的配置，因为models会依赖一些设置文件的
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MxShop.settings')

import django
django.setup()


# 这句话要放在这里，因为前面要初始化django的一些配置
from goods.models import Goods, GoodsCategory, GoodsImage

from db_tools.data.product_data import row_data


# 循环商品详情进来
for goods_detail in row_data:
    goods = Goods()
    goods.name = goods_detail["name"]
    goods.market_price = float(int(goods_detail["market_price"].replace("￥", "").replace("元", "")))
    goods.shop_price = float(int(goods_detail["sale_price"].replace("￥", "").replace("元", "")))

    # 商品简介, 如果没有简介，那就是空字符串
    goods.goods_brief = goods_detail["desc"] if goods_detail["desc"] is not None else ""

    # 副文本描述
    goods.goods_desc = goods_detail["goods_desc"] if goods_detail["goods_desc"] is not None else ""

    # 图片,如果没有图片，那就是个空字符串，这里也是可以的，因为后台是保存成字符串
    goods.goods_front_image = goods_detail["images"][0] if goods_detail["images"] else ""

    # 类别,取倒数第一个
    category_name = goods_detail["categorys"][-1]

    """
    这里为什么不用get，而是用filter
    如果filter没有数据的话，会返回一个空的数组
    如果用的是get，会有两种情况， 如果没有数据或者是查到了两条数据的话，
    那就会抛异常，得用try包住才能运行
    """
    category = GoodsCategory.objects.filter(name=category_name)
    if category:
        goods.category = category[0]
    goods.save()

    # 因为图片是轮播图，我们之前也在goods中modes定义了一个GoodsImage
    # 所以得弄一个循环
    for goods_image in goods_detail["images"]:
        goods_image_instance = GoodsImage()
        # 对象的图片
        goods_image_instance.image = goods_image
        # 对象的商品
        goods_image_instance.goods = goods
        goods_image_instance.save()












