# pip install pycryptodome
__author__ = 'bobby'

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes

import json


class AliPay(object):
    """
    支付宝支付接口
    """
    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        # 参数的初始化
        # 沙箱appid
        self.appid = appid
        self.app_notify_url = app_notify_url

        # 这是私钥文件路径
        self.app_private_key_path = app_private_key_path

        # 上面读文件，然后生成一个app_private_key接收
        self.app_private_key = None
        self.return_url = return_url

        # 读app_private_key_path这个文件，私钥
        with open(self.app_private_key_path) as fp:
            # importKey实例交给app_private_key
            self.app_private_key = RSA.importKey(fp.read())

        # 公钥，但是要去验证支付宝返回给我们的消息的时候，是最主要 的key
        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            # importKey实例交给alipay_public_key
            self.alipay_public_key = RSA.import_key(fp.read())

        # 如果debug为True那就是沙箱
        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            # 否则是支付己经上线的应用
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        # 这是电脑网站支付产品介绍(统一收单下单并支付页面接口)
        # 里的请求参数，必填字段
        biz_content = {
            # 商品标题/交易标题/订单标题/订单关键字等。
            # 注意：不可使用特殊字符，如 /，=，& 等。	例如：Iphone6 16G
            "subject": subject,
            # 订单号
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }
        # 这一句是因为biz_content里有很多参数，所以要用可变参数更新**kwargs
        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        # 有了data这些参数，那就进行签名sign_data
        return self.sign_data(data)

    def build_body(self, method, biz_content, return_url=None):
        data = {
            # 支付宝分配给开发者的应用ID
            "app_id": self.appid,
            # 接口名称
            "method": method,
            # 请求使用的编码格式，如utf-8,gbk,gb2312等
            "charset": "utf-8",
            # 商户生成签名字符串所使用的签名算法类型，目前支持RSA2和RSA，推荐使用RSA2
            "sign_type": "RSA2",
            # 发送请求的时间，格式"yyyy-MM-dd
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # 调用的接口版本，固定为：1.0
            "version": "1.0",
            # 请求参数biz_content是放在公共请求参数中，所以是一个嵌套的关系
            "biz_content": biz_content
        }
        # 一开始是return_url是为空的，如果不为空，那就放到data字典里
        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    # 这个签名非学的关键，几乎所以的支付宝的接口都有签名
    def sign_data(self, data):
        # 在上面的data参数里不能有sign，在这里pop进去
        data.pop("sign", None)

        # 排序后的字符串，ordered_data是排序的方法,app_id,biz_content,按字母首个字符来排序
        unsigned_items = self.ordered_data(data)

        # 生成签名的时候不要做预处理
        # 拼接成这样的格式：参数=参数值&参数=参数值&参数=参数值
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)

        # 开始签名
        sign = self.sign(unsigned_string.encode("utf-8"))
        # ordered_items = self.ordered_data(data)也是排序，重复了

        # 未处理的url：https://excashier.alipaydev.com/standard/auth.htm?payOrderId=https://.....
        # 用quote_plus做了一个预处理，例己经处理后的：https://excashier.alipaydev.com/standard/auth.htm?payOrderId=3d9ea3306fa949d99a2becdb1ebc6bba.00
        # 参数后还加了https://....这样的字符，容易出问题，所以用quote_plus方法转换成字符串
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)

        # 获得最终的订单信息字符串，还加上sign
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    # 一定要排序,很关键，不然会出错
    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        # sorted内置函数，形成一个元组tuple
        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        # 这个是私钥，在这里制作sign参数，用私钥来做
        key = self.app_private_key
        # 用PKCS1_v1_5来做，signer就是签名的对象
        signer = PKCS1_v1_5.new(key)
        # 调用的是SHA256这个算法
        signature = signer.sign(SHA256.new(unsigned_string))

        # 支付宝官方说必须要base64 编码，转换为unicode表示并移除回车
        # encodebytes之后是bye的类型，要用decode转换成utf8类型字符串，然后回车换行符去掉
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        # 这个就是签名的字符串
        return sign

    # signature就是支付宝返回sign
    def _verify(self, raw_content, signature):
        # 开始计算签名
        # 这个是公钥
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        # raw_content就是排序之后的字符串
        digest.update(raw_content.encode("utf8"))
        # 自己生成的digest，和传过来的sign做一个对比，如果是正确的，那就返回一个true
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    # 为了有人防止对支付的url进行攻击，修改订单状态，比如假装己经支付成功
    # 根据支付宝返回的数据进行验证，验证过程是与生成的过程刚好是反过来的过程
    # # signature就是支付宝返回sign
    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串，就是首个字母的排序
        unsigned_items = self.ordered_data(data)

        # 签名
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        # signature就是支付宝返回sign
        return self._verify(message, signature)


if __name__ == "__main__":

    # 根据url里的参数，也就是回跳参数，其实跟我们上面的参数一样，
    # 取到这些参数之后，我们再拿公钥进行签名，进行与这个url对比就行了
    # 这个url是支付成功后的url
    return_url = "http://39.102.98.66:8000/?charset=utf-8&out_trade_no=202102021122&method=alipay.trade.page.pay.return&total_amount=99.00&sign=XnPJZMB0sCssGodum%2B2JmwXsJwHMxZbnrDIYeiobsMAbOvDH3m2JOEpj0l%2BoTRE6%2Fzbq0%2BwxNAzwy%2BcRSTkZPKhPiW%2Bz45Es5HygAAizBMNpVrx7fLHfBdrmR%2BaMJiMIb9C9Yi7tFSNWqmYLXn4lK1dCbXN0DBRjsQcMhM%2FMWNAGv6B6Bx87mDwPvgkAKmXN133dkchjIYAWvtExgssVq4JmSjzzPvz2efALolHQKFRpf3RKK2QbiHeE0i%2BYuwPPVTADzxdFC9XO38qWBR1rhJ4clneMTbeL%2Bl%2BQLgIS4Rbna4yTCyOnWdJFuN3z8DtJqGZJFX2Zsg%2FIzYfwBSVyzA%3D%3D&trade_no=2021032122001404140510424593&auth_app_id=2021000117625426&version=1.0&app_id=2021000117625426&sign_type=RSA2&seller_id=2088621955430191&timestamp=2021-03-21+10%3A42%3A35"
    alipay = AliPay(
        # 沙箱的appid
        appid="2021000117625426",


        # 这个是异步的接口
        # 如果用户只是扫码了，不支付就关闭了页面，这时要去手机帐单里支付，这时候就要一个异步的请求，就是给这个url发一个异步的请求
        # 用户一旦支付了，支付宝会给你发一个notify请求，notify就是异步请求的意思
        # 这个订单己经被支付过了，就要告诉用户去更改订单的一些状态，但是这个url己经跟支付宝产生一个异步的交互了，是不可能在浏览器再访问
        app_notify_url="http://39.102.98.66:8000/alipay/return/",


        # 私钥的相对路径
        app_private_key_path=u"../trade/keys/private_2048.txt",
        alipay_public_key_path="../trade/keys/alipay_key_2048",  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        # 如果为True那就是用沙箱环境
        debug=True,  # 默认False,
        # 这是同步的接口
        return_url="http://39.102.98.66:8000/alipay/return/"
    )

    # 这一块是验证支付宝返回的数据是否正确
    o = urlparse(return_url)
    query = parse_qs(o.query)
    processed_query = {}
    # 把sign拿出来
    ali_sign = query.pop("sign")[0]

    # query里的参数是放在List下的,现在是要处理成dict，也就是字符串
    for key, value in query.items():
        processed_query[key] = value[0]
    print(alipay.verify(processed_query, ali_sign))

    url = alipay.direct_pay(
        subject="测试订单",
        # 订单号
        out_trade_no="20210202113289qq",
        # 要支付多少钱
        total_amount=67,
        # 这个就是用户支付后要跳转的页面
        return_url="http://39.102.98.66:8000/"

    )
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    print(re_url)