# !/usr/bin/env python
# coding:utf-8
"""
Created by tzw0745 on 2017/2/6.
"""
import os
import collections
import traceback


def main():
    tasks = collections.defaultdict(list)
    for file in [x for x in os.listdir() if x.startswith('Ep')]:
        tasks[file.split('_')[0]].append(file)

    for task_name in tasks:
        if len(tasks[task_name]) <= 1:
            continue
        file_type = tasks[task_name][0].split('.')[-1]
        with open('list.txt', 'w') as f:
            f.write('\n'.join('file \'{}\''.format(file)
                              for file in tasks[task_name]))
        shell = 'ffmpeg -f concat -i list.txt -c copy out.{}'
        os.system(shell.format(file_type))
        os.rename('out.{}'.format(file_type),
                  '{}.{}'.format(task_name, file_type))
        os.remove('list.txt')
        for file in tasks[task_name]:
            os.remove(file)

    print(tasks)

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
