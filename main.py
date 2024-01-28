import tkinter as tk
from tkinter import filedialog
import webview
import threading
import queue
import json
import os
import shutil
from datetime import datetime
import asyncio
import websockets
import time

import sys
import io

import subprocess


# 全局变量
folder_request_queue = queue.Queue()
folder_response_queue = queue.Queue()
message_queue = queue.Queue()
connected_websockets = set()


class ServerInfo:
    def __init__(self):
        self.port = None

async def websocket_server(info, stop_event, port=0):
    async with websockets.serve(handler, "localhost", port) as server:
        info.port = server.sockets[0].getsockname()[1]
        print(f"WebSocket Server started on port {info.port}")
        stop_event_loop = asyncio.ensure_future(stop_event.wait())
        message_loop = asyncio.ensure_future(send_messages())
        done, pending = await asyncio.wait(
            [stop_event_loop, message_loop],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

async def handler(websocket, path):
    print("WebSocket connection attempt")
    connected_websockets.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_websockets.remove(websocket)
        print("WebSocket connection closed")


def start_server(info):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    stop_event = asyncio.Event()
    loop.create_task(websocket_server(info, stop_event))  # 改为 create_task
    loop.run_forever()  # 使用 run_forever 保持事件循环运行

async def send_messages():
    while True:
        if not message_queue.empty():  # 检查队列是否非空
            message = message_queue.get()
            print(f"Sending message: {message}")
            websockets_to_remove = set()
            for websocket in connected_websockets:
                try:
                    await websocket.send(message)
                    print(f"Message sent to WebSocket client: {message}")
                except Exception as e:
                    print(f"Error sending message: {e}")
                    websockets_to_remove.add(websocket)
            connected_websockets.difference_update(websockets_to_remove)
        else:
            await asyncio.sleep(1)  # 队列为空时等待



async def echo(websocket, path):
    async for message in websocket:
        print(f"发送 {message}")  # 打印发送的消息
        await websocket.send(message)


# 在一个新线程中启动WebSocket服务器
server_info = ServerInfo()
server_thread = threading.Thread(target=lambda: start_server(server_info), daemon=True)
server_thread.start()

# 在程序退出时关闭服务器
def close_server(stop_event):
    stop_event.set()

# 调用 close_server(stop_event) 来停止服务器


def tkinter_thread():
    root = tk.Tk()
    root.withdraw()

    while True:
        # 等待文件夹选择请求
        request = folder_request_queue.get()
        if request == 'select_folder':
            folder_path = filedialog.askdirectory(master=root)
            folder_response_queue.put(folder_path)

# 启动Tkinter线程
threading.Thread(target=tkinter_thread, daemon=True).start()


class Api:
    
    def __init__(self):
        self.data_folder = 'data'
        self.projects_folder = 'data/projects'
        self.projects_list_file = 'data/projectslist.json'
        self.init_app_data()
        self.copy_statuses = {}  # 用于跟踪拷贝任务的状态

    def init_app_data(self):
        # 创建data文件夹和projects文件夹（如果不存在）
        os.makedirs(self.data_folder, exist_ok=True)
        os.makedirs(self.projects_folder, exist_ok=True)

        # 检查是否需要创建默认项目
        if not os.path.exists(self.projects_list_file):
            default_project = {
                "projectID": "default",
                "projectName": "默认项目"
            }
            projects_list = {"projects": [default_project]}
            with open(self.projects_list_file, 'w') as file:
                json.dump(projects_list, file, indent=4)

            default_project_file = f'{self.projects_folder}/default.json'
            default_project_data = {
                "projectID": "default",
                "projectName": "默认项目",
                "tasks": []
            }
            with open(default_project_file, 'w') as file:
                json.dump(default_project_data, file, indent=4)

    def add_task_to_project(self, project_id, task):
        project_file = f'{self.projects_folder}/{project_id}.JSON'
        if os.path.exists(project_file):
            with open(project_file, 'r') as file:
                project_data = json.load(file)
            
            # 添加任务创建时间和校验状态
            task['copyStatus'] = '开始拷贝'  # 初始状态
            task['creationTime'] = datetime.now().timestamp()  # 创建时间戳
            task['verificationStatus'] = '未校验'  # 校验状态初始设置为 '未校验'
            project_data['tasks'].append(task)

            with open(project_file, 'w') as file:
                json.dump(project_data, file, indent=4)
            
            return "Task added successfully"
        else:
            return "Project not found"
        
    def update_task_status(self, project_id, task_id, new_status):
        project_file = f'{self.projects_folder}/{project_id}.JSON'
        if os.path.exists(project_file):
            with open(project_file, 'r') as file:
                project_data = json.load(file)

            for task in project_data['tasks']:
                if task['taskId'] == task_id:
                    task['copyStatus'] = new_status
                    break

            with open(project_file, 'w') as file:
                json.dump(project_data, file, indent=4)
            return "Task status updated successfully"
        else:
            return "Project not found"
        
    def get_project_details(self, project_id):
        project_file = f'{self.projects_folder}/{project_id}.JSON'
        if os.path.exists(project_file):
            with open(project_file, 'r') as file:
                project_details = json.load(file)
                return project_details
        else:
            return {"error": "Project not found"}
        
    def save_project(self, project_name):
        project_id = str(int(datetime.now().timestamp() * 1000))
        new_project = {
            "projectID": project_id,
            "projectName": project_name
        }

        # 加载现有项目列表
        with open(self.projects_list_file, 'r') as file:
            projects_list = json.load(file)

        # 更新项目列表
        projects_list["projects"].append(new_project)
        with open(self.projects_list_file, 'w') as file:
            json.dump(projects_list, file, indent=4)

        # 创建新项目的文件
        new_project_data = {
            "projectID": project_id,
            "projectName": project_name,
            "tasks": []
        }

        new_project_file = f'{self.projects_folder}/{project_id}.json'
        with open(new_project_file, 'w') as file:
            json.dump(new_project_data, file, indent=4)

        # 发送 WebSocket 消息通知项目已添加
        add_message = f"Project '{project_name}' (ID: {project_id}) has been added."
        message_queue.put(add_message)

        return project_id

    def get_projects_list(self):
        if os.path.exists(self.projects_list_file):
            with open(self.projects_list_file, 'r') as file:
                projects_list = json.load(file)
                return projects_list
        else:
            return {"projects": []}
    
    def select_folder(self):
        folder_request_queue.put('select_folder')
        folder_path = folder_response_queue.get()
        self.print_selected_folder(folder_path)  # 确保调用此方法
        return folder_path


    def print_selected_folder(self, folder_path):
        message = f"Selected folder: {folder_path}"
        print(message)
        # message_queue.put(message)  # 将消息放入队列

    def delete_project(self, project_id):
        # 删除项目列表中的对应项目
        project_list_path = self.projects_list_file
        project_deleted = False
        project_name = None

        if os.path.exists(project_list_path):
            with open(project_list_path, 'r') as file:
                projects_list = json.load(file)
            for project in projects_list['projects']:
                if project['projectID'] == project_id:
                    project_name = project['projectName']
                    break
            projects_list['projects'] = [p for p in projects_list['projects'] if p['projectID'] != project_id]
            with open(project_list_path, 'w') as file:
                json.dump(projects_list, file, indent=4)
            project_deleted = True

        # 删除对应的项目详情文件
        project_detail_file = f'{self.projects_folder}/{project_id}.JSON'
        if os.path.exists(project_detail_file):
            os.remove(project_detail_file)
            project_deleted = True

        # 发送 WebSocket 消息通知项目已删除
        if project_deleted and project_name:
            delete_message = f"Project '{project_name}' (ID: {project_id}) has been deleted."
            message_queue.put(delete_message)
            return delete_message
        else:
            return "Project not found or already deleted."
        
    def delete_task(self, project_id, task_id):
        project_file = f'{self.projects_folder}/{project_id}.json'
        if os.path.exists(project_file):
            with open(project_file, 'r') as file:
                project_data = json.load(file)

            # 过滤掉要删除的任务
            project_data['tasks'] = [task for task in project_data['tasks'] if task['taskId'] != task_id]

            # 重新写入更新后的项目数据
            with open(project_file, 'w') as file:
                json.dump(project_data, file, indent=4)
                message = f"任务 {task_id} 已被删除。"
                message_queue.put(message)
            return True
        else:
            return False

    

    def start_copy(self, projectID, taskId, sourceDirectory, targetDirectory):
        try:
            # 开始拷贝
            self.update_task_status(projectID, taskId, "拷贝中")
            message = f"任务状态更新：开始拷贝任务 {taskId}，从 {sourceDirectory} 到 {targetDirectory}"
            print(message)
            message_queue.put(message)

            # 执行文件拷贝
            shutil.copytree(sourceDirectory, targetDirectory)

            # 拷贝完成，更新状态为"已完成"
            self.update_task_status(projectID, taskId, "已完成")
            message = f"任务状态更新：任务 {taskId} 拷贝完成"
            print(message)
            message_queue.put(message)

            return "拷贝完成"
        except Exception as e:
            # 拷贝出错，更新状态为"出错"
            self.update_task_status(projectID, taskId, "出错")
            message = f"任务状态更新：任务 {taskId} 拷贝出错: {str(e)}"
            print(message)
            message_queue.put(message)

            return f"拷贝出错: {str(e)}"




    def get_copy_status(self, taskId):
        # 获取指定任务的拷贝状态
        return self.copy_statuses.get(taskId, "未知任务")

    def send_copy_status_to_html(self, taskId, status):
        message = f"任务 {taskId} 状态: {status}"
        message_queue.put(message)  # 将消息放入队列

    def pause_copy(self, task_id):
        # 实现暂停拷贝的逻辑
        message = f"暂停拷贝任务 {task_id}"
        message_queue.put(message)  # 将消息放入队列
        # 此处添加暂停逻辑
        return "拷贝暂停"
    
    def check_folder_empty(self, folder_path):
        try:
            if not os.path.exists(folder_path) or not os.listdir(folder_path):
                return {'isEmpty': True}
            else:
                return {'isEmpty': False}
        except Exception as e:
            message = f"Error checking folder: {str(e)}"
            message_queue.put(message)  # 将消息放入队列
            raise  # 继续抛出异常以供进一步处理

    def open_directory(self, path):
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', path])
        else:  # Linux 或其他
            subprocess.Popen(['xdg-open', path])
      

def main():
    # 等待WebSocket服务器分配端口
    while server_info.port is None:
        time.sleep(0.1)

    websocket_port = server_info.port  # 选择一个适合您应用的端口号

    api = Api()
    chinese = {'global.quitConfirmation': '确定关闭?'}

    window = webview.create_window(
        '文件拷贝校验工具',
        f'static/index.html?port={websocket_port}',
        
        js_api=api,
        width=1000,
        height=750,
        resizable=False,
        fullscreen=False,
        confirm_close=True,
        localization=chinese
    )

    webview.start(http_server=False, gui='edgechromium', debug=True, private_mode=True)

    sys.exit(0)

if __name__ == '__main__':
    main()