# !/usr/bin/env python
# coding:utf-8
"""
Created by tzw0745 on 2017/7/26.
"""
import re
import json
from urllib import parse
from subprocess import check_output

import requests
import lxml.html


class Bilibili:
    def __init__(self):
        self.session = requests.session()

    def get_bangumi_info(self, bangumi_id):
        """
        获取番剧信息
        :param bangumi_id: 番剧id
        :return: 字典信息，包括名称、简介、url列表
        """
        bangumi_id = str(bangumi_id)
        if re.match(r'^\d+$', bangumi_id):
            host = 'http://bangumi.bilibili.com/'
            url = '{}jsonp/seasoninfo/{}.ver'.format(host, bangumi_id)
            r = self.session.get(url)
            if r.status_code == 404:
                raise ValueError('404 not found')
            r.encoding = 'utf-8'
            text = r.text
            text = text[text.find('{'): text.rfind('}') + 1]
            data = json.loads(text)['result']
            title = data['title']
            intro = data['evaluate']
            eps = [{'title': x['index_title'], 'url': x['webplay_url']}
                   for x in data['episodes']]
            eps.reverse()
        elif re.match(r'^av\d+$', bangumi_id):
            host = 'http://www.bilibili.com/'
            url = '{}video/{}/'.format(host, bangumi_id)
            r = self.session.get(url)
            if r.status_code == 404:
                raise ValueError('404 not found')
            r.encoding = 'utf-8'
            tree = lxml.html.fromstring(r.text)

            title = tree.cssselect('div.v\-title')[0]
            title = title.cssselect('h1')[0].text
            intro = tree.cssselect('div#v_desc')[0].text
            select = tree.cssselect('select#dedepagetitles')
            if select:
                eps = [{'title': x.text.split('、', 1)[-1],
                        'url': parse.urljoin(url, x.get('value'))}
                       for x in select[0].cssselect('option')]
            else:
                eps = [{'title': title, 'url': url}]
        else:
            raise ValueError('bangumi id not match')

        return {'title': title,
                'intro': intro,
                'eps': eps}

    @staticmethod
    def video_url_list(url, you_get=None):
        """
        获取网页中的视频文件列表
        :param url: 页面url
        :param you_get: you-get.exe 文件路径
        :return: 视频文件列表和文件类型
        """
        if not url.startswith('http://bangumi.bilibili.com/anime/') and \
                not url.startswith('http://www.bilibili.com/video/'):
            raise ValueError('url not correct')
        you_get = you_get if you_get else 'you-get.exe'
        cmd = '{} --json {}'.format(you_get, url)
        output = check_output(cmd)
        try:
            result = json.loads(output.decode('gbk'))
        except UnicodeDecodeError:
            result = json.loads(output.decode('utf-8'))
        key = max(result['streams'],
                  key=lambda x: result['streams'][x]['size'])
        return {'src': result['streams'][key]['src'],
                'type': result['streams'][key]['container']}
