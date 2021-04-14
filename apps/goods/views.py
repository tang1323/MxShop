
# from rest_framework.views import APIView
# from rest_framework import status   # 这是drf定义的一些状态码
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from rest_framework import filters  # 这是drf的filters
from rest_framework.pagination import PageNumberPagination    # 分页的包

# 这是最重要的一个views, 我们后边api人去尽量用这个viewsets来完成,更加简便，好用
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend   # 这是drf过滤器的包
from rest_framework.authentication import TokenAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_extensions.cache.mixins import CacheResponseMixin   # github上的drf扩展，功能有很多，这里用的是缓存
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle    # 这是对api进行限速的，比如爬虫
"""
这里是写django的djangorestframework的views
我们来看一下djangorestframework的views给我们提供的cbv(class base views)
让我们可以简单的快速的完成商品列表页的返回
"""
# 这个.是这个goods目录之下的这个models
from .models import Goods, GoodsCategory, HotSearchWords, Banner
from .filters import GoodsFilter    # 商品过滤器
from .serializers import GoodsSerializer, CategorySerializer, HotWordSerializer, BannerSerializer    # 商品序列化
from .serializers import IndexCategorySerializer


# 分页序列化的数据，深度定制化这个配置
class GoodsPagination(PageNumberPagination):
    # 这一页有多少个
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = "page"  # 这个是分页url最后面的一个名称，也就是页数p=2，这个要和前端的vue保持一致
    # 单页最大有几个
    max_page_size = 100

"""继承关系
GenericViewSet(viewset)     -drf
    GenericAPIView          -drf    # 继承了APIView，加了一些过滤功能，和分页以及serializer序列化
       APIView              -drf
            View            -django 
            
drf里面有很重要的概念:mixin-->这个文件放在site-packages/rest-framework/mixin
mixin里面有一些函数
    CreateModelMixin # 创建数据
    ListModelMixin  # 因为在views里一定要继承get方法，而get与list要进行绑定，也有过滤，有分页功能
    UpdateModelMixin    # 是部分更新还是全部更新
    RetrieveModelMixin  # 我们要获取商品的具体信息，检索 
    DestroyModelMixin   # 是一些状态码连接功能，删除
    
    
viewsets里面函数都是pass，因为是要在urls中用router.register来绑定'get': 'list',
当然也可以自己用动态
# goods_list = GoodsListViewSet.as_view({
#     'get': 'list',
# })
来绑定
"""


# CacheResponseMixin要放在第一个，这是一个缓存，哪个接口需要设置自己去加（个人数据就不建议加缓存，公共数据和未登录的数据就可以加缓存）
# GenericViewSet定制了as_views方法，可以在urls中get与list做一个绑定
# viewsets里面什么都没有做，让我们在urls中自己做router.register(r'goods', GoodsListViewSet)
# 让register自己绑定关系，也可以用'get': 'list',来绑定
# 公开数据不用token，不登录也是能访问的，用全局的TokenAuthentication就必须要登录才能访问，所以不能用全局的TokenAuthentication
# 或者说在这里的数据本身就要用户登录的情况下才能访问，就在这里写authentication_classes = [TokenAuthentication, ]
# 我们要获取某个商品的详情用：mixins.RetrieveModelMixin，只要使用了这个就能获取商品的详情页面
class GoodsListViewSet(CacheResponseMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品列表页，分页，搜索，过滤，排序
    """
    #
    # 这是对api进行限速的，比如爬虫
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = Goods.objects.all().order_by('id')

    # 将数据序列化
    serializer_class = GoodsSerializer

    # 这是序列化的分页
    pagination_class = GoodsPagination

    # 如果一定要是登录后才能看到的数据，就可以加入在这里，把TokenAuthentication，JSONWebTokenAuthentication加到这里来
    # 这是登录认证模式，在settings中设置的是全局模式
    # authentication_classes = [TokenAuthentication, ]
    # authentication_classes = [JSONWebTokenAuthentication, ]

    # 这个是过滤器加进来的,       filters.SearchFilter是搜索过滤器, filters.OrderingFilter是排序
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # 这个就是要在过滤器进行过滤的字段，但是有点不好的是，这个是要精确搜索才行，
    # 在实际中是要模糊搜索和区间搜索
    # 在github上搜索django_filter, 这个就能满足我们
    # filterset_fields = ['name', 'shop_price']
    """这个就是django_filter，在filters文件上，这里我们配置进来"""
    filter_class = GoodsFilter

    # filters.SearchFilter上面己经把这个搜索加进来了，这里是添加哪些字段进行搜索
    # ^是以什么开头的, =就是精确过滤， @就是全文的搜索， $就是正则来搜索
    search_fields = ['name', "goods_brief", 'goods_desc']

    # filters.OrderingFilter上面己经把这个排序加进来， 这里是添加哪些字段进行一个排序，比如说销量
    # 这个也应用于前端的排序， 这里是销量和价格的排序
    ordering_fields = ['sold_num', 'shop_price']

    # 这个函数是RetrieveModelMixin里的，重载加入我们的逻辑，这样也可以，信号量也可以
    # 点击数加1， 点击数和收藏数都用信号量来做，delete和save操作可以信号量signals来做
    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     # 修改商品的点击数量
    #     instance.click_num += 1
    #     instance.save()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)


# 这三种方法。这个ListAPIView在site-packages下的rest_framework下的generics.py,
# 里面还有很多简单的函数调用，这样我们就不用每次都写get方法了，
# 我们直接继承ListAPIView就行，因为它只！！！帮我们做了get方法
# class GoodsListView(generics.ListAPIView):
#     """
#     商品列表页
#     """
#     queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer
#     # 这是序列化的分页
#     pagination_class = GoodsPagination


# 这是第二种写法，generics.GenericAPIView是用的相当多的view，里面分页什么的都有，里面继承的是APIView
# class GoodsListView(mixins.ListModelMixin, generics.GenericAPIView):
#     """
#     商品列表页
#     """
#     queryset = Goods.objects.all()[:10]
#     serializer_class = GoodsSerializer
#
#     # 一定要重载get这个函数，或者是post请求，不然是返回不了数据的get是拉，post是推
#     def get(self, request, *args, **kwargs):
#         # 这个self.list是在ListModelMixin里边，里面做了分页，将数据序列化
#         return self.list(request, *args, **kwargs)


# 这是第一种写法。我们不用APIView来做，用更上一层的GenericAPIView来做
# class GoodsListView(APIView):
#     """
#     List all goods.
#     """
#     def get(self, request, format=None):
#         goods = Goods.objects.all()[:10]
#         #  many=True如果是一个列表就要配置上， 然后它就把它序列化成一个数组对象
#         # GoodsSerializer是在serializers下的，可以自己定义字段
#         goods_serializer = GoodsSerializer(goods, many=True)
#         return Response(goods_serializer.data)

    # """这个其实跟django中的form是一致的，
    # 就是在post的时候，把serializer换成我们的form
    # """
    # # 这是接收前端传递过来的json数据,然后保存到我们的数据库当中
    # # request这个是drf包封装过来的（也对response进行了封装），不是django的
    # def post(self, request, format=None):
    #     # 在django中是没有.data，这个request.data其实是drf封装的,
    #     # 不管你是get 还是post还是在body的数据它都会取出来 放在data里面
    #     serializer = GoodsSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         # 保存前端传过来的json数据成功则返回一个201的post请求，说明正确
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 类别序列化
# 我们要获取它的商品列表用：mixins.ListModelMixin
class CategoryViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
    商品分类列表数据
    retrieve:
    获取商品分类详情
    """
    # 类别序列化
    # 我们要获取它的商品列表用：mixins.ListModelMixin
    # 我们要获取某个商品的详情用：mixins.RetrieveModelMixin，获取详情就是获取这一类的所有数据了
    # 而在restful api中，要获取详情就得在urls加上一个id，具体看urls，因为drf己经帮我们做了id，所以非常的方便
    # 在教育网站那里，我们是这样是我们的课程的某个详情：url(r'^(?P<pk>[0-9+])/$',)，但是我现在不用这么写了，因为drf己经帮我们做了
    # 我们只要在这里加上mixins.RetrieveModelMixin,就行了，什么都不用做

    # 获取它的分类出来, 这个只拿一级类目出来，所以得用filter(category_type=1)
    queryset = GoodsCategory.objects.filter(category_type=1)
    # 商品分类列表数据
    serializer_class = CategorySerializer


class HotSearchsViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取热搜词列表
    """
    queryset = HotSearchWords.objects.all().order_by("-index")
    serializer_class = HotWordSerializer


# 首页轮播图
class BannerViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取轮播图列表
    """
    queryset = Banner.objects.all().order_by("index")
    serializer_class = BannerSerializer


# 首页商品分类数据
class IndexCategoryViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    首页商品分类数据
    """
    # is_tab是否导航,拿导航的商品出来就行了
    # name__in是只取后台添加这个类目的数据
    queryset = GoodsCategory.objects.filter(is_tab=True, name__in=["生鲜食品", "酒水饮料"])
    # 序列化后的数据
    serializer_class = IndexCategorySerializer

























