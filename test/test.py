import webview


class Api:

    def getRandomNumber(self):
        result = window.create_file_dialog(
            webview.FOLDER_DIALOG
        )
        print(result)


if __name__ == '__main__':
    api = Api()
    window = webview.create_window('JS API example', 'index.html',  js_api=api,)
    webview.start()