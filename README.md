# bilibli-down
下载[b站](http://www.bilibili.com/)上的番剧[http://bangumi.bilibili.com/anime/1089](http://bangumi.bilibili.com/anime/1089)和视频集合[http://www.bilibili.com/video/av390875/](http://www.bilibili.com/video/av390875/)

# 使用
1. 运行main.py，输入上述链接之一即可下载，下载的动漫保存在"D:\\动漫\\'动漫名'"目录下。
2. 因为B站超清视频有分段，所以下载完成后需要将comb.py复制到"D:\\动漫\\'动漫名'"目录运行，使用ffmpeg进行视频合并。

# 依赖
1. 第三方模块：requests、lxml+cssselect
2. 环境变量里有aria2c和ffmpeg程序
