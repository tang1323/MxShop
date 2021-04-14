
"""发送手机验证码的接口，云片网"""
import requests
import json


class YunPian(object):

    def __init__(self, api_key):
        """api_key在云片网的接口里说明必须要传送，下面是它的url"""
        self.api_key = api_key
        self.single_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_sms(self, code, mobile):
        """code是验证码，mobile是手机"""
        parmas = {
            # 这里的"apikey","mobile", "text"要和官方文档保持一致
            # "text"要与模版的一样，最好复制
            "apikey": self.api_key,
            "mobile": mobile,
            "text": "【唐明锐】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }
        # 然后我们就requests发送了
        response = requests.post(self.single_send_url, data=parmas)

        # 它返回的是字符串，这里我们转换成一个字典或者列表
        re_dict = json.loads(response.text)
        return re_dict
        # print(re_dict)


if __name__ == "__main__":
    # 3b4b90283fa8e7caae18876077f7b08b是apikey
    yun_pian = YunPian("3b4b90283fa8e7caae18876077f7b08b")
    # 自定义发送验证码和手机
    yun_pian.send_sms("274632", "13232732408")

















