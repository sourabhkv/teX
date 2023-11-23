from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QTextCursor, QIcon



class SearchDialog(QDialog):
    def __init__(self, parent, tabdata):
        super().__init__(parent)
        self.text_edit = tabdata.text_edit
        self.counter = 0
        self.move(0, 0)

        # Load the search dialog UI
        uic.loadUi('./ui/Search_dialog.ui', self)

        # Dialog settings
        self.setWindowTitle('Search Dialog')
        self.setWindowIcon(QIcon('./ui/images/notepad.ico'))

        # Connect the textChanged signal to find_text method
        self.lineEdit.textChanged.connect(self.find_text)

        # Disconnect returnPressed signal only if there are existing connections
        existing_connections = self.lineEdit.receivers(self.lineEdit.returnPressed)
        if existing_connections > 0:
            self.lineEdit.returnPressed.disconnect()

        # Connect the returnPressed signal to a lambda function that calls select_word
        self.lineEdit.returnPressed.connect(lambda: self.select_word)

        # Connect other signals and set up the UI
        self.pushButton.clicked.connect(lambda: self.select_word())
        self.pushButton_2.clicked.connect(self.close)
        self.checkBox_2.setChecked(True)
        self.radioButton_2.setChecked(True)
        self.lineEdit.setFocus()
        self.lineEdit.setPlaceholderText('Enter text')
        self.pushButton.setEnabled(False)
        self.status_label.setText('Enter word')
        self.show()

    
    def find_text(self):
        if self.checkBox.isChecked():
            __text = self.lineEdit.text()
            __main_text = self.text_edit.toPlainText()
        else:
            __text = self.lineEdit.text().lower()
            __main_text = self.text_edit.toPlainText().lower()
        if __text == '':
            self.status_label.setText('Enter word')
        else:
            __count = __main_text.count(__text)
            if __count:
                self.status_label.setText(f'{__text} Occurance : {__count}')
                self.find_substring_indexes()
                self.pushButton.setEnabled(True)
            else:
                error_box = QMessageBox()
                error_box.setWindowIcon(QIcon('./ui/images/notepad.ico'))
                error_box.setIcon(QMessageBox.Critical)
                error_box.setWindowTitle("teX")
                error_box.setText("No match found")
                error_box.setStandardButtons(QMessageBox.Ok)
                error_box.exec_()
    
    def select_word(self):
        __length = len(self.lineEdit.text())
        self.counter = self.counter % len(self.indexes)
        __start = self.indexes[self.counter]

        cursor = self.text_edit.textCursor()
        cursor.setPosition(__start, QTextCursor.MoveAnchor)  # Move the cursor to start

        # Select the word
        if self.checkBox_2.isChecked():
            cursor.setPosition(__start + __length, QTextCursor.KeepAnchor)  # Move the cursor to end while keeping the anchor
            self.text_edit.setTextCursor(cursor)
        
        self.status_label.setText(f'{self.counter+1} of {len(self.indexes)}')

        self.text_edit.setFocus()

        if self.radioButton_2.isChecked():
            self.counter += 1
        else:
            self.counter -= 1
    
    def find_substring_indexes(self):
        if self.checkBox.isChecked():
            input_string = self.text_edit.toPlainText()
            substring = self.lineEdit.text()
        else:
            input_string = self.text_edit.toPlainText().lower()
            substring = self.lineEdit.text().lower()
        self.indexes = []
        start_index = 0

        while start_index < len(input_string):
            index = input_string.find(substring, start_index)

            if index == -1:
                break

            self.indexes.append(index)
            start_index = index + 1
    
    def find_next(self):
        self.select_word()