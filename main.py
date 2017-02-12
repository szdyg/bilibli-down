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
from urllib import parse

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


def net_video_sniffer(url, full_hd=True, retry=3):
    """
    用flvcd的网页进行在线视频嗅探
    :param url: 在线视频url
    :param full_hd: 是否解析超清视频
    :param 重试次数，可选
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
                'value').split('|') if x] if temp else []
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
    print('请输入b站番剧链接：', end='')
    index = input()  # 'http://bangumi.bilibili.com/anime/2261/play#50529'
    print('解析中……\n')

    if re.match(r'http[s]?://bangumi.bilibili.com/anime/', index):
        # 通过番剧id获取番剧信息
        bangumi_id = int(re.findall(r'\d+', index)[0])
        info = get_bangumi_info(bangumi_id)
        bangumi_title = '{} {}'.format(info['bangumi_title'],
                                       info['season_title'])

        # 输出信息
        print('番剧名称：{}\n番剧简介：{}'.format(bangumi_title,
                                        info['evaluate'].strip()))
        print('共{}话'.format(len(info['episodes'])))

        # 设定保存文件夹
        bangumi_dir = 'D:\\动漫\\{}'.format(bangumi_title)
        if not os.path.exists(bangumi_dir):
            os.mkdir(bangumi_dir)

        # 遍历视频页面
        info['episodes'].reverse()
        for i, episode in enumerate(info['episodes']):
            print('下载第{}话……'.format(i + 1))
            # 设置文件前缀
            episode_title = 'Ep{:0>2}{}'.format(i + 1, '.{}'.format(
                episode['index_title']) if episode['index_title'] else '')

            # 获取视频下载链接
            download_list = net_video_sniffer(episode['webplay_url'])

            # 准备下载
            down_man = ARIA2C(bangumi_title)
            for part_index, url in enumerate(download_list):
                file_type = url_file_type(url)
                # 设定文件名
                if len(download_list) == 1:
                    file_name = '{}.{}'.format(episode_title, file_type)
                else:
                    file_name = '{}_part{:0>2}.{}'.format(
                        episode_title, part_index, file_type)

                file_name = correct_file_name(file_name)
                # 添加进队列
                down_man.add_task(url, bangumi_dir, file_name)

            # 下载
            down_man.start()

    elif re.match('http[s]?://www.bilibili.com/video/av\d+/.*', index):
        global s
        r = s.get(re.sub(r'index_\d+.html', '', index))
        tree = lxml.html.fromstring(r.text)

        # 获取标题、简介
        bangumi_title = tree.cssselect('div.v\-title h1')[0].text
        bangumi_title = correct_file_name(bangumi_title)
        evaluate = tree.cssselect(
            'meta[name=description]')[0].get('content')

        # 获取视频列表
        video_list = tree.cssselect('div#plist option')
        video_title_list = [x.text for x in video_list]
        video_list = [parse.urljoin(index, x.get('value'))
                      for x in video_list]
        # 输出信息
        print('番剧名称：{}\n番剧简介：{}'.format(bangumi_title, evaluate))
        print('共{}话'.format(len(video_list)))

        # 设定保存文件夹
        bangumi_dir = 'D:\\动漫\\{}'.format(bangumi_title)
        if not os.path.exists(bangumi_dir):
            os.mkdir(bangumi_dir)

        # 遍历视频页面
        for i, video_url in enumerate(video_list):
            print('下载第{}话……'.format(i + 1))
            # 设置文件前缀
            episode_title = 'Ep{:0>2}.{}'.format(
                i + 1, video_title_list[i].split('、', 1)[-1])

            # 获取视频下载链接
            download_list = net_video_sniffer(video_url)

            # 准备下载
            down_man = ARIA2C(bangumi_title)
            for part_index, url in enumerate(download_list):
                file_type = url_file_type(url)
                # 设定文件名
                if len(download_list) == 1:
                    file_name = '{}.{}'.format(episode_title, file_type)
                else:
                    file_name = '{}_part{:0>2}.{}'.format(
                        episode_title, part_index, file_type)

                file_name = correct_file_name(file_name)
                # 添加进队列
                down_man.add_task(url, bangumi_dir, file_name)

            # 下载
            down_man.start()
    else:
        print('url解析错误')


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
