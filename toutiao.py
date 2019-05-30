# _*_ coding=utf-8 _*_

import requests
import time
import os
from hashlib import md5
from urllib.parse import urlencode
from multiprocessing.pool import Pool


def get_data(offset):
    """
    构造URL，发送请求
    :param offset:
    :return:
    """
    timestamp = int(time.time())
    params = {
        'aid': '24',
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis',
        'timestamp': timestamp
    }

    base_url = 'https://www.toutiao.com/api/search/content/?keyword=%E8%A1%97%E6%8B%8D'
    url = base_url + urlencode(params)
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
    except requests.ConnectionError:
        return '555...'


def get_img(data):
    """
    提取每一张图片连接，与标题一并返回，构造生成器
    :param data:
    :return:
    """
    if data.get('data'):
        page_data = data.get('data')
        for item in page_data:
            # cell_type字段不存在的这类文章不爬取，它没有title，和image_list字段，会出错
            if item.get('cell_type') is not None:
                continue
            title = item.get('title').replace(' |', ' ')    # 去掉某些可能导致文件名错误而不能创建文件的特殊符号
            imgs = item.get('image_list')
            for img in imgs:
                yield {
                    'title': title,
                    'img': img.get('url')
                }


def save(item):
    """
    根据title创建文件夹，将图片以二进制形式写入，
    图片名称使用其内容的md5值，可以去除重复的图片
    :param item:
    :return:
    """
    img_path = 'img' + '/' + item.get('title')
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    try:
        res = requests.get(item.get('img'))
        if res.status_code == 200:
            file_path = img_path + '/' + '{name}.{suffix}'.format(
                name=md5(res.content).hexdigest(),
                suffix='jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(res.content)
                print('Successful')
            else:
                print('Already Download')
    except requests.ConnectionError:
        print('Failed to save images')


def main(offset):
    data = get_data(offset)
    for item in get_img(data):
        print(item)
        save(item)


START = 0
END = 10
if __name__ == "__main__":
    pool = Pool()
    offsets = ([n * 20 for n in range(START, END + 1)])
    pool.map(main, offsets)
    pool.close()
    pool.join()
