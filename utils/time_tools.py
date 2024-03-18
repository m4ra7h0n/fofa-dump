import datetime
import time


def timestamp_to_time_format(timestamp) -> str:
    """
    从时间戳转化成2023-01-01格式
    :param timestamp:
    :return:
    """
    return time.strftime("%Y-%m-%d", time.localtime(timestamp))

def time_format_to_timestamp(time_format) -> int:
    """
    从2023-01-01转化成时间戳格式
    :param time_format:
    :return:
    """
    return int(time.mktime(time.strptime(time_format, "%Y-%m-%d")))

def now_timestamp() -> int:
    """
    当前时间戳
    :return: 1710069428格式
    """
    return int(time.time())

def now_time_format() -> str:
    """
    当前日期
    :return: 2023-01-01格式
    """
    return timestamp_to_time_format(now_timestamp())

def decrease(from_timestamp, days):
    """
    减少天数
    :param from_timestamp: 从哪天减少, 需要传入时间戳
    :param days: 减少多少天
    :return: 2023-01-01格式
    """
    from_date = datetime.datetime.fromtimestamp(from_timestamp)
    delta = datetime.timedelta(days=days)
    n_days = from_date - delta
    return n_days.strftime('%Y-%m-%d')

def increase(from_timestamp, days):
    """
    增加天数
    :param from_timestamp: 从哪天减少, 需要传入时间戳
    :param days: 增加多少天
    :return: 2023-01-01格式
    """
    from_date = datetime.datetime.fromtimestamp(from_timestamp)
    delta = datetime.timedelta(days=days)
    n_days = from_date + delta
    return n_days.strftime('%Y-%m-%d')

def diff_timestamp(bigger_timestamp, smaller_timestamp):
    """
    :param bigger_timestamp: bigger
    :param smaller_timestamp: smaller
    :return: days
    """
    bigger_date = datetime.datetime.fromtimestamp(bigger_timestamp)
    smaller_date = datetime.datetime.fromtimestamp(smaller_timestamp)
    return (bigger_date - smaller_date).days