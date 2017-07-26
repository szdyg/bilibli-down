# !/usr/bin/env python
# coding:utf-8
"""
Created by tzw0745 on 2017/2/7.
"""
import os
import time
import subprocess
import collections


class IDM:
    """
    使用IDM进行下载等操作
    """

    def __init__(self, name, idm_dir=None):
        """
        初始化IDM类
        :param name: 任务名称，只是为了配合ARIA2C的init参数列表
        :param idm_dir: IDM的安装目录，可选
        """
        self.idm_dir = idm_dir if idm_dir else 'C:\\Program Files (x86)\\' \
                                               'Internet Download Manager'
        self.idm_path = '{}\\IDMan.exe'.format(self.idm_dir)
        self.name = name

    def add_task(self, url, file_dir, file_name, delay=0.5):
        """
        静默模式添加任务到IDM的下载队列
        :param url: 下载链接
        :param file_dir: 保存目录，绝对路径
        :param file_name: 保存文件名
        :param delay: 添加任务前的延迟(s)，可选
        :return: 无
        """
        time.sleep(delay)
        command = '"{}" /d "{}" /p "{}" /f "{}" /n /a'.format(
            self.idm_path, url, file_dir, file_name
        )
        subprocess.Popen(command)

    def start(self):
        """
        启动队列
        :return: 无
        """
        command = '"{}" /s'.format(self.idm_path)
        # 这个命令是启动idm的下载队列
        # 但idm 6.27 build3在win10 x64下执行这条命令时会崩溃
        # subprocess.Popen(command)
        print(command)


class ARIA2C:
    """
    使用ARIA2C进行下载等操作
    """

    def __init__(self, name, aria2c_dir=''):
        """
        初始化ARIA2C类
        :param name: 任务名
        :param aria2c_dir: ARIA2C的位置，可选
        """
        self.name = name
        self.aria2c_path = '{}aria2c.exe'.format(
            '{}\\'.format(aria2c_dir) if aria2c_dir else ''
        )
        self.tasks = collections.defaultdict()

    def __len__(self):
        """
        获取队列长度
        :return: int，队列长度
        """
        return len(self.tasks)

    def add_task(self, url, file_dir, file_name, headers=None, proxy=None):
        """
        添加任务到下载队列
        :param url: 下载链接
        :param file_dir: 保存目录，绝对路径
        :param file_name: 保存文件名
        :param headers: http headers，可选
        :param proxy: 代理，可选
        :return: bool，链接重复、文件已存在返回False
        """
        if url in self.tasks:
            return False
        file_path = '{}/{}'.format(file_dir, file_name)
        # 判断是否下载完成
        if os.path.exists(file_path) and not os.path.exists(
                        file_path + '.aria2'):
            return False

        self.tasks[url] = {'file_dir': file_dir,
                           'file_name': file_name}
        if headers:
            self.tasks[url]['headers'] = headers
        if proxy:
            self.tasks[url]['proxy'] = proxy
        return True

    def start(self):
        """
        启动队列，下载完成后清空队列
        :return: 无
        """
        if not self.tasks:
            return

        # 写入配置文件
        with open('{}.txt'.format(self.name), 'w', encoding='utf-8') as f:
            for i, url in enumerate(self.tasks):
                # 写入url
                f.write(url + '\n')
                # 写入headers
                headers = self.tasks[url].get('headers', {})
                for key in headers:
                    f.write(' header={}: {}\n'.format(key, headers[key]))
                # 写入目录和文件名
                f.write(' dir={}\n'.format(self.tasks[url]['file_dir']))
                f.write(' out={}\n'.format(self.tasks[url]['file_name']))
                # 其他
                f.write(' continue=true\n max-connection-per-server=10\n')
                proxy = self.tasks[url].get('proxy', None)
                if proxy:
                    f.write(' all-proxy={}\n'.format(proxy))
                f.write(' split=10\n min-split-size=1M\n')
                if i < len(self.tasks) - 1:
                    f.write('\n')
        # 开始下载
        command = '{} -i "{}.txt"'.format(self.aria2c_path, self.name)
        os.system(command)
        # 删除配置文件
        os.remove('{}.txt'.format(self.name))
        # 清空队列
        self.tasks.clear()
