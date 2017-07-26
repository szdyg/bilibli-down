# !/usr/bin/env python
# coding:utf-8
"""
Created by tzw0745 on 2017/2/6.
"""
import os
import re
import shutil
import traceback
import configparser

from Module.Downloader import ARIA2C
from Module.Bilibili import Bilibili


def correct_file_name(file_name):
    file_name = file_name.replace('\\', '＼').replace('/', '、')
    file_name = file_name.replace(':', '：').replace('*', '×')
    file_name = file_name.replace('?', '？').replace('"', '＂')
    file_name = file_name.replace('<', '＜').replace('>', '＞')
    return file_name.replace('|', '｜')


def merge_video(video_list, out):
    """
    合并视频文件
    :param video_list: 要合并的视频文件列表
    :param out: 视频输出路径
    :return: 无
    """
    with open('merge.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join("file '{}'".format(x)
                          for x in video_list))
    cmd = 'ffmpeg -f concat -safe 0 -i merge.txt -c copy "{}"'
    os.system(cmd.format(out))
    os.remove('merge.txt')


def main():
    # 读取配置文件
    cfg = configparser.ConfigParser()
    cfg.read('main.ini', encoding='utf-8')
    proxy = cfg.get('main', 'proxy', fallback=None)
    save_dir = cfg.get('main', 'dir', fallback='D:/动漫')
    cache_dir = cfg.get('main', 'cache', fallback='D:/temp')
    # 如果配置文件未指定url，则从控制台输入
    try:
        target = cfg.get('main', 'url')
        print('b站番剧链接：', target)
    except configparser.Error:
        print('请输入b站番剧链接：', end='', flush=True)
        target = input()
    if target[-1] != '/':
        target = '{}/'.format(target)
    print('解析中……\n')

    bilibili = Bilibili()
    # 获取番剧信息
    if re.match(r'^http[s]?://bangumi.bilibili.com/anime/\d+[/?].*', target):
        bangumi_id = int(re.findall(r'/(\d+)[/?].*', target)[0])
    elif re.match('http[s]?://www.bilibili.com/video/av\d+[/?].*', target):
        bangumi_id = re.findall(r'/(av\d+)[/?].*', target)[0]
    else:
        raise ValueError('url not match')
    info = bilibili.get_bangumi_info(bangumi_id)
    info['title'] = correct_file_name(info['title'])
    print('番剧名称：{}\n番剧简介：{}'.format(info['title'], info['intro']))
    print('共{}话'.format(len(info['eps'])))

    # 设置保存路径、缓存路径
    os.mkdir(save_dir) if not os.path.exists(save_dir) else None
    save_dir = '/'.join([save_dir, info['title']])
    os.mkdir(save_dir) if not os.path.exists(save_dir) else None
    os.mkdir(cache_dir) if not os.path.exists(cache_dir) else None

    # 设置下载器、下载参数、文件名格式
    down_man = ARIA2C('/'.join([cache_dir, info['title']]))
    headers = {'Referer': 'http://www.bilibili.com/'}
    epf = 'Ep{:0>2}.{}.{}' if len(info['eps']) < 100 else 'Ep{:0>3}.{}.{}'
    # 遍历番剧章节
    for i, ep in enumerate(info['eps']):
        print('下载第{:0>2}话……'.format(i + 1))
        # 获取章节视频信息
        video_info = bilibili.video_url_list(ep['url'])

        # 设置目标文件名、缓存文件名
        file_name = epf.format(i + 1, ep['title'], video_info['type'])
        file_name = file_name.replace('..', '.')
        final_file = '/'.join([save_dir, file_name])
        temp_file = '/'.join([cache_dir, file_name])
        if os.path.exists(final_file):
            continue

        # 判断是否需要分段下载
        part_list = []
        if len(video_info['src']) > 1:
            for part_i, part_url in enumerate(video_info['src']):
                part_file = '{}.part{:0>2}'.format(file_name, part_i)
                part_list.append('/'.join([cache_dir, part_file]))
                down_man.add_task(part_url, cache_dir, part_file,
                                  headers=headers, proxy=proxy)
        elif len(video_info['src']) == 1:
            down_man.add_task(video_info['src'][0], cache_dir, file_name,
                              headers=headers, proxy=proxy)
        down_man.start()

        # 缓存文件to目标文件
        if os.path.exists(temp_file):
            shutil.move(temp_file, final_file)
        else:
            merge_video(part_list, temp_file)
            shutil.move(temp_file, final_file)
            for x in part_list:
                os.remove(x)


if __name__ == '__main__':
    split_line = '-' * 80
    try:
        print(split_line)
        main()
        print('\nall done')
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
    finally:
        print(split_line)
    input()
