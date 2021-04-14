"""这是在drf上的过滤器"""
import django_filters
from django.db.models import Q


from .models import Goods


class GoodsFilter(django_filters.rest_framework.FilterSet):
    """
    商品的过滤类
    """
    # 商品在商店的一个价格，gte这是最小值小于等于
    # 这里要与前端的list/list.js下的pricemin，pricemax要保持一致
    # //这两个价格都要和前端保持一致
    pricemin = django_filters.NumberFilter(field_name="shop_price", help_text="最低价格", lookup_expr="gt")
    # lte这是最大值大于等于
    pricemax = django_filters.NumberFilter(field_name="shop_price", help_text="最高价格", lookup_expr="lt")

    # 这是标题栏的一级分类要获取以下的二级分类再获取所有商品的一个方法
    # 这里要与前端的list/list.js下的top_category要保持一致
    # 外键就是一个NumberFilter,里面传递一个函数
    top_category = django_filters.NumberFilter(method='top_category_filter')

    # 这里会默认传递一些默认的参数进来， 我们需要将这些写进来
    def top_category_filter(self, queryset, name, value):
        """这里我们要做一个让标题栏的一级分类能够获取我们的二级分类下的商品"""
        """这里如果category的id等于我们这里传进来的value，说明这个商品就是我们的一级类目
            如果是二级类目，我们直接找这个父的category, 它的id和这个相等就对了
            如果是三级类目，我们就直接找这个父的category，再找父的category，它的id和这个相等就对了
            这三个任意满足一个我们就返回回来了
            所以这里做一个or的关系，用django里的Q！！！！
        """
        # 这个category要从models里找, 这个parent_category是从models里找的，就是父的, 这里是两个下划线，最后一个是从两个父的上面查找
        return queryset.filter(Q(category_id=value)|Q(category__parent_category_id=value)|Q(category__parent_category__parent_category_id=value))

    # icontains加了i是忽略大小写，不加lookup_expr="icontains"就是精确搜索
    name = django_filters.CharFilter(field_name="name", help_text="搜索商品名称", lookup_expr="icontains")

    class Meta:
        model = Goods
        # 要显示的字段
        fields = ["pricemin", "pricemax", 'name', "is_hot", "is_new"]


















