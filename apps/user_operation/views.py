from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated      # 权限验证，谁登录了就获取谁的收藏记录
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication


from .models import UserFav, UserLeavingMessage, UserAddress
from .serializers import UserFavSerializers, UserFavDetailSerializers, AddressSerializer, LeavingMessageSerializer
from utils.permissions import IsOwnerOrReadOnly     # 加入这个，我们删除的时候就会验证权限的问题


# 用户收藏
# mixins.CreateModelMixin是收藏商品,因为是post的数据到后台数据库
# mixins.DestroyModelMixin是取消收藏商品
# mixins.ListModelMixin是获取商品收藏列表
# mixins.RetrieveModelMixin检索模型混合
# GenericViewSet定制了as_views方法，可以在urls中get与list做一个绑定
# viewsets里面什么都没有做，让我们在urls中自己做router.register(r'goods', GoodsListViewSet)
# 想要使用动态获取permissions(权限)，动态获取serializer，self.action,只有使用了viewsets才能用，使用APIView是没有这个好处的
class UserFavViewset(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    用户收藏功能
    list:
        获取用户收藏列表
    retrieve:
        判断某个商品是否己经收藏
    create:
        收藏商品
    """
    # 拿出所有的收藏记录，是不合理的，合理的只能获取当前用户UserFav才对
    # queryset = UserFav.objects.all()

    # 序列化收藏这个数据
    serializer_class = UserFavSerializers

    # 权限验证
    # IsAuthenticated一定要登录才能获取
    # IsOwnerOrReadOnly是否当前用户
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # 要看到收藏记录，需要带上用户登录后自身的token，这是属于私密数据
    # 一定要加上这个SessionAuthentication才能身份认证成功
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]

    # goods在UserFav是以外键存在的，所以在数据库表user_operations_userfav中出现goods_id
    # 这个加上来是在url中是以goods_id搜索，不再是以id搜索，例如：127.0.0.1/userfavs/10/
    lookup_field = "goods_id"

    # 合理的只能获取当前用户UserFav才对，所认重载这个方法
    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)

    # 这个函数在CreateModelMixin，重载它，这样也可以，信号量也可以
    # 收藏数量加1，点击数和收藏数都用信号量来做，delete和save操作可以信号量signals来做
    # def perform_create(self, serializer):
    #     instance = serializer.save()
    #
    #     # 这个instance.goods是UserFavSerializers/UserFav里的goods
    #     goods = instance.goods
    #     # 收藏数加1
    #     goods.fav_num += 1
    #     goods.save()

    # 这是用户收藏商品列表
    def get_serializer_class(self):
        """
        动态获取serializer
        retrieve检索
        create创建注册
        :return:
        """
        # 想要使用动态获取permissions(权限)，动态获取serializer，self.action,只有使用了viewsets才能用，使用APIView是没有这个好处的
        if self.action == "list":
            # 如果是检索的话，那就用获取用户详情的serializer
            return UserFavDetailSerializers
        elif self.action == "create":
            # 否则的话用这个serializer
            return UserFavSerializers

        return UserFavSerializers


# mixins.ListModelMixin是获取用户留言列表
# mixins.DestroyModelMixin删除用户留言功能
# mixins.CreateModelMixin添加用户留言功能
# viewsets.GenericViewSet定制了as_views方法，可以在urls中get与list做一个绑定
# viewsets里面什么都没有做，让我们在urls中自己做router.register(r'goods', GoodsListViewSet)
# 想要使用动态获取permissions(权限)，动态获取serializer，self.action,只有使用了viewsets才能用，使用APIView是没有这个好处的
class LeavingMessageViewset(mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取用户留言
    create:
        添加留言
    delete:
        删除留言功能
    """
    # 序列化留言数据
    serializer_class =  LeavingMessageSerializer

    # 权限验证
    # IsAuthenticated一定要登录才能获取
    # IsOwnerOrReadOnly是否当前用户
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # 要看到留言记录，需要带上用户登录后自身的token，这是属于私密数据
    # 一定要加上这个SessionAuthentication才能身份认证成功
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]

    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


# 用户收货地址功能
# mixins.ListModelMixin列表功能
# mixins.CreateModelMixin添加功能
# mixins.UpdateModelMixin更新功能
# mixins.DestroyModelMixin删除功能
# viewsets.GenericViewSet定制了as_views方法，可以在urls中get与list做一个绑定
# viewsets里面什么都没有做，让我们在urls中自己做router.register(r'goods', GoodsListViewSet)
# 想要使用动态获取permissions(权限)，动态获取serializer，self.action,只有使用了viewsets才能用，使用APIView是没有这个好处的
# class AddressViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
#     """
#     有一个Model己经继承了增删改查功能，所以用viewsets.ModelViewSet
#     """

class AddressViewset(viewsets.ModelViewSet):
    """
    收货地址管理
    list:
        获取收货地址
    create:
        添加收货地址
    update:
        更新收货地址
    delete:
        删除收货地址
    """
    # 序列化收货地址数据
    serializer_class = AddressSerializer

    # 权限验证
    # IsAuthenticated一定要登录才能获取
    # IsOwnerOrReadOnly是否当前用户
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # 要看到留言记录，需要带上用户登录后自身的token，这是属于私密数据
    # 一定要加上这个SessionAuthentication才能身份认证成功
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)











