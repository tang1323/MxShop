
# 这里是写django的views
# 这是django最底层的views，也是最常用的
from django.views.generic.base import View
# 还有一种ListView，也是可以的，但我们还是用最底层的view
# from django.views.generic import ListView
from goods.models import Goods


class GoodsListView(View):
    def get(self, request):
        """
        通过django的view实现商品列表页
        :param request:
        :return:
        """
        json_list = []
        # 取出所有的商品,goods是一个对象
        goods = Goods.objects.all()[:10]

        # 用这个方式取会有很多问题，比如取add_time，json.dumps中的datetime是做不了时间类型的序列化
        # for good in goods:
        #     json_dict = {}
        #     # 取出商品的名字
        #     json_dict["name"] = good.name
        #     # 商品的类别
        #     json_dict["category"] = good.category.name
        #     # 商品的市场价格
        #     json_dict["market_price"] = good.market_price
        #     # 商品在商店的价格
        #     json_dict["shop_price"] = good.shop_price
        #     # 商品编码
        #     json_dict["goods_sn"] = good.goods_sn
        #     json_list.append(json_dict)

        """
        上面一个一个写太麻烦
        from django.forms.models import model_to_dict
        用这个一次性取出所有字段
        ImageFieldFile is not JSON serializable
        ImageField不能做序列化
        """
        # from django.forms.models import model_to_dict
        # for good in goods:
        #     json_dict = model_to_dict(good)
        #     json_list.append(json_dict)

        """
        用serializers.serialize这个做序列化
        一般我们做api接口的时候或者json返回的时候我们都用JsonResponse
        """
        import json
        from django.core import serializers
        json_data = serializers.serialize("json", goods)
        # json.loads和json.dumps是相反的操作，这里把它注释掉，那return就不用json.dumps(json_data)了
        # 但是这里我们用的是JsonResponse，它源码里有json.dumps，所以我们这里放开
        json_data = json.loads(json_data)   # loads字符串变成列表或者字典

        # 这里我们用JsonResponse，因为在源码里面有json.dumps和content_type="application/json"， 这样代码更加简洁
        from django.http import JsonResponse
        return JsonResponse(json_data, safe=False)

        # 如果要返回json，我们用的HttpResponse，是必须要返回这个content_type="application/json"
        # from django.http import HttpResponse
        # return HttpResponse(json_data, content_type="application/json")






















