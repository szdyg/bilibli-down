# !/usr/bin/env python
# coding:utf-8
"""
Created by tzw0745 on 2017/2/6.
"""
import os
import re
import json
import traceback
import configparser
from urllib.parse import urljoin
from subprocess import check_output

import requests
import lxml.html

from downloader import ARIA2C, IDM

s = requests.session()


def correct_file_name(file_name):
    """
    删除文件名中非法字符
    :param file_name: 文件名
    :return: 删除非法字符后的文件名
    """
    return re.sub(r'[\\/:*?"<>|]', '', file_name)


def net_video_sniffer(url):
    """
    用you-get进行在线视频嗅探
    :param url: 在线视频url
    :return: 列表，视频的下载链接
    """
    cmd = 'you-get.exe --json "{}"'.format(url)
    output = check_output(cmd)
    try:
        result = json.loads(output.decode('gbk'))
    except UnicodeDecodeError:
        result = json.loads(output.decode('utf-8'))
    return {'src': result['streams']['__default__']['src'],
            'type': result['streams']['__default__']['container']}


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
        raise KeyError('番剧id必须为纯数字: {}'.format(bangumi_id))

    global s
    url = 'http://bangumi.bilibili.com/jsonp/seasoninfo/{}.ver'
    r = s.get(url.format(bangumi_id))
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
    proxy = cfg.get('main', 'proxy', fallback=None)
    save_dir = cfg.get('main', 'dir', fallback='D:/动漫')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    try:
        target = cfg.get('main', 'url')
        print('b站番剧链接：', target)
    except configparser.Error:  # 用户输入
        print('请输入b站番剧链接：', end='')
        target = input()
    if target[-1] != '/':
        target = '{}/'.format(target)
    print('解析中……\n')

    if re.match(r'http[s]?://bangumi.bilibili.com/anime/\d+[/?].*', target):
        # 获取番剧信息
        bangumi_id = int(re.findall(r'/(\d+)[/?].*', target)[0])
        info = get_bangumi_info(bangumi_id)

        # 动漫保存文件夹
        bangumi_title = '{} {}'.format(info['bangumi_title'],
                                       info['season_title'])
        save_dir = '{}/{}'.format(save_dir, correct_file_name(bangumi_title))
        info['episodes'].reverse()
        # url和标题
        ep_url_list = [ep['webplay_url'] for ep in info['episodes']]
        ep_title_list = [ep['index_title'] for ep in info['episodes']]

        print('番剧名称：{}\n番剧简介：{}'.format(bangumi_title,
                                        info['evaluate'].strip()))
        print('共{}话'.format(len(info['episodes'])))

    elif re.match('http[s]?://www.bilibili.com/video/av\d+[/?].*', target):
        # 获取番剧信息
        global s
        tree = lxml.html.fromstring(s.get(target).text)
        evaluate = tree.cssselect(
            'meta[name=description]')[0].get('content')

        # 动漫保存文件夹
        bangumi_title = tree.cssselect('div.v\-title h1')[0].text
        save_dir = '{}/{}'.format(save_dir, correct_file_name(bangumi_title))
        # url和标题
        play_list = tree.cssselect('div#plist option')
        ep_url_list = [urljoin(target, x.get('value')) for x in play_list]
        ep_title_list = [x.text.split('、', 1)[1] for x in play_list]

        # 输出信息
        print('番剧名称：{}\n番剧简介：{}'.format(bangumi_title, evaluate))
        print('共{}话'.format(len(play_list)))

    else:
        print('url解析错误')
        return
    if not ep_url_list:
        return

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    epf = 'Ep{:0>2}.{}.{}' if len(ep_url_list) < 100 else 'Ep{:0>3}.{}.{}'
    ep_title_list = [correct_file_name(x) for x in ep_title_list]
    # 开始下载
    for i, url in enumerate(ep_url_list):
        print('下载第{:0>2}话……'.format(i + 1))
        temp = net_video_sniffer(url)

        file_name = epf.format(i + 1, ep_title_list[i], temp['type'])
        file_name = file_name.replace('..', '.')

        down_man = ARIA2C(correct_file_name(bangumi_title))
        down_url_list = temp['src']
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
