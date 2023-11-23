from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QIcon

class GoToDialog(QDialog):
    def __init__(self, parent, current_tab):
        super().__init__(parent)
        self.__current_tab = current_tab
        self.tab_textedit_data = current_tab.text_edit.toPlainText()

        # Load the search dialog UI
        uic.loadUi('./ui/goto.ui', self)
        self.setWindowIcon(QIcon('./ui/images/notepad.ico'))
        self.pushButton_2.clicked.connect(self.close)
        self.lineEdit.setFocus()
        self.__text = 1
        self.lineEdit.textChanged.connect(self.check_digit)
        self.lineEdit.returnPressed.connect(lambda: self.move_cursor_to_start_of_line(self.__text))
        self.pushButton.clicked.connect(lambda: self.move_cursor_to_start_of_line(self.__text))
        self.show()
    
    def check_digit(self):
        try:
            self.__text = int(self.lineEdit.text())
            if self.__text <= len(self.tab_textedit_data.split('\n')):
                self.pushButton.setEnabled(True)
            else:
                self.pushButton.setEnabled(False)
        except:
            self.pushButton.setEnabled(False)
    
    def move_cursor_to_start_of_line(self, line_number):
        text = self.__current_tab.text_edit.toPlainText()
        lines = text.split('\n')
        pos = sum(len(line) + 1 for line in lines[:line_number-1])  # +1 for '\n'

        cursor = self.__current_tab.text_edit.textCursor()
        cursor.setPosition(pos)
        self.__current_tab.text_edit.setTextCursor(cursor)
        self.close()