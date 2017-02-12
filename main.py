# !/usr/bin/env python
# coding:utf-8
"""
Created by tzw0745 on 2017/2/6.
"""
import os
import re
import time
import json
import traceback
import configparser
from urllib import parse
from subprocess import check_output

import requests
import lxml.html

from downloader import ARIA2C, IDM

s = requests.session()
bangumi_info_api = 'http://bangumi.bilibili.com/jsonp/seasoninfo/{}.ver'


def correct_file_name(file_name):
    """
    删除文件名中非法字符
    :param file_name: 文件名
    :return: 删除非法字符后的文件名
    """
    return re.sub(r'[\\/:*?"<>|]', '', file_name)


def net_video_sniffer(url, full_hd=True, retry=5):
    """
    用flvcd的网页进行在线视频嗅探
    :param url: 在线视频url
    :param full_hd: 是否解析超清视频
    :param retry: 重试次数，可选
    :return: 列表，视频的下载链接
    """
    api = 'http://www.flvcd.com/parse.php'
    params = {'kw': url.strip()}
    if full_hd:
        params['format'] = 'super'

    global s
    for i in range(retry):
        try:
            tree = lxml.html.fromstring(s.get(api, params=params).text)
            temp = tree.cssselect('input[name=inf]')
            return [x for x in temp[0].get(
                'value').split('|') if x]
        except Exception as error:
            if i >= retry - 1:
                raise ValueError('在线视频{}解析错误 {}'.format(url, str(error)))
            time.sleep(3)


def url_file_type(url):
    """
    从url中获取文件扩展名
    :param url: url
    :return: 文件扩展名
    """
    short = url.split('?')[0].split('/')[-1]
    candidates = re.findall(r'\.([a-zA-Z0-9]{2,5})', short)
    return candidates[-1] if candidates else ''


def get_bangumi_info(bangumi_id):
    """
    获取b站番剧信息
    :param bangumi_id: 番剧id，纯数字
    :return: 字典信息
    """
    try:
        bangumi_id = int(bangumi_id)
    except ValueError:
        raise ValueError('番剧id必须为纯数字: {}'.format(bangumi_id))

    global s, bangumi_info_api
    r = s.get(bangumi_info_api.format(bangumi_id))
    r.encoding = r.apparent_encoding
    temp = r.text
    result = json.loads(temp[temp.find('{'): temp.rfind('}') + 1])
    if result['code'] != 0:
        raise ValueError(result['message'])

    return result['result']


def main():
    # 读取配置文件
    cfg = configparser.ConfigParser()
    cfg.read('main.ini')
    # 读取代理
    try:
        proxy = cfg.get('main', 'proxy')
    except configparser.Error:  # 默认代理
        proxy = None
    # 读取目录
    try:
        save_dir = cfg.get('main', 'dir')
    except configparser.Error:  # 默认目录
        save_dir = 'D:/动漫'
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    # 读取链接
    try:
        index = cfg.get('main', 'url')
        print('b站番剧链接：', index)
    except configparser.Error:  # 用户输入
        print('请输入b站番剧链接：', end='')
        index = input()
    print('解析中……\n')

    if re.match(r'http[s]?://bangumi.bilibili.com/anime/\d+', index):
        # 获取番剧信息
        bangumi_id = int(re.findall(r'\d+', index)[0])
        info = get_bangumi_info(bangumi_id)

        # 更新目录
        bangumi_title = '{} {}'.format(info['bangumi_title'],
                                       info['season_title'])
        save_dir = '{}/{}'.format(save_dir, correct_file_name(bangumi_title))
        info['episodes'].reverse()
        # 获取url和标题
        video_url_list = [ep['webplay_url'] for ep in info['episodes']]
        video_title_list = [ep['index_title'] for ep in info['episodes']]

        # 输出信息
        print('番剧名称：{}\n番剧简介：{}'.format(bangumi_title,
                                        info['evaluate'].strip()))
        print('共{}话'.format(len(info['episodes'])))

    elif re.match('http[s]?://www.bilibili.com/video/av\d+/.*', index):
        # 获取番剧信息
        global s
        r = s.get(re.sub(r'index_\d+.html', '', index))
        tree = lxml.html.fromstring(r.text)
        evaluate = tree.cssselect(
            'meta[name=description]')[0].get('content')

        # 更新目录
        bangumi_title = tree.cssselect('div.v\-title h1')[0].text
        save_dir = '{}/{}'.format(save_dir, correct_file_name(bangumi_title))
        # 获取视频列表
        part_list = tree.cssselect('div#plist option')
        video_url_list = [parse.urljoin(index, x.get('value'))
                          for x in part_list]
        video_title_list = [x.text.split('、', 1)[-1] for x in part_list]

        # 输出信息
        print('番剧名称：{}\n番剧简介：{}'.format(bangumi_title, evaluate))
        print('共{}话'.format(len(part_list)))

    else:
        print('url解析错误')
        return

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    epf = 'Ep{:0>2}.{}.flv'
    if len(video_url_list) > 100:
        epf = 'Ep{:0>3}.{}.flv'
    # 下载
    for i, url in enumerate(video_url_list):
        print('下载第{:0>2}话……'.format(i + 1))
        file_name = epf.format(i + 1, video_title_list[i])

        down_man = ARIA2C(correct_file_name(bangumi_title))
        down_url_list = net_video_sniffer(url)
        if len(down_url_list) > 1:
            for part_i, part_url in enumerate(down_url_list):
                part_file = '{}.part{:0>2}'.format(file_name, part_i)
                down_man.add_task(part_url, save_dir, part_file,
                                  proxy=proxy)
        else:
            down_man.add_task(down_url_list[0], save_dir, file_name,
                              proxy=proxy)
        down_man.start()


if __name__ == '__main__':
    split_line = '-' * 80
    try:
        print(split_line)
        main()
        print('\nall done')
    except:
        print(traceback.format_exc())
    finally:
        print(split_line)
    input()
