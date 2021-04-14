from datetime import datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import mixins
from django.shortcuts import redirect

from .serializers import ShopCartSerializer, OrderDetailSerializer, ShopCartDetailSerializer, OrderSerializer
from utils.permissions import IsOwnerOrReadOnly
from .models import ShoppingCart, OrderInfo, OrderGoods


# 要用上增删改查，就直接用ModelViewSet，里面己经继承了所有的mixins
class ShoppingCartViewset(viewsets.ModelViewSet):
    """
    购物车功能
    list:
        获取购物车详情
    create:
        加入购物车
    delete:
        删除购物车记录
    update:
        更新购物车记录
    """
    # 序列化收货地址数据
    serializer_class = ShopCartSerializer

    # 权限验证
    # IsAuthenticated一定要登录才能获取
    # IsOwnerOrReadOnly是否当前用户
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # 要看到留言记录，需要带上用户登录后自身的token，这是属于私密数据
    # 一定要加上这个SessionAuthentication才能身份认证成功
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]

    # goods在UserFav是以外键存在的，所以在数据库表user_operations_userfav中出现goods_id
    # 这个加上来是在url中是以goods_id搜索，不再是以id搜索，例如：127.0.0.1/userfavs/10/,这样就能查看详情了
    lookup_field = "goods_id"

    # 库存量的操作：新增商品到购物车，库存数-1
    def perform_create(self, serializer):
        # 购物车
        shop_cart = serializer.save()
        # shop_cart.goods是在ShopCartSerializer/ShoppingCart
        goods = shop_cart.goods
        # goods.goods_num在ShoppingCart/Goods/goods_num
        # 库存数量减1
        goods.goods_num -= shop_cart.nums
        goods.save()

    # 库存量的操作：删除购物车数量，库存数+1
    # 这个方法在ModelViewSet/DestroyModelMixin/
    def perform_destroy(self, instance):
        goods = instance.goods
        goods.goods_num += instance.nums
        goods.save()
        instance.delete()

    # 库存量的操作：在购物车里修改数量，库存数+1也可能 -1
    # 这个方法在ModelViewSet/UpdateModelMixin/
    def perform_update(self, serializer):
        # 先取到之前的数据，然后和现在的数据做一个比对
        # existed_record获取己有的值
        # instance是modelsfrom的一个实例，这里是放在serializer.instance里
        existed_record = ShoppingCart.objects.get(id=serializer.instance.id)

        # 获取之前的值
        existed_nums = existed_record.nums
        # 获取保存之后的值（实时的数据）
        saved_record = serializer.save()

        # 修改后的数量 - 修改前的数量，就得到变化的数量nums，
        nums = saved_record.nums - existed_nums

        # 如果变化的数量是正数，就是说修改后的数量 > 修改前的数量， 这证明我们进行了一个增的操作
        # 如果变化的数量是负数，就是说修改后的数量 < 修改前的数量， 这证明我们进行了一个减的操作
        goods = saved_record.goods
        goods.goods_num -= nums
        goods.save()


    # 这个只返回当前用户帐号的列表
    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    # 动态获取购物车上的商品详情，如果是list
    def get_serializer_class(self):
        if self.action == "list":
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer


# 因为不用修改，所以不用继承ModelViewSet，
# ListModelMixin查看订单列表
# CreateModelMixin创建订单
# DestroyModelMixin删除订单
# mixins.RetrieveModelMixin检索订单或者说是搜索订单商品的详情
class OrderViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    订单管理
    list:
        获取个人订单
    delete:
        删除订单
    create:
        新增订单
    """
    # 序列化收货地址数据
    serializer_class = OrderSerializer

    # 权限验证
    # IsAuthenticated一定要登录才能获取
    # IsOwnerOrReadOnly是否当前用户
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # 要看到留言记录，需要带上用户登录后自身的token，这是属于私密数据
    # 一定要加上这个SessionAuthentication才能身份认证成功
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]

    # 这个只返回当前用户帐号的订单列表
    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    # 动态获取订单里面商品详情，点击订单号进来就是这个
    # retrieve是放在mixins.RetrieveModelMixin中
    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

    # 首先我们获取用户创建订单需求之后， 我们将购物车里的所有信息商品拿出来, 这些信息OrderInfo，现在要把有些数据放到OrderGoods表
    # 第一：拿出来之后来到OrderGoods添加生成!!!!!!!!!!!!!!这个函数主要做这个
    # 记录，意思就是说将我们购物车里的数据添加到OrderGoods
    # 第二，将我们购物车里的记录删除
    # 我们用这个函数，放在CreateModelMixin，数据保存的时候放在order变量里
    def perform_create(self, serializer):
        order = serializer.save()
        # 订单号做好之后，就可以直接调用save, 就拿到order,做后续操作
        # 比如说要生成OrderGoods表，所以说我们要去获取用户当前购物车所有商品
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        # 这样就可以生成我们的OrderGoods表了
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            # 这样我们就能获取到购物车里边的所有商品，将它保存到OrderGoods表
            order_goods.save()

            # 用户购买后清空购物车，这里只支持一次性清空，不像淘宝那样可以选择哪些商品
            # 这里我们delete，shop_cart的时候，也会将OrderGoods表也删除掉
            shop_cart.delete()
        return order


from rest_framework.views import APIView    # 因为我们是跟支付宝相关的，我们是没有models的，可以用最底层的一个view，
from utils.alipay import AliPay
from MxShop.settings import ali_pub_key_path, private_key_path
from rest_framework.response import Response
# 阿里支付的接口
class AlipayView(APIView):
    """
    异步notify_url：通过 POST 请求的形式将支付结果作为参数通知到商户系统。对于 PC 网站支付的交易，在用户支付完成之后，支付宝会根据 API 中商户传入的 notify_url，
    同步return_url: 通过 get请求的形式将部分支付结果作为参数通知到商户系统。对于 PC 网站支付的交易，在用户支付完成之后，支付宝会根据 API 中商户传入的 return_url，
    这个view，即可以处理get，又可以处理post，只需要配置一个url就可以完成支付宝的两种形式的返回
    """
    def get(self, requests):
        """
        处理支付宝的return_url
        :return:
        """
        # 将request.get里的get请求全部拿出来,两者只是post和get的区别
        processed_dict = {}
        for key, value in requests.GET.items():
            processed_dict[key] = value

        # 一定要post出来
        sign = processed_dict.pop("sign", None)

        alipay = AliPay(
            # 沙箱的appid
            appid="2021000117625426",

            # 这个是异步的接口
            # 如果用户只是扫码了，不支付就关闭了页面，这时要去手机帐单里支付，这时候就要一个异步的请求，就是给这个url发一个异步的请求
            # 用户一旦支付了，支付宝会给你发一个notify请求，notify就是异步请求的意思
            # 这个订单己经被支付过了，就要告诉用户去更改订单的一些状态，但是这个url己经跟支付宝产生一个异步的交互了，是不可能在浏览器再访问
            # app_notify_url="http://39.102.98.66:8000/alipay/return/",
            app_notify_url="http://127.0.0.1:8000/alipay/return/",

            # 私钥的相对路径
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            # 如果为True那就是用沙箱环境
            debug=True,  # 默认False,
            # 这是同步的接口
            # return_url="http://39.102.98.66:8000/alipay/return/",
            return_url="http://127.0.0.1:8000/alipay/return/"
        )
        # 这样就对支付宝返回来的数据进行一个验证，verify()
        # verify_re是一个布尔值，如果为True，那就证明返回的数据正常
        verify_re = alipay.verify(processed_dict, sign)

        # 如果为True
        if verify_re is True:
            # out_trade_no是商户唯一订单号，原支付请求的商户订单号。是支付宝的异步响应参数
            order_sn = processed_dict.get("out_trade_no", None)
            # 支付宝交易号。支付宝交易凭证号。
            trade_no = processed_dict.get('trade_no', None)
            # 交易状态。交易目前所处的状态。详情请参见
            trade_status = processed_dict.get('trade_status', None)

            # 查询数据库OrderInfo的记录,用订单号来查询数据库，因为是唯一的
            """不用查询数据库的状态也可以，因为上面己经做了验证了，就是verify()方法"""
            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                # 支付订单的状态
                existed_order.pay_status = trade_status
                # trade_no 在支付宝支付的时候会生成一个交易号
                existed_order.trade_no = trade_no
                # 支付时间
                existed_order.pay_time = datetime.now()
                existed_order.save()

            # 一定要给支付宝发送一个消息，不然这个接口会不停的给支付宝发消息
            # return Response("success")

            # 支付成功后跳 转到首页
            response = redirect("index")
            # 希望我们跳转到这个页面的时候，跳转到vue项目的时候，
            # 如果cookies里面有naxPath, 它直接跳转pay页面，就是支付的页面，后台是无法跳转的
            # 只能让vue帮我们跳，在前端页面的src/router/index.js/329行
            # max_age=2是说两秒钟后过期
            response.set_cookie("nexPath", "pay", max_age=2)
            return response

        # 如果验证失败就直接跳转到首页
        else:
            # 支付失败后跳转到首页
            response = redirect("index")
            return response

    def post(self, requests):
        """
        处理支付宝的notify_url
        :param requests:
        :return:
        """
        # 将request.post里的post请求全部拿出来，两者只是post和get的区别
        processed_dict = {}
        for key, value in requests.POST.items():
            processed_dict[key] = value

        # 一定要post出来
        sign = processed_dict.pop("sign", None)

        alipay = AliPay(
            # 沙箱的appid
            appid="2021000117625426",

            # 这个是异步的接口
            # 如果用户只是扫码了，不支付就关闭了页面，这时要去手机帐单里支付，这时候就要一个异步的请求，就是给这个url发一个异步的请求
            # 用户一旦支付了，支付宝会给你发一个notify请求，notify就是异步请求的意思
            # 这个订单己经被支付过了，就要告诉用户去更改订单的一些状态，但是这个url己经跟支付宝产生一个异步的交互了，是不可能在浏览器再访问
            # app_notify_url="http://39.102.98.66:8000/alipay/return/",
            app_notify_url="http://127.0.0.1:8000/alipay/return/",

            # 私钥的相对路径
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            # 如果为True那就是用沙箱环境
            debug=True,  # 默认False,
            # 这是同步的接口
            # return_url="http://39.102.98.66:8000/alipay/return/",
            return_url="http://127.0.0.1:8000/alipay/return/"
        )
        # 这样就对支付宝返回来的数据进行一个验证，verify()
        # verify_re是一个布尔值，如果为True，那就证明返回的数据正常
        verify_re = alipay.verify(processed_dict, sign)

        # 如果为True
        if verify_re is True:
            # out_trade_no是商户唯一订单号，原支付请求的商户订单号。是支付宝的异步响应参数
            order_sn = processed_dict.get("out_trade_no", None)
            # 支付宝交易号。支付宝交易凭证号。
            trade_no = processed_dict.get('trade_no', None)
            # 交易状态。交易目前所处的状态。详情请参见
            trade_status = processed_dict.get('trade_status', None)

            # 查询数据库OrderInfo的记录,用订单号来查询数据库，因为是唯一的
            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:

                # 结算完成后就计算卖出去的数量，进行+1操作
                # 这里是取OrderGoods中的order，是反向取，因为有一个related_name相关联
                order_goods = existed_order.goods.all()
                for order_good in order_goods:
                    # 获取在OrderGoods里的goods商品
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()

                # 支付订单的状态
                existed_order.pay_status = trade_status
                # trade_no 在支付宝支付的时候会生成一个交易号
                existed_order.trade_no = trade_no
                # 支付时间
                existed_order.pay_time = datetime.now()
                existed_order.save()

            # 一定要给支付宝发送一个消息，不然这个接口会不停的给支付宝发消息
            # return Response("success")

            # 支付成功后跳 转到首页
            response = redirect("index")
            # 希望我们跳转到这个页面的时候，跳转到vue项目的时候，
            # 如果cookies里面有naxPath, 它直接跳转pay页面，就是支付的页面，后台是无法跳转的
            # 只能让vue帮我们跳，在前端页面的src/router/index.js/329行
            # max_age=2是说两秒钟后过期
            response.set_cookie("nexPath", "pay", max_age=2)
            return response

            # 如果验证失败就直接跳转到首页
        else:
            # 支付失败后跳转到首页
            response = redirect("index")
            return response
















