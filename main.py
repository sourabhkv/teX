from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont, QTextCharFormat, QIcon, QPixmap
import sys
import os
from datetime import datetime
from PyQt5.QtCore import QTimer

class MyGUI(QMainWindow):
    def __init__(self,*args):
        self.__version__ = 1.01
        super(MyGUI, self).__init__()
        self.tab_count = -1
        self.tab_data = []
        self.tab_textedit_data = []
        #self.save_status = []                        track saving status of files
        uic.loadUi('text_editor.ui', self)
        icon = QIcon('notepad.ico')
        self.setWindowIcon(icon)
        self.setWindowTitle('Text editor x')
        self.dark_theme_enabled = False

        if len(args) > 1:
            for i in args[1:]:
                  # Convert i to string
                with open(i,"r") as file:
                    self.add_new_tab(tabname=str(i),text = file.read())
                    #self.tab_textedit_data[self.tabWidget.currentIndex()].setPlainText(file.read())
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

        self.tabWidget.currentChanged.connect(self.update_cursor)

        self.actionDark_Theme.triggered.connect(self.dark_theme)

        self.actionAbout.triggered.connect(self.about)

        self.statusBar().showMessage(f"Line: 1, Column: 1")

        self.setStyleSheet('''background-color: #FFFFFF;color: #000; border: none;''')

        self.menubar.setStyleSheet("")
        
        self.show()

    def add_new_tab(self, tabname, text = ''):
        self.tab_data.append(QWidget())
        self.tabWidget.addTab(self.tab_data[-1], tabname)
        self.tab_count += 1
        self.tabWidget.setCurrentIndex(self.tab_count)
        self.tab_textedit_data.append(QPlainTextEdit(self.tab_data[-1]))
        #self.save_status.append(False)

        plain_text_edit = self.tab_textedit_data[-1]
        layout = QVBoxLayout()
        layout.addWidget(plain_text_edit)
        plain_text_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        plain_text_edit.setPlainText(text)
        self.tab_data[-1].setLayout(layout)
        plain_text_edit.setFocus()
        plain_text_edit.installEventFilter(self)
        plain_text_edit.textChanged.connect(self.handle_text_changed)
        
        # Use QTimer to set the scrollbar value after the widget is displayed
        QTimer.singleShot(0, lambda: self.set_scrollbar_value(plain_text_edit))
    
    def handle_text_changed(self):# mark * with unsaved files
        if self.tabWidget.tabText(self.tabWidget.currentIndex())!='Untitled' and not self.tabWidget.tabText(self.tabWidget.currentIndex()).endswith('*'):
            self.tabWidget.setTabText(self.tabWidget.currentIndex(), self.tabWidget.tabText(self.tabWidget.currentIndex())+"*")
            

    def set_scrollbar_value(self, plain_text_edit):
        plain_text_edit.verticalScrollBar().setSingleStep(2)
        plain_text_edit.verticalScrollBar().setPageStep(10)
        plain_text_edit.cursorPositionChanged.connect(self.update_cursor_position)
        if not self.dark_theme_enabled:
            plain_text_edit.setStyleSheet('''
                QScrollBar:vertical {
                    width: 5px; /* Set the width of the vertical scrollbar */
                }
                QScrollBar:horizontal {
                    height: 5px; /* Set the height of the horizontal scrollbar */
                }
                QScrollBar::handle {
                    background: #000; /* Set the background color of the scrollbar handle */
                    border: 1px solid #666; /* Set a border around the handle */
                }
            ''')
        else:
            plain_text_edit.setStyleSheet('''
                QScrollBar:vertical {
                    width: 5px; /* Set the width of the vertical scrollbar */
                }
                QScrollBar:horizontal {
                    height: 5px; /* Set the height of the horizontal scrollbar */
                }
                QScrollBar::handle {
                    background: #555; /* Set the background color of the scrollbar handle */
                    border: 1px solid #000; /* Set a border around the handle */
                }
            ''')
    
    def close_tab(self,tab_index):
        if self.tab_count != 0:
            if len(self.tab_textedit_data[tab_index].toPlainText())==0 and self.tabWidget.tabText(tab_index)=='Untitled' and not self.tabWidget.tabText(tab_index).endswith('*'):
                self.tab_data.pop(tab_index)
                self.tab_textedit_data.pop(tab_index)
                self.tabWidget.removeTab(tab_index)
                self.tab_count -= 1
                self.tab_textedit_data[self.tabWidget.currentIndex()].setFocus()
            else:
                if len(self.tab_textedit_data[tab_index].toPlainText())!=0 and self.tabWidget.tabText(tab_index)=='Untitled':
                    dialog = QMessageBox()
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
                self.tab_textedit_data.pop(tab_index)
                self.tabWidget.removeTab(tab_index)
                self.tab_count -= 1
                try:
                    self.tab_textedit_data[tab_index-1].setFocus()
                except:
                    pass
        else:
            if len(self.tab_textedit_data[tab_index].toPlainText())!=0 and self.tabWidget.tabText(tab_index)=='Untitled' or self.tabWidget.tabText(tab_index).endswith('*'):
                    dialog = QMessageBox()
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
    
    def about(self):
        msgBox = QMessageBox()
        pixmap = QPixmap("notepad.png")
        msgBox.setIconPixmap(pixmap)
        msgBox.setText("Text Editor X\nDeveloped by sourabhkv")
        msgBox.setWindowTitle("About")
        msgBox.addButton(QMessageBox.Ok)
        msgBox.exec()


    def open_file(self):
        _text = self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText()
        if _text=="":
            options_ = QFileDialog.Options()
            filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text Files (*.txt);;Python Files (*.py)", options=options_)
            if filename != "":
                with open(filename, "r") as file:
                    self.tab_textedit_data[self.tabWidget.currentIndex()].setPlainText(file.read())
                self.tabWidget.setTabText(self.tabWidget.currentIndex(), filename)
        
        else:
            options_ = QFileDialog.Options()
            filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text Files (*.txt);;Python Files (*.py)", options=options_)
            if filename != "":
                self.add_new_tab(filename)
                with open(filename, "r") as file:
                    self.tab_textedit_data[self.tabWidget.currentIndex()].setPlainText(file.read())
    
    def save_file(self):
        __text = self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText()
        if __text!="":
            __tabname = self.tabWidget.tabText(self.tabWidget.currentIndex())
            if __tabname=="Untitled":
                options = QFileDialog.Options()
                filename, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Text Files (*.txt);;Python Files (*.py);;All files (*)", options=options)
                if filename != "":
                    with open(filename, "w") as file:
                        file.write(self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText())
                    self.tabWidget.setTabText(self.tabWidget.currentIndex(), filename)
            else:
                if os.path.exists(__tabname):
                    with open(__tabname, "w") as file:
                        file.write(self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText())
                else:
                    self.tabWidget.setTabText(self.tabWidget.currentIndex(), "Untitled")
    
    def save_as_file(self):
        __text = self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText()
        if __text!="":
            options = QFileDialog.Options()
            filename, _ = QFileDialog.getSaveFileName(self, "Save As file", "", "Text Files (*.txt);;Python Files (*.py);;All files (*)", options=options)
            if filename != "":
                with open(filename, "w") as file:
                    file.write(self.tab_textedit_data[self.tabWidget.currentIndex()].toPlainText())
                self.tabWidget.setTabText(self.tabWidget.currentIndex(), filename)


    def update_cursor_position(self):
        cursor = self.tab_textedit_data[self.tabWidget.currentIndex()].textCursor()
        line = cursor.blockNumber() + 1  # Get the current line number (1-based)
        column = cursor.columnNumber()  # Get the current column number (0-based)
        
        # Update the status bar with cursor position
        self.statusBar().showMessage(f"Line: {line}, Column: {column}")
    
    def update_cursor(self):
        if self.tab_count>0:
            self.update_cursor_position
    
    def zoom_out(self):
        font = self.tab_textedit_data[self.tabWidget.currentIndex()].font()
        font.setPointSize(font.pointSize() - 1)
        for i in range(self.tab_count+1):
            self.tab_textedit_data[i].setFont(font)

    def zoom_in(self):
        font = self.tab_textedit_data[self.tabWidget.currentIndex()].font()
        font.setPointSize(font.pointSize() + 1)
        for i in range(self.tab_count+1):
            self.tab_textedit_data[i].setFont(font)
    
    def dark_theme(self):
        self.dark_theme_enabled = not self.dark_theme_enabled
        if self.dark_theme_enabled:
            self.setStyleSheet('''background-color: #333; color: #FFF; border: none;''')
            self.tabWidget.setStyleSheet('''
                            QTabWidget::pane {
                    background-color: #333; /* Set the background color */
                }
                
                QTabBar::tab {
                    background-color: #777; /* Set the background color of tabs */
                    color: #FFF; /* Set the text color of tabs */
                    border: 1px solid #555; /* Set a border around tabs */
                    padding: 5px;
                }
                
                QTabBar::tab:selected {
                    background-color: #333; /* Set the background color of the selected tab */
                }
                ''')
            self.statusbar.setStyleSheet("""
                background-color: #222; /* Set the background color of the status bar */
                color: #FFF; /* Set the text color of the status bar */
                """)
            self.menubar.setStyleSheet("""
                QMenuBar {
                    background-color: #222; /* Set the background color of the menu bar */
                    color: #FFF; /* Set the text color of the menu bar */
                }
                QMenuBar::item:selected {
                    background-color: #444; /* Set the background color when hovering */
                }
                """)
        else:
            self.setStyleSheet('''background-color: #FFFFFF;color: #000; border: none;''')
            self.tabWidget.setStyleSheet('')
            self.statusbar.setStyleSheet('')
            self.menubar.setStyleSheet('')
    
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
    
    def restore_font(self):
        font = QFont("Segoe UI", 10)
        for i in range(self.tab_count+1):
            self.tab_textedit_data[i].setFont(font)
    
    def create_new_window(self):
        new_instance = MyGUI()
        new_instance.show()

def main():
    app = QApplication([])
    window = MyGUI(*sys.argv)
    app.exec_()

if __name__ == '__main__':
    main()