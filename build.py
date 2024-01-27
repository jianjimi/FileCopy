import PyInstaller.__main__

PyInstaller.__main__.run([
    '--name=%s' % '剪辑迷-文件拷贝校验工具0.0.1', # 打包之后的应用名称
    # '--onefile', # 单文件
    '--onedir', # 单文件加目录
    '--windowed',
    '--add-data=%s' % 'static;static',  # 需要复制的额外文件或文件夹
    '--icon=%s' % 'static/img/app_icon.ico',  # 设置图标
    '--version-file=%s' % 'version_info.txt',
    'main.py',  # 您的主Python脚本文件
])
