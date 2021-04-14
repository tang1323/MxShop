"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
import xadmin
from MxShop.settings import MEDIA_ROOT
from django.views.static import serve
# 引入官方文档
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter        # 有这个routers配置更加简单
from rest_framework.authtoken import views       # 获取token的url
from rest_framework_jwt.views import obtain_jwt_token   # jwt的认证接口

# from goods.views_base import GoodsListView     # 这个是试验
from goods.views import GoodsListViewSet, CategoryViewset, HotSearchsViewset, BannerViewset
from goods.views import IndexCategoryViewset
from users.views import SmsCodeViewset, UserViewset    # 短信验证
from user_operation.views import UserFavViewset, LeavingMessageViewset, AddressViewset         # 用户收藏,用户留言,# 收货地址
from trade.views import ShoppingCartViewset, OrderViewset      # 用户加入购物车


# 随着后面系统的url越来越多，这个就更加方便好用
router = DefaultRouter()

# 配置goods的url
router.register(r'goods', GoodsListViewSet, basename="goods")

# 验证码的urls
router.register(r'code', SmsCodeViewset, basename="code")

# 配置category的url
router.register(r'categorys', CategoryViewset, basename="categorys")

# 注册页面
router.register(r'users', UserViewset, basename="users")

# 搜索框
router.register(r'hotsearchs', HotSearchsViewset, basename="hotsearchs")

# 用户收藏
router.register(r'userfavs', UserFavViewset, basename="userfavs")

# 用户留言
router.register(r'messages', LeavingMessageViewset, basename="messages")

# 收货地址
router.register(r'address', AddressViewset, basename="address")

# 购物车url
router.register(r'shopcarts', ShoppingCartViewset, basename="shopcarts")

# 订单相关url
router.register(r'orders', OrderViewset, basename="orders")

# 轮播图url
router.register(r'banners', BannerViewset, basename="banners")

# 首页商品系列数据url
router.register(r'indexgoods', IndexCategoryViewset, basename="indexgoods")

"""
这个己经用router替代，它register里面己经帮我们做了get与list一些配置，更加简单
如果想自己来绑定也可以
"""
# Goods的
# 原本要在views里要做，这个self.list是在ListModelMixin里边，里面做了分页，将数据序列化
# return self.list(request, *args, **kwargs)
# 但是这里通过as_view直接get与list做一个绑定
# goods_list = GoodsListViewSet.as_view({
#     'get': 'list',
# })
from trade.views import AlipayView
from django.views.generic import TemplateView
urlpatterns = [
       url(r'^xadmin/', xadmin.site.urls),
       url(r'^admin/', admin.site.urls),

       # 这是drf登录的url,在后边调试api的时候会用到
       url('api-auth/', include('rest_framework.urls')),

       # 后台xadmin中的图片显示
       url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),

       # 商品的列表页面，己经用下边的替代
       # url(r'goods/$', goods_list, name="goods-list"),

       url(r'^', include(router.urls)),

       # 用户支付后要跳转到index页面，就是首页，是用cnpm run build来生成的，但是是放在django代理的
       url(r'^index/', TemplateView.as_view(template_name="index.html"), name='index'),

       # 这实际就是生成drf的自动文档的配置，记得把docs/$中的$去掉！！！
       url(r'docs/', include_docs_urls(title="慕学生鲜")),

       # 这是获取token的一个url，drf自带的token认证模式
       url('api-token-auth/', views.obtain_auth_token),

       # jwt的认证接口
       url(r'^login/', obtain_jwt_token),

       # 支付宝的return_url与notify_url
       url(r'^alipay/return/', AlipayView.as_view(), name="alipay"),
]

















