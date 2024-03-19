import base64

import requests
import urllib3

from settings import FOFA_KEY, FOFA_EMAIL
from utils.command import parse_json
from utils.httpclient import Request
from utils.time_tools import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FofaSearch:
    """
    如果一天更新资产超过1w那超过的部分就没辙了
    """

    def __init__(self, query_str, fields='ip,host,port,link,domain', deduplicate_field='host'):
        """
        :param query_str: 查询字符串
        :param fields: 查询字段
        :param deduplicate_field: 去重字段, 需要在fields中出现
        """
        self.key = FOFA_KEY
        self.email = FOFA_EMAIL
        self.query_str = query_str
        self.query = query_str  # self.query = '(' + query_str + ') && country="CN" && status_code="200"'
        self.fields = fields  # ip,port,host,link,domain -> https://fofa.info/api/batches_pages
        if deduplicate_field not in fields:
            raise Exception('需要传入去重的字段, 并且该字段在fields中')
        self.deduplicate_field = deduplicate_field

    def get_all_assets(self):
        print(self.query)
        return self.get_all_assets_recursion(time_format_to_timestamp(increase(now_timestamp(), 1)))

    def get_all_assets_recursion(self, timestamp_before):
        total_size = self.get_total_size()
        size_counter = 0  # 累加获取的数量
        print('fofa查询获取总数量: ' + str(total_size))
        deduplicate_set = set()  # 用于去重的集合
        assets = []  # 最终返回的资产
        o_right = 365  # 初始二分查找跨度可稍微设置大一点, 程序自动调整该大小
        o_left = 0
        target = 10000
        while True:
            query = '{query} && before="{before}"'.format(query=self.query, before=timestamp_to_time_format(timestamp_before))
            result = self.my_fofa(query)
            if result is not None:
                size = self.add_assets(result, deduplicate_set, assets)
                last_total_size = size['last_total_size']
                size_counter += size['this_size']

                if last_total_size == 0:
                    break
                print('fofa查询本次获取数量 before->{before}: {num}'.format(before=timestamp_to_time_format(timestamp_before), num=str(len(result['results']))))

                # right值动态调整, 找到下一个1w条的最小before
                # 三种情况
                # 1.10000落在left和right区间      -> 这种情况的二分法有意义
                # 1.right值和上一次请求的差值小于1w -> 这种情况就是right设置过小, 会有大量重复的数据等待去重
                # 1.left和上一次请求的差值大于1w    -> 这种情况不会, 因为left为0, 和上次一样
                # 综合来看初始right设置大一点没有问题
                left = o_left
                right = o_right
                while left < right:
                    mid = (left + right) // 2

                    query = '{query} && before="{before}"'.format(query=self.query, before=decrease(timestamp_before, mid))
                    result = self.my_fofa(query, size=1)
                    if result is not None:
                        next_total_size = int(result['size'])
                        diff = last_total_size - next_total_size
                        # print(diff)
                        if diff == target:
                            right = mid
                        elif diff < target:
                            left = mid + 1
                        elif diff > target:
                            right = mid

                last_timestamp_before = timestamp_before
                timestamp_before = time_format_to_timestamp(decrease(timestamp_before, left))
                # 寻找差值最接近1w的下一个before的时间, 使用二分法, right为上次查找和本次查找时间差值的二倍 (稍微智能一些)
                o_right = diff_timestamp(last_timestamp_before, timestamp_before) * 2

                # 数量过少的情况
                if size_counter >= total_size:
                    break
        print('去重后已获取: ' + str(len(assets)))
        return assets

    def my_fofa(self, query=None, size=10000, fields=None):
        query = self.query if query is None else query
        fields = self.fields if fields is None else fields
        qbase64 = base64.b64encode(query.encode('utf-8'))
        url = 'https://fofa.info/api/v1/search/all?email={email}&key={key}&size={size}&fields={fields}&qbase64={qbase64}&full=true'.format(email=self.email, key=self.key, fields=fields, size=size, qbase64=qbase64.decode('utf'))
        data = Request().get(url).data
        return self.handle_fofa_result(data)

    # 主要是请求fofa结果处理, 异常打印, 除了正常结果其余都返回None
    def handle_fofa_result(self, result) -> str: # 取text之后的内容, json类型
        # fofa层面的错误
        if isinstance(result, requests.Response):
            if result.status_code != 200:
                print(result)
                return None
            else:
                result = result.text
        result = parse_json(result)
        error = result.get('error')
        if error:
            print(result)
            return None
        else:
            return result

    def get_total_size(self) -> int:
        """
        使用fofa查询软件, 设置full=true拿到的全部数量
        :return:
        """
        size = self.my_fofa(size=1)['size']
        return int(size)

    def add_assets(self, result, deduplicate_set, assets):
        """
        去重, 添加资产, 返回result中的数量
        :param result: 单次查询结果
        :param deduplicate_set: 用于去重的数据
        :param assets: 总资产
        :return: (本次获取未去重数量, 总共的资产数)
        """
        idx = self.fields.split(',').index(self.deduplicate_field)
        for asset in result['results']:
            deduplicate_data = ''
            if isinstance(asset, list):
                deduplicate_data = asset[idx]  # 多字段
            else:
                deduplicate_data = asset  # 单字段

            if deduplicate_data not in deduplicate_set:
                assets.append(asset)
                deduplicate_set.add(deduplicate_data)

        # (本次获取未去重数量, 总共的资产数)
        return {'this_size': len(result['results']), 'last_total_size': result['size']}