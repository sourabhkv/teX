from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont, QTextCharFormat, QIcon, QPixmap
from PyQt5.QtTest import QTest
import sys
import os
from datetime import datetime
from PyQt5.QtCore import QTimer
import chardet
import json

class MyGUI(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MyGUI, self).__init__()
        self.__version__ = 1.05
        self.tab_count = -1
        self.tab_data = []
        self.tab_textedit_data = []
        self.save_status = []
        self.file_encoding = []
        uic.loadUi('text_editor.ui', self)
        icon = QIcon('notepad.ico')
        self.setWindowIcon(icon)
        self.setWindowTitle('Text editor x')
        self.dark_theme_enabled = False
        self.zoom_level = 100

        try:
            with open('settings.json','r') as file:
                self.settings_data = json.load(file)
        except FileNotFoundError:
            sys.exit(0)
        except json.JSONDecodeError as e:
            sys.exit(0)
        

        if len(args) > 1:
            for i in args[1:]:
                with open(i,"r") as file:
                    self.add_new_tab(tabname=str(i),text = file.read(), filename = i)
                    
        else:
            self.add_new_tab(tabname="Untitled")
        
        self.setAcceptDrops(True)

        self.actionNew_tab.triggered.connect(lambda: self.add_new_tab("Untitled"))

        self.actionClose_tab.triggered.connect(self.close_tab)

        self.actionOpen.triggered.connect(self.open_file)

        self.actionSave.triggered.connect(self.save_file)

        self.actionZoom_in.triggered.connect(self.zoom_in)

        self.actionZoom_out_2.triggered.connect(self.zoom_out)

        self.actiontime_date.triggered.connect(self.time_date)

        self.actionSave_As.triggered.connect(self.save_as_file)

        self.actionFont_size.triggered.connect(self.open_font_picker)

        self.tabWidget.tabCloseRequested.connect(self.close_tab)

        self.actionRestore_default_zoom.triggered.connect(self.restore_font)

        self.actionNew_Window.triggered.connect(self.create_new_window)

        self.actionClose_window.triggered.connect(self.closeEvent)

        self.tabWidget.currentChanged.connect(self.update_cursor)

        self.actionDark_Theme.triggered.connect(self.dark_theme)

        self.actionAbout.triggered.connect(self.about)

        self.statusBar().showMessage(f"Ln 1 , Col 1")

        self.setStyleSheet(self.settings_data['theme']['light-theme']['window'])

        self.menubar.setStyleSheet("")

        self.permanent_label = QLabel(f"   {self.zoom_level} %  ")
        self.statusbar.addPermanentWidget(self.permanent_label)
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.VLine)
        self.separator.setFrameShadow(QFrame.Sunken)

        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.VLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        

        self.permanent_label2 = QLabel("   ASCII   ")
        self.statusbar.addPermanentWidget(self.permanent_label2)

        if self.settings_data['always-show-maximized']:
            self.showMaximized()


        
        self.show()

    def add_new_tab(self, tabname, text = '', filename = None):
        self.tab_data.append(QWidget())
        self.tabWidget.addTab(self.tab_data[-1], tabname)
        self.tab_count += 1
        self.tabWidget.setCurrentIndex(self.tab_count)
        self.tab_textedit_data.append(QPlainTextEdit(self.tab_data[-1]))

        if text == '' and filename is None:
            self.save_status.append(False)
            self.file_encoding.append('   ASCII   ')
        elif text!='' and filename is not None:
            self.save_status.append(True)
            with open(filename,'rb') as __file:
                self.detect_encoding(__file.read())

        plain_text_edit = self.tab_textedit_data[-1]
        layout = QVBoxLayout()
        layout.addWidget(plain_text_edit)
        plain_text_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        plain_text_edit.setPlainText(text)
        self.tab_data[-1].setLayout(layout)
        plain_text_edit.setFocus()
        plain_text_edit.installEventFilter(self)
        plain_text_edit.textChanged.connect(self.handle_text_changed)

        font = QFont(self.settings_data["default-font"], self.settings_data["default-font-size"])
        plain_text_edit.setFont(font)
        
        QTimer.singleShot(0, lambda: self.set_scrollbar_value(plain_text_edit))
    
    def handle_text_changed(self):   # mark * with unsaved files
        if self.tabWidget.tabText(self.tabWidget.currentIndex())!='Untitled' and not self.tabWidget.tabText(self.tabWidget.currentIndex()).endswith('•'):
            self.save_status[self.tabWidget.currentIndex()] = False
            self.tabWidget.setTabText(self.tabWidget.currentIndex(), self.tabWidget.tabText(self.tabWidget.currentIndex())+"•")
            

    def set_scrollbar_value(self, plain_text_edit):
        plain_text_edit.verticalScrollBar().setSingleStep(2)
        plain_text_edit.verticalScrollBar().setPageStep(10)
        plain_text_edit.cursorPositionChanged.connect(self.update_cursor_position)
        if not self.dark_theme_enabled:
            plain_text_edit.setStyleSheet(self.settings_data['theme']['dark-theme']['text-edit-stylesheet'])
        else: #light theme
            plain_text_edit.setStyleSheet(self.settings_data['theme']['light-theme']['text-edit-stylesheet'])
    
    def close_tab(self,tab_index):
        if self.tab_count != 0:
            if len(self.tab_textedit_data[tab_index].toPlainText())==0 and self.tabWidget.tabText(tab_index)=='Untitled' and not self.tabWidget.tabText(tab_index).endswith('•'):
                self.tab_data.pop(tab_index)
                self.tab_textedit_data.pop(tab_index)
                self.tabWidget.removeTab(tab_index)
                self.save_status.pop(tab_index)
                self.file_encoding.pop(tab_index)
                self.tab_count -= 1
                self.tab_textedit_data[self.tabWidget.currentIndex()].setFocus()
            else:
                if len(self.tab_textedit_data[tab_index].toPlainText())!=0 and self.tabWidget.tabText(tab_index)=='Untitled':
                    dialog = QMessageBox()
                    dialog.setWindowIcon(QIcon('notepad.ico'))
                    dialog.setText("Do you want to save your work?")
                    dialog.addButton(QPushButton("Yes"), QMessageBox.AcceptRole)
                    dialog.addButton(QPushButton("No"), QMessageBox.RejectRole)
                    dialog.addButton(QPushButton("Cancel"), QMessageBox.RejectRole)
                    answer = dialog.exec_()
                    if answer == 0:
                        self.save_file()
                    else:
                        pass
                
                self.tab_data.pop(tab_index)
                self.file_encoding.pop(tab_index)
                self.tab_textedit_data.pop(tab_index)
                self.save_status.pop(tab_index)
                self.tabWidget.removeTab(tab_index)
                self.tab_count -= 1
                try:
                    self.tab_textedit_data[tab_index-1].setFocus()
                except:
                    pass
        else:
            if len(self.tab_textedit_data[tab_index].toPlainText())!=0 and self.tabWidget.tabText(tab_index)=='Untitled' or self.tabWidget.tabText(tab_index).endswith('•'):
                    dialog = QMessageBox()
                    dialog.setWindowIcon(QIcon('notepad.ico'))
                    dialog.setText("Do you want to save your work?")
                    dialog.addButton(QPushButton("Yes"), QMessageBox.AcceptRole)
                    dialog.addButton(QPushButton("No"), QMessageBox.RejectRole)
                    dialog.addButton(QPushButton("Cancel"), QMessageBox.RejectRole)
                    answer = dialog.exec_()
                    if answer == 0:
                        self.save_file()
                    else:
                        pass
            sys.exit(0)
    
    def detect_encoding(self,rawdata):
        result = chardet.detect(rawdata)
        encoding = result['encoding']
        confidence = result['confidence']
        try:
            if encoding:
                self.file_encoding.append(f'   {encoding.upper()}   ')
        except:
            self.file_encoding.append('   ASCII   ')
    
    def about(self):
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QIcon('notepad.ico'))
        pixmap = QPixmap("notepad.png")
        msgBox.setIconPixmap(pixmap)
        msgBox.setText(f"Text Editor X\nDeveloped by sourabhkv\nVersion : {self.__version__}")
        msgBox.setWindowTitle("About")
        msgBox.addButton(QMessageBox.Ok)
        msgBox.exec()


    def open_file(self):
        _text = self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText()
        if _text=="":
            options_ = QFileDialog.Options()
            filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", self.settings_data['open-file-types'], options=options_)
            if filename != "":
                with open(filename, "r") as file:
                    self.tab_textedit_data[self.tabWidget.currentIndex()].setPlainText(file.read())
                self.tabWidget.setTabText(self.tabWidget.currentIndex(), filename)
        
        else:
            options_ = QFileDialog.Options()
            filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", self.settings_data['open-file-types'], options=options_)
            if filename != "":
                self.add_new_tab(filename)
                with open(filename, "r") as file:
                    self.tab_textedit_data[self.tabWidget.currentIndex()].setPlainText(file.read())
    
    def save_file(self):
        __text = self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText()
        if __text!="" and not self.save_status[self.tabWidget.currentIndex()]:
            __tabname = self.tabWidget.tabText(self.tabWidget.currentIndex())
            if __tabname=="Untitled":
                options = QFileDialog.Options()
                filename, _ = QFileDialog.getSaveFileName(self, "Save file", "", self.settings_data['open-file-types'], options=options)
                if filename != "":
                    with open(filename, "w") as file:
                        file.write(self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText())
                        self.tab_textedit_data[self.tabWidget.currentIndex()].clear()
                        self.tab_textedit_data[self.tabWidget.currentIndex()].setPlainText(__text)
                    
                    self.tabWidget.setTabText(self.tabWidget.currentIndex(), filename)
        
            else:
                if os.path.exists(__tabname):
                    with open(__tabname, "w") as file:
                        file.write(self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText())
                elif __tabname.endswith('•'):
                    with open(__tabname[:-1], "w") as file:
                        file.write(self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText())
                        self.tab_textedit_data[self.tabWidget.currentIndex()].clear()
                        self.tab_textedit_data[self.tabWidget.currentIndex()].setPlainText(__text[:-1])
                        self.tabWidget.setTabText(self.tabWidget.currentIndex(), __tabname[:-1])
                        self.save_status[self.tabWidget.currentIndex()] = True
                else:
                    self.tabWidget.setTabText(self.tabWidget.currentIndex(), "Untitled")
    
    def save_as_file(self):
        __text = self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText()
        if __text!="":
            options = QFileDialog.Options()
            filename, _ = QFileDialog.getSaveFileName(self, "Save As file", "", self.settings_data['open-file-types'], options=options)
            if filename != "":
                with open(filename, "w") as file:
                    file.write(self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText())
                    self.tab_textedit_data[self.tabWidget.currentIndex()].clear()
                    self.tab_textedit_data[self.tabWidget.currentIndex()].setPlainText(__text)
                self.tabWidget.setTabText(self.tabWidget.currentIndex(), filename)


    def update_cursor_position(self):
        self.tab_textedit_data[self.tabWidget.currentIndex()].setFocus()
        cursor = self.tab_textedit_data[self.tabWidget.currentIndex()].textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.permanent_label2.setText(self.file_encoding[self.tabWidget.currentIndex()])
        
        # Update the status bar with cursor position
        self.statusBar().showMessage(f"Ln {line} , Col {column}")
    
    def update_cursor(self):
        if self.tab_count>0:
            self.update_cursor_position
    
    def zoom_out(self):
        if self.zoom_level>=85:
            font = self.tab_textedit_data[self.tabWidget.currentIndex()].font()
            font.setPointSize(font.pointSize() - 2)
            self.zoom_level -= 5
            self.permanent_label.setText(f'  {self.zoom_level} %  ')
            for i in range(self.tab_count+1):
                self.tab_textedit_data[i].setFont(font)

    def zoom_in(self):
        font = self.tab_textedit_data[self.tabWidget.currentIndex()].font()
        font.setPointSize(font.pointSize() + 2)
        self.zoom_level += 5
        self.permanent_label.setText(f'  {self.zoom_level} %  ')
        for i in range(self.tab_count+1):
            self.tab_textedit_data[i].setFont(font)
    
    def dark_theme(self):
        self.dark_theme_enabled = not self.dark_theme_enabled
        if self.dark_theme_enabled:
            self.setStyleSheet(self.settings_data['theme']['dark-theme']['window'])
            self.tabWidget.setStyleSheet(self.settings_data['theme']['dark-theme']['tabwidget-stylesheet'])
            self.statusbar.setStyleSheet(self.settings_data['theme']['dark-theme']['statusbar-stylesheet'])
            self.menubar.setStyleSheet(self.settings_data['theme']['dark-theme']['menubar-stylesheet'])
        else:
            self.setStyleSheet(self.settings_data['theme']['light-theme']['window'])
            self.tabWidget.setStyleSheet(self.settings_data['theme']['light-theme']['tabwidget-stylesheet'])
            self.statusbar.setStyleSheet(self.settings_data['theme']['light-theme']['statusbar-stylesheet'])
            self.menubar.setStyleSheet(self.settings_data['theme']['light-theme']['menubar-stylesheet'])
    
    def time_date(self):
        __current_time = datetime.now().strftime('%H:%M:%S')
        __current_date = datetime.now().strftime('%Y-%m-%d')
        __current_day = datetime.now().strftime('%A')
        __text_to_insert = __current_time + " " + __current_date + " " + __current_day
        cursor = self.tab_textedit_data[self.tabWidget.currentIndex()].textCursor()
        cursor.insertText(__text_to_insert)
    
    def open_font_picker(self):
        font, ok = QFontDialog.getFont(self.tab_textedit_data[self.tabWidget.currentIndex()].font(), self)
        if ok:
            cursor =  self.tab_textedit_data[self.tabWidget.currentIndex()].textCursor()
            if cursor.hasSelection():
                cursor.mergeCharFormat(QTextCharFormat().setFont(font))
                self.tab_textedit_data[self.tabWidget.currentIndex()].setTextCursor(cursor)
            else:
                for i in range(self.tab_count+1):
                    self.tab_textedit_data[i].setFont(font)

            self.settings_data['default-font'] = font.family()
            self.settings_data['default-font-size'] = font.pointSize()
            with open('settings.json','w') as file:
                json.dump(self.settings_data, file, indent=4)
    
    def restore_font(self):
        self.zoom_level = 100
        self.permanent_label.setText(f'  {self.zoom_level} %  ')
        font = QFont(self.settings_data['default-font'], self.settings_data['default-font-size'])
        for i in range(self.tab_count+1):
            self.tab_textedit_data[i].setFont(font)
    
    def create_new_window(self):
        new_instance = MyGUI()
        new_instance.show()
    
    def closeEvent(self, event):
        while self.tab_count!=0:
            self.close_tab(self.tabWidget.currentIndex())
        if self.tab_count==0:
            self.close_tab(self.tabWidget.currentIndex())

def main():
    app = QApplication([])
    window = MyGUI(*sys.argv)
    app.exec_()

if __name__ == '__main__':
    main()