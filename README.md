# bilibli-down (Python3)
> 下载[b站](http://www.bilibili.com/)上的多集视频，如：
* [http://bangumi.bilibili.com/anime/5070/play#91004](http://bangumi.bilibili.com/anime/5070/play#91004)
  ![](http://ofpb4e3i2.bkt.clouddn.com/17-4-9/84740577-file_1491669211227_1054b.png)
* [http://www.bilibili.com/video/av4052827/](http://www.bilibili.com/video/av4052827/)
![](http://ofpb4e3i2.bkt.clouddn.com/17-4-9/13494349-file_1491669452084_17c38.png)
> 下载效果如下：
  ![](http://ofpb4e3i2.bkt.clouddn.com/17-9-1/3336760.jpg)

# 使用
1. 修改main.ini，再运行main.py即可下载，动漫保存目录由main.ini中的main-->dir指定。
2. 下载过程中的临时文件保存目录由main.ini中的main-->cache指定。
3. http代理由main.ini中的main-->proxy指定。

# 依赖
1. 第三方模块：requests、lxml、cssselect、you-get
2. ffmpeg.exe、you-get.exe需要在环境变量或当前工作目录中。
