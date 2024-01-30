# FileCopy
使用Python+pywebview+VUE3+HTML+JS+CSS制作的一款文件拷贝检验工具。

在没人大量恶意使用的情况下，可能会开源，可能免费



--------

**开发日志**

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