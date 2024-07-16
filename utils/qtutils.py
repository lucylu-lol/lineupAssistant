import os
import sys
import json
import pyperclip
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QToolTip, QMessageBox, QScrollArea, QVBoxLayout, QHBoxLayout, QDialog, QGridLayout
from PyQt5.QtCore import Qt, QEvent, QUrl, QPoint
from PyQt5.QtGui import QPixmap, QFont,QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        # 运行时的临时文件夹路径
        base_path = sys._MEIPASS
    else:
        # 未打包时的项目路径
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class InfoWidget(QLabel):
    def __init__(self, text1, image_path, text2, url, code_path, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.text1 = text1
        self.image_path = image_path
        self.text2 = text2
        self.url = url
        self.code_path = code_path

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 上方显示文本
        label1 = QLabel(self.text1)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        label1.setFont(font)
        layout.addWidget(label1)

        # 中间图片和应用按钮水平布局
        middle_layout = QHBoxLayout()

        # 中间显示图片
        if not os.path.exists(self.image_path):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"{self.image_path} 不存在！")
            msg.setWindowTitle("错误")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.exec_()

        pixmap = QPixmap(self.image_path)
        self.image_label = QLabel()
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

        self.image_label.mousePressEvent = self.showWebPage  # 点击事件
        middle_layout.addWidget(self.image_label)

        # 右侧应用按钮
        apply_button = QPushButton('应用')
        apply_button.setFixedSize(40, 30)
        apply_button.clicked.connect(self.copyCodeToClipboard)
        middle_layout.addWidget(apply_button)

        layout.addLayout(middle_layout)

        # 下方显示文本
        # label3 = QLabel(self.text2)
        # layout.addWidget(label3)
        self.setFixedHeight(200)
        self.load_json()

        self.setLayout(layout)
        self.installEventFilter(self)

    def load_json(self):
        try:
            with open(self.code_path, 'r', encoding="utf-8") as file:
                data = json.load(file)
                self.code = data.get('code', '')
                self.url = QUrl(data.get('url', ''))
        except Exception as e:
            print(f"Error copying code: {e}")

    def showWebPage(self, event):
        dialog = QWidget(self.parent.parent)

        screen = self.parent.screen()
        width = 600
        height = 400
        dialog.setGeometry(screen.size().width() // 2 - width // 2, screen.size().height() // 2 - height // 2, width, height)
        dialog.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        # dialog.setAttribute(Qt.WA_TranslucentBackground, True)
        dialog.setWindowTitle('攻略')

        web_view = QWebEngineView()
        web_view.load(self.url)

        layout = QVBoxLayout()
        layout.addWidget(web_view)
        dialog.setLayout(layout)
        dialog.resize(800, 600)  # 设置窗口大小
        dialog.show()

    def copyCodeToClipboard(self):
        try:
            pyperclip.copy(self.code)

            QToolTip.showText(self.image_label.mapToGlobal(QPoint(self.image_label.width() // 2, self.image_label.height() // 2)), "复制成功", self)

            print("Code copied to clipboard.")
        except Exception as e:
            print(f"Error copying code: {e}")

    def eventFilter(self, source, event):
        if event.type() == QEvent.Resize and source is self:
            self.adjustImageSize()
        return super().eventFilter(source, event)

    def adjustImageSize(self):
        pixmap = QPixmap(self.image_path)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))


class LineupWidget(QWidget):
    def __init__(self, parent):
        super(LineupWidget, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle('阵容图 by 明日晴')
        self.setWindowIcon(QIcon(resource_path("resources/icon.jpg")))
        screen = self.parent.screen()
        # 设置窗口大小和位置
        width, height = 570, 800
        self.setGeometry(screen.size().width() // 2 - width // 2, screen.size().height() // 2 - height // 2, width, height)
        layout = QVBoxLayout()

        # 添加快捷链接

        self.shortcut_layout = QGridLayout()
        self.shortcut_buttons = []
        layout.addLayout(self.shortcut_layout)

        # 添加多条信息
        self.scroll_area = QScrollArea()
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        custom_path = "./lineup"
        lineup_nums = 0
        if os.path.exists(custom_path):
            try:
                for index, item in enumerate(os.listdir(custom_path)):
                    text1 = item
                    img_path = os.path.join(custom_path, text1, "lineup.png")
                    description = ""
                    code_path = os.path.join(custom_path, text1, "code.json")
                    self.info = InfoWidget(text1, img_path, description, QUrl(), code_path, self)
                    self.scroll_layout.addWidget(self.info)

                    # 创建快捷按钮
                    shortcut_button = QPushButton(text1, self)
                    shortcut_button.clicked.connect(lambda checked, idx=index: self.scrollToWidget(idx))
                    self.shortcut_buttons.append(shortcut_button)
                    self.shortcut_layout.addWidget(shortcut_button, index // 4, index % 4)  # 每行4个按钮
                    lineup_nums = index+1
            except Exception as E:
                print(f"ERROR:{E}")

        path = resource_path("resources/lineup")
        try:
            for index, item in enumerate(os.listdir(path)):
                text1 = item
                img_path = os.path.join(path, text1, "lineup.png")
                description = ""
                code_path = os.path.join(path, text1, "code.json")
                self.info = InfoWidget(text1, img_path, description, QUrl(), code_path, self)
                self.scroll_layout.addWidget(self.info)

                # 创建快捷按钮
                shortcut_button = QPushButton(text1, self)
                shortcut_button.clicked.connect(lambda checked, idx=(index+lineup_nums): self.scrollToWidget(idx))
                self.shortcut_buttons.append(shortcut_button)
                self.shortcut_layout.addWidget(shortcut_button, (lineup_nums+index) // 4, (lineup_nums+index) % 4)  # 每行4个按钮
        except Exception as E:
            print(f"ERROR:{E}")

        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)

        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def scrollToWidget(self, index):
        scroll_bar = self.scroll_area.verticalScrollBar()
        # self.height()
        widget_height = self.info.height()  # InfoWidget 的固定高度
        target_position = index * widget_height
        scroll_bar.setValue(target_position)

    def closeEvent(self, event):
        event.ignore()
        self.hide()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("帮助 by 明日晴")
        self.setWindowIcon(QIcon(resource_path("resources/icon.jpg")))

        screen = parent.screen()

        # 设置窗口大小和位置
        width, height = 600, 250
        self.setGeometry(screen.size().width() // 2 - width // 2, screen.size().height() // 2 - height // 2, width, height)

        # 整体布局
        main_layout = QHBoxLayout(self)

        # 左边布局（文字和图片）
        left_layout = QVBoxLayout()
        text_label = QLabel("""
添加阵容：
新建lineup文件夹，在lineup文件夹下新建阵容文件夹，
命名为阵容名称,如天龙鹿娜，添加缩略图lineup.png，和code.json
code.json中code对应阵容分享码，url对应阵容攻略，来自于云顶助手
        """)
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignLeft)
        left_layout.addWidget(text_label)

        pixmap = QPixmap(resource_path("resources/code.png"))
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(True)
        left_layout.addWidget(image_label)

        pixmap2 = QPixmap(resource_path("resources/help.png"))
        image_label = QLabel()
        image_label.setPixmap(pixmap2)
        image_label.setScaledContents(True)
        left_layout.addWidget(image_label)
        main_layout.addLayout(left_layout)

        # 右边布局（两行文字和图片）
        right_layout = QVBoxLayout()

        # 第一行文字
        right_text_layout = QHBoxLayout()
        additional_text_label1 = QLabel("联系")
        additional_text_label1.setAlignment(Qt.AlignCenter)
        right_text_layout.addWidget(additional_text_label1)

        # 第二行文字
        additional_text_label2 = QLabel("赞助")
        additional_text_label2.setAlignment(Qt.AlignCenter)
        right_text_layout.addWidget(additional_text_label2)
        right_layout.addLayout(right_text_layout)

        # 第一行图片
        right_img_layout = QHBoxLayout()
        pixmap2 = QPixmap(resource_path(resource_path("resources/support/wechat.png"))).scaled(300, 300, Qt.KeepAspectRatio)
        image_label2 = QLabel()
        image_label2.setPixmap(pixmap2)
        image_label2.setAlignment(Qt.AlignCenter)
        image_label2.setScaledContents(True)
        right_img_layout.addWidget(image_label2)

        # 第二行图片
        pixmap3 = QPixmap(resource_path(resource_path("resources/support/wechat_pay.png"))).scaled(300, 300, Qt.KeepAspectRatio)
        image_label3 = QLabel()
        image_label3.setPixmap(pixmap3)
        image_label3.setAlignment(Qt.AlignCenter)
        image_label3.setScaledContents(True)
        right_img_layout.addWidget(image_label3)
        right_layout.addLayout(right_img_layout)

        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)