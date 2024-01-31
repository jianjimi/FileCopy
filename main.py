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

import subprocess
import sqlite3




global window

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


class Api:

    def __init__(self):
        self.database_file = 'filecopy.db'
        self.init_database()
        self.copy_statuses = {}  # 用于跟踪拷贝任务的状态

    def init_database(self):
        # 连接到SQLite数据库
        conn = sqlite3.connect(self.database_file)

        # 创建一个cursor对象
        cursor = conn.cursor()

        # 创建Projects表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Projects (
            project_id INTEGER PRIMARY KEY,
            project_name TEXT,
            creation_time DATETIME,
            project_status TEXT
        )
        ''')

        # 创建Tasks表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tasks (
            task_id INTEGER PRIMARY KEY,
            project_id INTEGER,
            task_name TEXT,
            source_path TEXT,
            destination_path TEXT,
            creation_time DATETIME,
            start_time DATETIME,
            end_time DATETIME,
            copy_status TEXT,
            verification_method TEXT,
            verification_status TEXT,
            file_size INTEGER,
            file_count INTEGER,
            FOREIGN KEY (project_id) REFERENCES Projects(project_id)
        )
        ''')

        # 创建Queue表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Queue (
            queue_id INTEGER PRIMARY KEY,
            task_id INTEGER,
            queue_order INTEGER,
            creation_time DATETIME,
            start_time DATETIME,
            end_time DATETIME,
            queue_status TEXT,
            FOREIGN KEY (task_id) REFERENCES Tasks(task_id)
        )
        ''')

        # 创建Task Logs表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Task_Logs (
            log_id INTEGER PRIMARY KEY,
            task_id INTEGER,
            project_id INTEGER,
            status TEXT,
            source_directory TEXT,
            destination_directory TEXT,
            file_size INTEGER,
            md5_value TEXT,
            xxhash_value TEXT,
            first_frame TEXT,
            middle_frame TEXT,
            last_frame TEXT,
            resolution TEXT,
            format TEXT,
            frame_rate TEXT,
            FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
            FOREIGN KEY (project_id) REFERENCES Projects(project_id)
        )
        ''')

        # 创建Messages表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Messages (
            message_id INTEGER PRIMARY KEY,
            task_id INTEGER,
            message_type TEXT,
            message_content TEXT,
            creation_time DATETIME,
            FOREIGN KEY (task_id) REFERENCES Tasks(task_id)
        )
        ''')

        # 插入默认项目（如果需要）
        cursor.execute("SELECT COUNT(*) FROM Projects")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Projects (project_name, creation_time, project_status) VALUES (?, ?, ?)", ("默认项目", datetime.now(), "未拷贝"))

        # 提交事务
        conn.commit()

        # 关闭连接
        conn.close()



    def add_task_to_project(self, project_id, task):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # 检查项目是否存在
        cursor.execute("SELECT * FROM Projects WHERE project_id=?", (project_id,))
        if cursor.fetchone() is None:
            conn.close()
            return "Project not found"

        # 添加任务到数据库
        cursor.execute('''
            INSERT INTO Tasks (project_id, task_name, source_path, destination_path, creation_time, start_time, end_time, copy_status, verification_method, verification_status, file_size, file_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, task['taskName'], task['sourcePath'], task['destinationPath'], datetime.now(), None, None, '未开始', task['verificationMethod'], '未校验', task['fileSize'], task['fileCount']))
        
        conn.commit()
        conn.close()
        return "Task added successfully"


        
    def update_task_status(self, project_id, task_id, new_status):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE Tasks SET copy_status = ? WHERE project_id = ? AND task_id = ?
        ''', (new_status, project_id, task_id))

        conn.commit()
        conn.close()
        return "Task status updated successfully"


        
    def get_project_details(self, project_id):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Projects WHERE project_id=?", (project_id,))
        project = cursor.fetchone()

        if project is None:
            conn.close()
            return {"error": "Project not found"}

        cursor.execute("SELECT * FROM Tasks WHERE project_id=?", (project_id,))
        tasks = [{'taskId': row[0], 'project_id': row[1], 'taskName': row[2], 'sourcePath': row[3], 'destinationPath': row[4], 'creationTime': row[5], 'startTime': row[6], 'endTime': row[7], 'copyStatus': row[8], 'verificationMethod': row[9], 'verificationStatus': row[10], 'fileSize': row[11], 'fileCount': row[12]} for row in cursor.fetchall()]

        project_details = {
            "projectID": project[0],
            "projectName": project[1],
            "creationTime": project[2],
            "projectStatus": project[3],
            "tasks": tasks
        }

        conn.close()
        return project_details


        
    def save_project(self, project_name):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # 添加新项目
        cursor.execute('''
            INSERT INTO Projects (project_name, creation_time, project_status)
            VALUES (?, ?, ?)
        ''', (project_name, datetime.now(), '未拷贝'))
        project_id = cursor.lastrowid

        conn.commit()
        conn.close()

        # 发送 WebSocket 消息通知项目已添加
        add_message = f"新建项目 '{project_name}' (ID: {project_id}) 成功"
        message_queue.put(add_message)

        return project_id



    def get_projects_list(self):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM projects")
        rows = cursor.fetchall()

        # 将每行数据转换为字典
        projects = []
        for row in rows:
            project = {
                "projectID": row[0],
                "projectName": row[1],
                "description": row[2],
                # 添加其他字段...
            }
            projects.append(project)

        conn.close()
        return {"projects": projects}

    def select_folder(self):
        result = window.create_file_dialog(
            webview.FOLDER_DIALOG, allow_multiple=False
        )
        print(result)
        
        return result


    def print_selected_folder(self, folder_path):
        message = f"Selected folder: {folder_path}"
        print(message)
        # message_queue.put(message)  # 将消息放入队列

    def delete_project(self, project_id):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # 检查项目是否存在
        cursor.execute("SELECT project_id FROM projects WHERE project_id=?", (project_id,))
        project = cursor.fetchone()
        if project is None:
            conn.close()
            return "Project not found or already deleted."

        # 删除项目
        cursor.execute("DELETE FROM projects WHERE project_id=?", (project_id,))
        conn.commit()
        conn.close()

        delete_message = f"项目 '{project[0]}' (ID: {project_id}) 已经被删除"
        message_queue.put(delete_message)
        return delete_message

        
    def delete_task(self, project_id, task_id):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # 删除任务
        cursor.execute("DELETE FROM tasks WHERE project_id=? AND task_id=?", (project_id, task_id))
        conn.commit()
        conn.close()

        message = f"任务 {task_id} 已被删除。"
        message_queue.put(message)
        return True


    

    def start_copy(self, projectID, taskId, sourcePath, destinationPath):
        try:
            # 开始拷贝
            self.update_task_status(projectID, taskId, "拷贝中")
            message = f"任务状态更新：开始拷贝任务 {taskId}，从 {sourcePath} 到 {destinationPath}"
            print(message)
            message_queue.put(message)

            # 执行文件拷贝
            shutil.copytree(sourcePath, destinationPath)

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
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        cursor.execute("SELECT task_status FROM tasks WHERE id=?", (taskId,))
        status = cursor.fetchone()
        conn.close()

        return status[0] if status else "未知任务"


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
    global window
    # 等待WebSocket服务器分配端口
    while server_info.port is None:
        time.sleep(0.1)

    websocket_port = server_info.port

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