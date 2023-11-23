from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QTextCursor, QIcon, QTextDocument



class ReplaceDialog(QDialog):
    def __init__(self, parent, current_tab):
        super().__init__(parent)
        self.__current_tab = current_tab
        self.tab_textedit_data = current_tab.text_edit.toPlainText()
        self.counter = 0
        self.move(0, 0)

        # Load the search dialog UI
        uic.loadUi('./ui/replace_dialog.ui', self)
        self.setWindowIcon(QIcon('./ui/images/notepad.ico'))
        self.pushButton_3.clicked.connect(self.close)
        self.checkBox_2.setChecked(True)
        self.radioButton_2.setChecked(True)
        self.lineEdit.setFocus()
        self.pushButton_2.clicked.connect(self.replace_all)
        self.pushButton.clicked.connect(self.replace_next)

        self.show()
    
    def replace_all(self):
        __text1 = self.lineEdit.text()
        __text2 = self.lineEdit_2.text()

        if __text1 != '' and __text2 != '':
            cursor = self.__current_tab.text_edit.textCursor()
            cursor.beginEditBlock()

            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
            cursor.insertText(cursor.selectedText().replace(__text1, __text2))

            cursor.endEditBlock()

            self.__current_tab.text_edit.setTextCursor(cursor)
            self.__current_tab.text_edit.ensureCursorVisible()
    
    def replace_next(self):
        __text1 = self.lineEdit.text()
        __text2 = self.lineEdit_2.text()

        if __text1 != '' and __text2 != '':
            # Get the QTextEdit object
            text_edit = self.__current_tab.text_edit

            # Create a QTextDocument.FindFlag
            find_flags = QTextDocument.FindFlags()

            # Find the next occurrence of __text1
            found = text_edit.find(__text1, find_flags)

            if found:
                # Replace the selected text with __text2
                text_edit.textCursor().insertText(__text2)

                # Ensure the cursor is visible
                text_edit.ensureCursorVisible()
            else:
                # No more occurrences found, close the dialog
                self.close()