import sys
import music
from PyQt5.QtWidgets import (QApplication)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = music.MusicPlayer()
    sys.exit(app.exec_())