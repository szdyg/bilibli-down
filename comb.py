# !/usr/bin/env python
# coding:utf-8
"""
Created by tzw0745 on 2017/2/6.
"""
import re
import os
import collections
import traceback


def main():
    tasks = collections.defaultdict(list)
    for file in [x for x in os.listdir('.') if re.search(r'part\d+$', x)]:
        tasks[file[:file.rfind('.')]].append(file)

    for video_name in tasks:
        with open('list.txt', 'w') as f:
            f.write('\n'.join('file \'{}\''.format(file)
                              for file in tasks[video_name]))
        file_type = video_name.split('.')[-1]
        command = 'ffmpeg -f concat -i list.txt -c copy out.{}'
        os.system(command.format(file_type))
        os.rename('out.{}'.format(file_type), video_name)
        os.remove('list.txt')
        for file in tasks[video_name]:
            os.remove(file)


if __name__ == '__main__':
    split_line = '-' * 80
    try:
        print(split_line)
        main()
        print('\nall done')
    except Exception as e:
        print(traceback.format_exc())
    finally:
        print(split_line)
    input()
