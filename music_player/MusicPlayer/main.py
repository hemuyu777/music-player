from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QMessageBox
from PyQt5.QtCore import Qt

import configparser
import os
import random
import time
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import (QWidget, QDesktopWidget, QMessageBox, QHBoxLayout, QVBoxLayout,
                                QSlider, QListWidget, QPushButton, QLabel, QFileDialog)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 初始化，界面设计
        self.setWindowTitle('登录酷狗音乐')
        self.setGeometry(800, 500, 400, 200)
        self.setWindowIcon(QIcon('resource/image/jiaobiao.png'))

        self.username_label = QLabel('用户名:', self)
        self.username_label.move(40, 20)

        self.username_edit = QLineEdit(self)
        self.username_edit.setPlaceholderText("请输入用户名")
        self.username_edit.move(120, 20)

        self.password_label = QLabel('密码:', self)
        self.password_label.move(40, 60)

        self.password_edit = QLineEdit(self)
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.move(120, 60)

        self.login_button = QPushButton('登录', self)
        self.login_button.move(100, 100)
        self.login_button.setStyleSheet("background-color:black;color:white")
        self.login_button.clicked.connect(self.check_login)

        self.forget_button = QPushButton('忘记密码', self)
        self.forget_button.move(250, 100)
        self.forget_button.setStyleSheet("background-color:black;color:white")
        self.forget_button.clicked.connect(self.forget)

    def check_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        if username == '禾木予' and password == '123456':
            self.close()
            self.main_window = MusicPlayer()
            self.main_window.show()
        else:
            QMessageBox.warning(self, '错误提示', '用户名或密码错误')

    def forget(self):
        QMessageBox.warning(self, '密码提示', '密码为：123456')

class MusicPlayer(QWidget):
    # 01初始化配置，界面设计
    def __init__(self):
        super().__init__()
        self.startTimeLabel = QLabel('00:00')
        self.endTimeLabel = QLabel('00:00')
        self.slider = QSlider(Qt.Horizontal, self)
        self.PlayModeBtn = QPushButton(self)
        self.playBtn = QPushButton(self)
        self.prevBtn = QPushButton(self)
        self.nextBtn = QPushButton(self)
        self.openBtn = QPushButton(self)
        self.musicList = QListWidget()
        self.musicList.setStyleSheet("QListWidget:item:selected:!active {background-color: yellow; color: blue;}")
        self.song_formats = ['mp3', 'm4a', 'flac', 'kgm', 'kgg']
        self.songs_list = []
        self.cur_playing_song = ''
        self.is_pause = True
        self.player = QMediaPlayer()
        self.is_switching = False
        self.playMode = 0
        self.settingfilename = 'config.ini'
        self.textLable = QLabel('播放方式')
        self.infoLabel = QLabel('音乐文件夹')

        self.playBtn.setStyleSheet("QPushButton{border-image: url(resource/image/play3.png)}")
        self.playBtn.setFixedSize(58, 58)
        self.nextBtn.setStyleSheet("QPushButton{border-image: url(resource/image/end3.png)}")
        self.nextBtn.setFixedSize(48, 48)
        self.prevBtn.setStyleSheet("QPushButton{border-image: url(resource/image/start3.png)}")
        self.prevBtn.setFixedSize(48, 48)
        self.openBtn.setStyleSheet("QPushButton{border-image: url(resource/image/open_file.png)}")
        self.openBtn.setFixedSize(34, 34)
        self.PlayModeBtn.setStyleSheet("QPushButton{border-image: url(resource/image/sequential.png)}")
        self.PlayModeBtn.setFixedSize(24, 24)

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.playByMode)

        self.hBoxSlider = QHBoxLayout()
        self.hBoxSlider.addWidget(self.startTimeLabel)
        self.hBoxSlider.addWidget(self.slider)
        self.hBoxSlider.addWidget(self.endTimeLabel)

        self.hBoxButton = QHBoxLayout()
        self.hBoxButton.addWidget(self.PlayModeBtn)
        self.hBoxButton.addStretch(1)
        self.hBoxButton.addWidget(self.prevBtn)
        self.hBoxButton.addWidget(self.playBtn)
        self.hBoxButton.addWidget(self.nextBtn)
        self.hBoxButton.addStretch(1)
        self.hBoxButton.addWidget(self.openBtn)

        self.vBoxControl = QVBoxLayout()
        self.vBoxControl.addLayout(self.hBoxSlider)
        self.vBoxControl.addLayout(self.hBoxButton)

        self.hBoxAbout = QHBoxLayout()
        self.hBoxAbout.addWidget(self.textLable)
        self.hBoxAbout.addStretch(1)
        self.hBoxAbout.addWidget(self.infoLabel)

        self.vboxMain = QVBoxLayout()
        self.vboxMain.addWidget(self.musicList)
        self.vboxMain.addLayout(self.vBoxControl)
        self.vboxMain.addLayout(self.hBoxAbout)

        self.setLayout(self.vboxMain)

        self.openBtn.clicked.connect(self.openMusicFloder)
        self.playBtn.clicked.connect(self.playMusic)
        self.prevBtn.clicked.connect(self.prevMusic)
        self.nextBtn.clicked.connect(self.nextMusic)
        self.musicList.itemDoubleClicked.connect(self.doubleClicked)
        self.slider.sliderMoved[int].connect(lambda: self.player.setPosition(self.slider.value()))
        self.PlayModeBtn.clicked.connect(self.playModeSet)

        # 加载配置文件
        self.loadingSetting()
        # 初始化界面
        self.initUI()

    # 02初始化界面
    def initUI(self):
        self.resize(800, 600)
        self.center()
        self.setWindowTitle('酷狗音乐播放')
        self.setWindowIcon(QIcon('resource/image/jiaobiao.png'))
        self.show()

    # 03窗口显示居中设置
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 04打开选择音乐文件夹
    def openMusicFloder(self):
        self.cur_path = QFileDialog.getExistingDirectory(self, "选择音乐文件夹", './')
        if self.cur_path:
            self.showMusicList()
            self.cur_playing_song = ''
            self.startTimeLabel.setText('00:00')
            self.endTimeLabel.setText('00:00')
            self.slider.setSliderPosition(0)
            self.updateSetting()
            self.is_pause = True
            self.playBtn.setStyleSheet("QPushButton{border-image: url(resource/image/play3.png)}")


    # 05显示音乐列表
    def showMusicList(self):
        self.musicList.clear()  # 清空之前的列表
        for song in os.listdir(self.cur_path):
            if song.split('.')[-1] in self.song_formats:
                self.songs_list.append([song, os.path.join(self.cur_path, song).replace('\\', '/')])
                self.musicList.addItem(song)
        self.musicList.setCurrentRow(0)
        if self.songs_list:
            self.cur_playing_song = self.songs_list[self.musicList.currentRow()][-1]

    # 06提示
    def Tips(self, message):
        QMessageBox.about(self, "温馨提示", message)

    # 07设置当前播放的音乐
    def setCurPlaying(self):
        self.cur_playing_song = self.songs_list[self.musicList.currentRow()][-1]
        self.player.setMedia(QMediaContent(QUrl(self.cur_playing_song)))

    # 08播放/暂停播放
    def playMusic(self):
        if self.musicList.count() == 0:
            self.Tips('当前路径无可播放的音乐文件')
            return
        if not self.player.isAudioAvailable():
            self.setCurPlaying()
        if self.is_pause or self.is_switching:
            self.player.play()
            self.is_pause = False
            self.playBtn.setStyleSheet("QPushButton{border-image: url(resource/image/pause3.png)}")
        elif (not self.is_pause) and (not self.is_switching):
            self.player.pause()
            self.is_pause = True
            self.playBtn.setStyleSheet("QPushButton{border-image: url(resource/image/play3.png)}")

    # 09上一首
    def prevMusic(self):
        self.slider.setValue(0)
        if self.musicList.count() == 0:
            self.Tips('当前路径无可播放的音乐文件')
            return
        pre_row = self.musicList.currentRow() - 1 if self.musicList.currentRow() != 0 else self.musicList.count() - 1
        self.musicList.setCurrentRow(pre_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False

    # 10下一首
    def nextMusic(self):
        self.slider.setValue(0)
        if self.musicList.count() == 0:
            self.Tips('当前路径无可播放的音乐文件')
            return
        next_row = self.musicList.currentRow() + 1 if self.musicList.currentRow() != self.musicList.count() - 1 else 0
        self.musicList.setCurrentRow(next_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False

    # 11双击歌曲名称播放音乐
    def doubleClicked(self):
        self.slider.setValue(0)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False

    # 12根据播放模式自动播放，并刷新进度条
    def playByMode(self):
        # 刷新进度条
        if (not self.is_pause) and (not self.is_switching):
            self.slider.setMinimum(0)
            self.slider.setMaximum(self.player.duration())
            self.slider.setValue(self.slider.value() + 1000)
        self.startTimeLabel.setText(time.strftime('%M:%S', time.localtime(self.player.position() / 1000)))
        self.endTimeLabel.setText(time.strftime('%M:%S', time.localtime(self.player.duration() / 1000)))
        # 顺序播放
        if (self.playMode == 0) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.nextMusic()
        # 单曲循环
        elif (self.playMode == 1) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.setCurPlaying()
                self.slider.setValue(0)
                self.playMusic()
                self.is_switching = False
        # 随机播放
        elif (self.playMode == 2) and (not self.is_pause) and (not self.is_switching):
            if self.musicList.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.musicList.setCurrentRow(random.randint(0, self.musicList.count() - 1))
                self.setCurPlaying()
                self.slider.setValue(0)
                self.playMusic()
                self.is_switching = False

    # 13更新配置文件
    def updateSetting(self):
        config = configparser.ConfigParser()
        config.read(self.settingfilename)
        if not os.path.isfile(self.settingfilename):
            config.add_section('MusicPlayer')
        config.set('MusicPlayer', 'PATH', self.cur_path)
        config.write(open(self.settingfilename, 'w'))

    # 14加载配置文件
    def loadingSetting(self):
        config = configparser.ConfigParser()
        config.read(self.settingfilename)
        if not os.path.isfile(self.settingfilename):
            return
        self.cur_path = config.get('MusicPlayer', 'PATH')
        self.showMusicList()

    # 15播放模式设置
    def playModeSet(self):
        # 设置为单曲循环模式
        if self.playMode == 0:
            self.playMode = 1
            self.PlayModeBtn.setStyleSheet("QPushButton{border-image: url(resource/image/circulation.png)}")
        # 设置为随机播放模式
        elif self.playMode == 1:
            self.playMode = 2
            self.PlayModeBtn.setStyleSheet("QPushButton{border-image: url(resource/image/random.png)}")
        # 设置为顺序播放模式
        elif self.playMode == 2:
            self.playMode = 0
            self.PlayModeBtn.setStyleSheet("QPushButton{border-image: url(resource/image/sequential.png)}")

    # 16退出
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '温馨提示', "您确定要退出播放吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication([])
    login_window = LoginWindow()
    login_window.show()
    app.exec_()