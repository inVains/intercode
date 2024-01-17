import config
import requests
import json
import os
import re
from time import sleep

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

# Set OpenAPI key from environment or config file
API_KEY = os.environ.get("WENXIN_API_KEY")
SECRET_KEY = os.environ.get("WENXIN_SECRET_KEY")
if (API_KEY is None or API_KEY == "") and os.path.isfile(os.path.join(os.getcwd(), "keys.cfg")):
    cfg = config.Config('keys.cfg')
    API_KEY = cfg.get("WENXIN_API_KEY")
    SECRET_KEY = cfg.get("WENXIN_SECRET_KEY")


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    token = str(requests.post(url, params=params).json().get("access_token"))
    return token


# Define Wenxin chat function
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def Wenxin(messages, model="completions", num_samples=1):
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}?access_token=" + get_access_token()

    payload = json.dumps({
        "messages": messages,
        "disable_search": False,
        "enable_citation": False,
        # "temperature":0, # wenxin建议该参数和top_p只设置1个
        "top_p": 0,  # 影响输出文本的多样性，取值越大，生成文本的多样性越强
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)
    return res.get("result")


if __name__ == "__main__":
    messages = [
        {
            "role": "user",
            "content": "#使用下面格式进行回答，每个问题和答案通过----分隔，只要返回回答# \n问题：「中国有多少个民族？」\n回答：「56个民族」\n---- \n问题：「中国国土一共有多少平方公里」 \n回答："
        },
        {
            "role": "assistant",
            "content": "「中国国土面积为960万平方公里」"
        },
        {
            "role": "user",
            "content": "问题：「中国湖南省多少平方公里」\n回答："
        }
    ]
    print(Wenxin(messages))
