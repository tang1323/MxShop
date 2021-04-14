from datetime import datetime

from django.db import models
from DjangoUeditor.models import UEditorField


# 商品类别
class GoodsCategory(models.Model):
    """
    商品类别
    """
    # 一个models完成所有级别的商品类型,就是有三种级别或者更多
    CATEGORY_TYPE = (
        (1, "一级类目"),
        (2, "二级类目"),
        (3, "三级类目"),
    )

    # 商品名称
    name = models.CharField(default="", max_length=30, verbose_name="类别名", help_text="类别名")

    # 编码,就是name的英文的类型等等
    code = models.CharField(default="", max_length=30, verbose_name="类别code", help_text="类别code")

    # 简单描述
    desc = models.TextField(default="", verbose_name="类别描述", help_text="类别描述")

    # 品牌类型, 什么级别的类, 比如一级,二级, 三级, 用choices
    category_type = models.IntegerField(choices=CATEGORY_TYPE, verbose_name="类目级别", help_text="类目级别")

    # 父类的品牌, 自己指向自己用self
    parent_category = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, verbose_name="父类目级别", help_text="父目录", related_name="sub_cat")

    # 因为首页的全部商品类别下的商品和生鲜食品,酒水饮料都是来自同一张表的
    is_tab = models.BooleanField(default=False, verbose_name="是否导航", help_text="是否导航")

    # 添加时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "商品类别"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 一对多的关系,就设计一个外键关系
# 品牌名
class GoodsCategoryBrand(models.Model):
    """
    品牌名
    """
    # related_name是反向取比较方便，就是通过GoodsCategory反向取这个字段category
    category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, related_name='brands', null=True, blank=True, verbose_name="商品类目")

    # 品牌名称
    name = models.CharField(default="", max_length=30, verbose_name="品牌名", help_text="品牌名")

    # 品牌的简单描述
    desc = models.TextField(default="", max_length=200, verbose_name="品牌描述", help_text="品牌描述")

    # 大类就是一级类下有多个商家的图片,所以是一个一对多的关系
    image = models.ImageField(max_length=200, upload_to="brand/")

    # 添加时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "品牌"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 商品
class Goods(models.Model):
    """
    商品
    """
    # 类别， 这是一个外键
    category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name="商品类目")

    # 商品编码
    goods_sn = models.CharField(max_length=50, default="", verbose_name="商品唯一货号")

    # 商品名称
    name = models.CharField(max_length=100,  verbose_name="商品名")

    # 商品点击数
    click_num = models.IntegerField(default=0, verbose_name="点击数")

    # 卖出的数量
    sold_num = models.IntegerField(default=0, verbose_name="商品销售量")

    # 商品的收藏数
    fav_num = models.IntegerField(default=0, verbose_name="收藏数")

    # 商品的库存的数量
    goods_num = models.IntegerField(default=0, verbose_name="库存数")

    # 商品的市场的价格
    market_price = models.FloatField(default=0, verbose_name="市场价格")

    # 商品在商店的价格
    shop_price = models.FloatField(default=0, verbose_name="本店价格")

    # 商品的简介
    goods_brief = models.TextField(max_length=500, verbose_name="商品简短描述")

    # 商品的副文本介绍, 导入DjangoUeditor第三方包, 放在extra_apps
    goods_desc = UEditorField(verbose_name=u"内容", imagePath="goods/images/", width=1000, height=300, filePath="goods/files/", default='')

    # 此商品为免运费商品，计算配送金额时将不计入配送费用
    # 是否有上面这个字段
    ship_free = models.BooleanField(default=True, verbose_name="是否承担运费")

    # 商品的封面图片
    goods_front_image = models.ImageField(upload_to="goods/images/", null=True, blank=True, verbose_name="封面图")

    # 哪一些商品的新品
    is_new = models.BooleanField(default=False, verbose_name="是否新品")

    # 点进到商品详情页面的右下有热卖商品,那怎么知道哪些是热卖的商品???
    is_hot = models.BooleanField(default=False, verbose_name="是否热销")

    # 添加时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class IndexAd(models.Model):
    """首页的一级类目的广告"""
    # related_name是反向取比较方便，就是通过GoodsCategory反向取这个字段category
    category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, related_name='category', verbose_name="商品类目")

    # related_name是反向取比较方便，就是通过Goods反向取这个字段goods
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='goods')

    class Meta:
        verbose_name = '首页商品类别广告'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name


# 商品详情页面的轮播品, 是有很多张,是一对多的关系
# 所以必须要建立一张表如何来序列化这个外键的记录呢
# 这是一个外键，
class GoodsImage(models.Model):
    """
    商品轮播图
    """
    # 它是我们的一个外键, 指向我们的Goods
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name="商品", related_name="images")

    # 图片
    image = models.ImageField(upload_to="", verbose_name="图片", null=True, blank=True)

    # 添加时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "商品图片"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name


# 首页的轮播商品
class Banner(models.Model):
    """
    因为首页的商品的轮播图会有拉伸,所以这里单独做一个表
    首页的轮播商品
    """
    # 这是一个外键,指向Goods
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name="商品")

    image = models.ImageField(upload_to='banner', verbose_name="轮播图片")

    # 图片轮播的一个顺序,要保持一个顺序
    index = models.IntegerField(default=0, verbose_name="轮播顺序")

    # 添加时间
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "轮播商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name


# 热搜词
class HotSearchWords(models.Model):
    """
    热搜词
    """
    keywords = models.CharField(default="", max_length=20, verbose_name="热搜词")
    index = models.IntegerField(default=0, verbose_name="排序")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = '热搜词'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.keywords























