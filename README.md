# FileCopy（暂定）
使用Python+pywebview+websockets+VUE3+HTML+JS+CSS制作的一款文件拷贝检验工具。

**在没人大量恶意使用的情况下，可能会开源，可能免费**

--------

**目前正在开发中，暂不提供安装包，源码使用方式如下：**

开发环境： `python 3.11.x` 、`Vscode`

安装 `pywebview` 和 `websockets`

```
pip install pywebview
pip install websockets
```

启动
```
python main.py
```
--------

# 联系方式：
 
微信：CN-LXG



---------

# 开发版更新日志

仅作参考，记录一下每次的进度。

### [Dev] - 2024.02.03

待办：校验逻辑待添加

- 优化：扫描之后的文件夹大小和数量的显示
- 优化：创建时间、结束时间、用时的显示
- 更改：修改了不同状态下的颜色。


### [Dev] - 2024.01.31-2

待办：（校验逻辑待完成）

- 更改：开始拷贝的流程修改为只传递任务ID。
- 新增：开始拷贝之前扫描文件夹文件数量和文件夹大小。
- 新增：任务的开始时间和结束时间。
- 新增：校验模式的选择。


### [Dev] - 2024.01.31-2

~~待办1：开始拷贝的流程待优化，现在传递参数过多，稍后修改为只传递任务ID即可。~~
待办2：再往后需要加到队列中，使用队列进行拷贝。以及，优化任务的创建形式。

- 修复：新建项目、删除项目、新建任务、删除任务、开始拷贝、路径显示、创建时间的调用


### [Dev] - 2024.01.31

~~待办：只完成了数据库的创建和python的修改，js的调用还存在问题~~

- 修改：更换SQLite的方式存储数据

### [Dev] - 2024.01.30

- 更改：SQLite的方式存储数据，替换json方式

- 修复：更换pywebview获取文件夹方式之后的报错
- 修复：目标路径的斜杠错误


### [Dev] - 2024.01.29

- 修复：Mac端打不开的bug

- 移除：tkinter，采用pywebview方案获取文件夹(未搞定)


### [Dev] - 2024.01.27

- 更改：改为暗色模式


### [Dev] - 一些记不得日期的

- 新增：美化界面，完成python的文件复制
- 更改：js获取python数据改为使用websockets获取
- 新增：完成js操作后端python
- 新增：写完html页面
- 测试：python + pywebview，成功运行
- 新增：新建文件夹
