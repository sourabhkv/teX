from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap

class About(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__version__ = 1.2
        self.setWindowIcon(QIcon('./ui/images/notepad.ico'))
        pixmap = QPixmap("./ui/images/notepad.png")
        self.setIconPixmap(pixmap)
        label = QLabel()
        label.setOpenExternalLinks(True)  # Enable opening links externally
        label.setText(f"Text Editor X<br>Developed by <a href='https://github.com/sourabhkv'>sourabhkv</a><br>Version: {self.__version__}")
        self.layout().addWidget(label)
        self.setWindowTitle("About")
        self.addButton(QMessageBox.Ok)
        self.exec()