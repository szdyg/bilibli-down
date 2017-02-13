# bilibli-down
下载[b站](http://www.bilibili.com/)上的番剧（如[http://bangumi.bilibili.com/anime/1089](http://bangumi.bilibili.com/anime/1089)）和视频集合（如[http://www.bilibili.com/video/av390875/](http://www.bilibili.com/video/av390875/)）

# 使用
1. 修改main.ini，再运行main.py即可下载，动漫保存目录由main.ini中的main-->dir指定，proxy代理可选。
2. 因为B站超清视频有分段，所以下载完成后需要将comb.py复制到动漫下载目录下运行，使用ffmpeg进行视频合并。

# 依赖
1. 第三方模块：requests、lxml+cssselect
2. 环境变量里有aria2c和ffmpeg程序
