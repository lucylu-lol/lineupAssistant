import os
import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QLabel, QMenu, QAction
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMovie

from utils import LineupWidget, SettingsDialog, resource_path



class TransparentGIFWindow(QWidget):
    def __init__(self, gif_path):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(screen.width() * 0.8, screen.height() * 0.8, 200, 200)

        self.label = QLabel(self)
        self.movie = QMovie(gif_path)
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.setScaledSize(self.size())
        self.label.setMovie(self.movie)
        self.movie.start()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

        self.contextMenu = QMenu(self)
        lineupAction = QAction("阵容", self)
        lineupAction.triggered.connect(self.showLineupWindow)
        helpAction = QAction("帮助", self)
        helpAction.triggered.connect(self.showHelpDialog)
        exitAction = QAction("退出", self)
        exitAction.triggered.connect(self.close)
        self.contextMenu.addAction(lineupAction)
        self.contextMenu.addAction(helpAction)
        self.contextMenu.addAction(exitAction)

        self.drag_position = QPoint(0, 0)
        self.setMouseTracking(True)

        self.lineup_widget = LineupWidget(self)

        self.settings_dialog = SettingsDialog(self)

        self.initUI()

    def openMenu(self, position):
        self.contextMenu.exec_(self.mapToGlobal(position))

    def initUI(self):
        self.setWindowTitle('明日晴')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lineup_widget.show()
            event.accept()


    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def showLineupWindow(self):
        try:

            self.lineup_widget.show()
        except Exception as e:
            print(f"Error showing lineup widget: {e}")

    def showHelpDialog(self):
        try:
            self.settings_dialog.exec_()
        except Exception as e:
            print(f"Error showing settings dialog: {e}")

    def close(self):
        sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    name = os.listdir(resource_path("resources/role"))
    gif_path = os.path.join(resource_path("resources/role"), random.choice(name))
    window = TransparentGIFWindow(gif_path)
    window.show()

    sys.exit(app.exec_())
