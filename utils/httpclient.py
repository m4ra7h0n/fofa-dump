import requests

from settings import GLOBAL_PROXY
from fake_useragent import UserAgent


class Request:
    # your spider code
    def __init__(self, proxy=True):
        self.data = None
        self.proxy = proxy
        self.ua = UserAgent()

    def get(self, url, **kwargs):
        self.random_UA()
        retry_count = 5
        proxy = get_proxy().get("proxy") if GLOBAL_PROXY and self.proxy else None
        while retry_count > 0:
            try:
                if proxy:
                    response = requests.get(url, verify=False, proxies={"http": "http://{}".format(proxy)}, **kwargs)
                else:
                    response = requests.get(url, verify=False, **kwargs)
                self.handle(response)
                return self
            except Exception:
                retry_count -= 1
        # 删除代理池中代理
        delete_proxy(proxy)
        return None

    def post(self, url, **kwargs):
        self.random_UA()
        retry_count = 5
        proxy = get_proxy().get("proxy") if GLOBAL_PROXY and self.proxy else None
        while retry_count > 0:
            try:
                if proxy:
                    response = requests.post(url, verify=False, proxies={"http": "http://{}".format(proxy)}, **kwargs)
                else:
                    response = requests.post(url, verify=False, **kwargs)
                self.handle(response)
                return self
            except Exception as e:
                print(e)
                retry_count -= 1
        # 删除代理池中代理
        delete_proxy(proxy)
        return None

    def handle(self, response):
        if response.status_code != 200:
            print(response.content)
            return None
        else:
            self.data = response.text


    def random_UA(self, **kwargs):
        headers = kwargs.get('headers', {})
        if headers is None:
            kwargs.update('headers', {'User-Agent': self.ua.random})
        else:
            headers.update({'User-Agent': self.ua.random})

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

