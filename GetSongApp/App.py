import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from UI import Ui_MainWindow  # 导入由UI文件生成的类
from GetSongDetails import getsong
from PyQt5 import QtWidgets
import requests


class Worker(QObject):
    finished = pyqtSignal(list)

    def __init__(self, songname, songresource):
        super().__init__()
        self.songname = songname
        self.songresource = songresource

    def run(self):
        li_songs, li_singers, li_contents = getsong(self.songname, self.songresource)
        self.finished.emit([li_songs, li_singers, li_contents])


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 使用UI类创建窗口
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.Search.clicked.connect(self.SearchButtonClicked)

        # 创建工作线程和线程对象
        self.worker = None
        self.thread = None

    def SearchButtonClicked(self):
        # 如果之前有线程在运行，先停止它
        if self.thread and self.thread.isRunning():
            QMessageBox.warning(self, "警告", "上一个搜索任务正在进行，请稍后再试！")
            return

        # 获取用户输入的歌曲名
        songname = self.ui.SongName.text().strip()  # 去除首尾空格

        # 获取用户选择的音乐资源
        if self.ui.WYYMusic.isChecked():
            songresource = "netease"
        elif self.ui.QQMusic.isChecked():
            songresource = "qq"
        elif self.ui.KuGouMusic.isChecked():
            songresource = "kugou"
        else:
            songresource = None

        # 检查输入框和选择按钮是否都有内容
        if not songname or not songresource:
            QMessageBox.warning(self, "警告", "请填写歌曲名称并选择音乐资源！")
            return

        # 创建并启动工作线程
        self.worker = Worker(songname, songresource)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handleResults)
        self.thread.start()

    def handleResults(self, results):
        # 处理工作线程完成后的结果
        li_songs, li_singers, li_contents = results
        if not li_songs and not li_singers and not li_contents:
            QMessageBox.warning(self, "警告", "查找的音乐内容为空，请用其他通道！")
        else:
            self.load_data_to_table(li_songs, li_singers, li_contents)

    def load_data_to_table(self, li_songs, li_singers, li_contents):
        # 如果上一个工作线程正在运行，停止它
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        # 清空表格内容
        self.ui.DisplayTable.clearContents()

        # 设置表格行数
        row_count = max(len(li_songs), len(li_singers), len(li_contents))
        self.ui.DisplayTable.setRowCount(row_count)

        # 将数据加载到表格中
        for i in range(row_count):
            self.ui.DisplayTable.setItem(i, 0, QtWidgets.QTableWidgetItem(li_songs[i] if i < len(li_songs) else ""))
            self.ui.DisplayTable.setItem(i, 1, QtWidgets.QTableWidgetItem(li_singers[i] if i < len(li_singers) else ""))
            self.ui.DisplayTable.setItem(i, 2,
                                         QtWidgets.QTableWidgetItem(li_contents[i] if i < len(li_contents) else ""))
            # 添加按钮到第四列
            download_button = QtWidgets.QPushButton("下载")
            download_button.clicked.connect(lambda _, row=i: self.download_content(row))
            self.ui.DisplayTable.setCellWidget(i, 3, download_button)

    def download_content(self, row):
        # 获取第一列和第二列的内容，假设是歌曲名和歌手名
        song_item = self.ui.DisplayTable.item(row, 0)
        singer_item = self.ui.DisplayTable.item(row, 1)
        if song_item is None or singer_item is None:
            return

        song_name = song_item.text()
        singer_name = singer_item.text()

        # 获取第三列的内容，假设是网址
        url_item = self.ui.DisplayTable.item(row, 2)
        if url_item is None:
            return

        url = url_item.text()

        # 下载操作
        try:
            response = requests.get(url)
            # 假设你想将下载的内容保存到文件中，文件名用歌曲名和歌手名组成
            with open(f"{song_name}_{singer_name}.mp3", "wb") as f:
                f.write(response.content)
            QMessageBox.information(self, "下载完成", f"{song_name} - {singer_name} 下载完成！")
        except Exception as e:
            QMessageBox.warning(self, "下载失败", f"{song_name} - {singer_name} 下载失败：{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MyMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
