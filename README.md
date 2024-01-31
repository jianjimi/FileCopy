# FileCopy
使用Python+pywebview+VUE3+HTML+JS+CSS制作的一款文件拷贝检验工具。

在没人大量恶意使用的情况下，可能会开源，可能免费

--------
**源码使用方式**

开发环境 python 3.11

安装 pywebview 和 websockets

    pip install pywebview

    pip install websockets

启动
    
    python main.py


--------

**开发日志**

2024.01.31-2

（校验逻辑待完成）

- 开始拷贝的流程修改为只传递任务ID。
- 开始拷贝之前扫描文件夹文件数量和文件夹大小。
- 添加任务的开始时间和结束时间。
- 添加校验模式的选择。


2024.01.31-2

开始拷贝的流程待优化，现在传递参数过多，稍后修改为只传递任务ID即可。再往后需要加到队列中，使用队列进行拷贝。以及，优化任务的创建形式。

- 完成 新建项目、删除项目、新建任务、删除任务、开始拷贝、路径显示、创建时间的显示 等修改


2024.01.31

只完成了数据库的创建和python的修改，js的调用还存在问题
- 更换SQLite的方式存储数据



2024.01.30

更换SQLite的方式存储数据，替换现在的json方式
- 搞定更换pywebview之后获取文件夹的报错
- 修复目标路径的斜杠错误



2024.01.29
- 移除tkinter，采用pywebview方案获取文件夹(未搞定)
- 修复Mac端打不开的bug


2024.01.27
- 改为暗色模式


不记得日期的内容
- 美化界面，完成python的文件复制
- js获取python数据改为使用websockets获取
- 完成js操作后端python
- 写完html页面
- 测试 python + pywebview，成功运行