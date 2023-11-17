from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QTextCursor, QIcon



class ReplaceDialog(QDialog):
    def __init__(self, parent, tab_textedit_data, current_tab_index):
        super().__init__(parent)
        self.tab_textedit_data = tab_textedit_data
        self.current_tab_index = current_tab_index
        self.counter = 0
        self.move(0, 0)

        # Load the search dialog UI
        uic.loadUi('./ui/replace_dialog.ui', self)
        self.setWindowIcon(QIcon('./ui/images/notepad.ico'))
        self.pushButton_3.clicked.connect(self.close)
        self.checkBox_2.setChecked(True)
        self.radioButton_2.setChecked(True)
        self.lineEdit.setFocus()

        self.show()