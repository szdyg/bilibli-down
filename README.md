# bilibli-down
> 下载[b站](http://www.bilibili.com/)上的多集视频，如：
* [http://bangumi.bilibili.com/anime/5070/play#91004](http://bangumi.bilibili.com/anime/5070/play#91004)
  ![](http://ofpb4e3i2.bkt.clouddn.com/17-4-9/84740577-file_1491669211227_1054b.png)
* [http://www.bilibili.com/video/av4052827/](http://www.bilibili.com/video/av4052827/)
![](http://ofpb4e3i2.bkt.clouddn.com/17-4-9/13494349-file_1491669452084_17c38.png)

# 使用
1. 修改main.ini，再运行main.py即可下载，动漫保存目录由main.ini中的main-->dir指定，proxy代理可选。
2. 因为B站超清视频有分段，所以下载完成后需要将comb.py复制到动漫下载目录下运行，使用ffmpeg进行视频合并。

# 依赖
1. 第三方模块：requests、lxml+cssselect
2. 环境变量里有ffmpeg程序
