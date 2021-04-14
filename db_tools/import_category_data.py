

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
from goods.models import GoodsCategory

# all_category = GoodsCategory.objects.all()


from db_tools.data.category_data import row_data

# 循环遍历商品的级别    这个category_data文件的目录
for lev1_cat in row_data:
    lev1_intance = GoodsCategory()
    lev1_intance.code = lev1_cat['code']
    lev1_intance.name = lev1_cat['name']
    # 这个是第一级目录
    lev1_intance.category_type = 1
    lev1_intance.save()

    for lev2_cat in lev1_cat["sub_categorys"]:
        lev2_intance = GoodsCategory()
        lev2_intance.code = lev2_cat['code']
        lev2_intance.name = lev2_cat['name']
        # 这个是第二级目录
        lev2_intance.category_type = 2
        # 它的父类是谁
        lev2_intance.parent_category = lev1_intance
        lev2_intance.save()

        for lev3_cat in lev2_cat["sub_categorys"]:
            lev3_intance = GoodsCategory()
            lev3_intance.code = lev3_cat['code']
            lev3_intance.name = lev3_cat['name']
            # 这个是第三级目录
            lev3_intance.category_type = 3
            # 它的父类是谁
            lev3_intance.parent_category = lev2_intance
            lev3_intance.save()


















