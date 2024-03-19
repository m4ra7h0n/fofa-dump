import re

from fofa import FofaSearch


def jd():
    # 奇怪了2023-04-05和2023-04-04一天差了14w....这个真没办法了
    hosts = FofaSearch('domain="jd.com"', fields='link', deduplicate_field='link').get_all_assets()
    with open('domains.txt', 'w') as f:
        for host in hosts:
            r = re.compile('^(https?://)?([.\w-]*)(:\d{,8})?').match(host)
            if r:
                f.write(r.group(2) + '\n')


def re_test():
    # 提取域名和ip
    s = ['http://a.com:80',
         'http://b.com',
         'http://1.1.1.1:80',
         'http://1.1.1.2',
         '1.1.1.3',
         '1.1.1.4:65535',
         'c.com:80',
         'd.com']
    p = re.compile('^(https?://)?([.\w-]*)(:\d{,8})?')
    for u in s:
        r = p.match(u)
        print(r.group(2))


if __name__ == '__main__':
    jd()
    # FofaSearch(query_str='app = "wspx"', deduplicate_field='domain').get_all_assets()
    # FofaSearch('domain="jd.com"', fields='domain,title,link', deduplicate_field='domain').get_all_assets()
    # FofaSearch('app="log4j2"').get_all_assets()

    # now = now_timestamp()
    # before = time_format_to_timestamp('2018-01-01')
    # days = diff_timestamp(now, before)
    # print(days)
