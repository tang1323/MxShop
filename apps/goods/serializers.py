"""反序列化到drf成json数据"""
# 主要是为了自动地将models的实例对象序列化，搞成json数据更方便前端使用
from rest_framework import serializers
from django.db.models import Q

from goods.models import Goods, GoodsCategory, HotSearchWords, GoodsImage, Banner
from goods.models import GoodsCategoryBrand, IndexAd


# 商品类别，将Model反序列化出来
class CategorySerializer3(serializers.ModelSerializer):
    """这里是三类目录"""
    class Meta:
        model = GoodsCategory
        # 这个就是把所以的字段序列化出来
        fields = "__all__"


# 商品类别，将Model反序列化出来
class CategorySerializer2(serializers.ModelSerializer):
    # 这个是外键的一个serializers，我们可以嵌套到GoodsSerializer里面做一个展示

    # related_name="sub_cat",这个在models里面定义的parent_category字段里的一个参数
    # parent_category其实是一类的分类，怎么通过一类的分类拿到二类的分类？？那要怎么反过来拿？？？我们直接一类的对象.sub_cat
    # sub_cat要与models里的定义sub_cat得一致的
    # many=True，为什么要加这个，因为这个是二类目录，二类目录下有很多三类目录，所以要加
    sub_cat = CategorySerializer3(many=True)
    """这里是二类目录"""
    class Meta:
        model = GoodsCategory
        # 这个就是把所以的字段序列化出来
        fields = "__all__"


# 商品类别，将Model反序列化出来
class CategorySerializer(serializers.ModelSerializer):
    """这里是一类目录"""
    # 这个是外键的一个serializers，我们可以嵌套到GoodsSerializer里面做一个展示

    # related_name="sub_cat",这个在models里面定义的parent_category字段里的一个参数
    # parent_category其实是一类的分类，怎么通过一类的分类拿到二类的分类？？那要怎么反过来拿？？？我们直接一类的对象.sub_cat
    # sub_cat要与models里的定义sub_cat得一致的
    # many=True，为什么要加这个，因为这个是一类目录，一类目录下有很多二类目录，所以要加
    sub_cat = CategorySerializer2(many=True)

    class Meta:
        model = GoodsCategory
        # 这个就是把所以的字段序列化出来
        fields = "__all__"


# 如何来序列化GoodsImage这个外键的记录呢
# 我们可以做一个嵌套的serializer
class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        # 这是要一个详情页的一个轮播图
        fields = ["image", ]    # 做完这个就可以嵌套到GoodsSerializer


class GoodsSerializer(serializers.ModelSerializer):
    """
    用Serializer需要一个一个添加，代码不精简，也麻烦
    name = serializers.CharField(required=True, max_length=100)
    click_num = serializers.IntegerField(default=0)
    goods_front_image = serializers.ImageField()

    所以有个ModelSerializer， 能一次全部添加进去
    """

    # 我们实例化它就可以了
    category = CategorySerializer()

    # 商品详情页的一个轮播图的
    # images是models下的related_name名称
    # many = True是有多条轮播图，所以等于True
    images = GoodsImageSerializer(many=True)

    class Meta:
        model = Goods
        # 添加进来的它会自己与serializer做一个映射
        # fields = ['name', 'market_price', 'add_time', 'goods_num']

        # 这个就是把所有的字段序列化出来
        fields = "__all__"

    # """现在想把上面的字段或者全部的字段保存到数据库该怎么做
    # 比如前端传过来的json数据，这里要给前端添加商品的接口的话，可以通过serializers来验证，
    # 验证前端传过来的json的body
    # 这里要与views中的post对应，才能上传给数据库
    # """
    # # 我们可以覆盖重载serializers中的create方法
    # # validated_data把上面那些定义的字段放到里面来
    # def create(self, validated_data):
    #     """
    #     Create and return a new `Snippet` instance, given the validated data.
    #     """
    #     # Goods是models里面的，objects是models的管理器，objects里面有个函数create
    #     return Goods.objects.create(**validated_data)


# 搜索框
class HotWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotSearchWords
        fields = "__all__"


# 轮播图数据序列化
class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


# 品牌序列化
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


# 首页商品的分类数据序列化
class IndexCategorySerializer(serializers.ModelSerializer):
    # 嵌套BrandSerializer，many=True就是一个category就有多个brand
    brands = BrandSerializer(many=True)

    # 这样取不行，因为我们取商品的时候是直接取最小类目的商品，而这里有一级二级三级类目
    # 而这样取是取出第一级类目的，比如：生鲜食品。但是我们要取的是第三级商品内容
    # goods = GoodsSerializer()

    # 给某个字段生成一个url界面，在drf官方文档下的Serializer fields/SerializerMethodField
    # read_only=True不能是用户提交，是服务器生成返回的
    # 这里我们就是取的第三级的商品的内容
    goods = serializers.SerializerMethodField()

    # 二级类目，一级类目有很多个二级类目，就是一对多，所以用上many=True
    sub_cat = CategorySerializer2(many=True)

    # 首页商品广告位的数据
    ad_goods = serializers.SerializerMethodField()

    def get_ad_goods(self, obj):
        goods_json = {}
        # 取出models下的IndexAd的数据
        ad_goods = IndexAd.objects.filter(category_id=obj.id, )
        if ad_goods:
            good_ins = ad_goods[0].goods
            # 拿到这个商品之后做序列化
            # context={'request': self.context['request']}是在商品图片上加上域名，这里不是view，不会自动加上给你，所以这是一个细节
            # goods_json是一个serializer实例
            goods_json = GoodsSerializer(good_ins, many=False, context={'request': self.context['request']}).data

        # 只有加上.data才是json数据
        return goods_json

    # 这个函数的命名规则是 get_加字段名goods
    def get_goods(self, obj):
        # 通过obj.id拿到第一级类目的id，然后我们就通过这些id取出第三级类目
        # 这个category(类目)要从models里找, 这个parent_category是从models里找的，就是父的, 这里是两个下划线，最后一个是从两个父的上面查找
        all_goods = Goods.objects.filter(Q(category_id=obj.id)|Q(category__parent_category_id=obj.id)|Q(category__parent_category__parent_category_id=obj.id))

        # 拿数据后做一个序列化， context={'request': self.context['request']}是在商品图片上加上域名，这里不是view，不会自动加上给你，所以这是一个细节
        # many=True, 是指一对多就等于True
        # goods_serializer是一个serializer对象
        goods_serializer = GoodsSerializer(all_goods, many=True, context={'request': self.context['request']})

        # 只有加上.data才是json数据
        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = "__all__"






























