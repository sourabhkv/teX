from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont, QTextCharFormat, QIcon
import sys
import os
from elements import find, replace, page, go_to, about
import json

class MyGUI(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MyGUI, self).__init__()
        uic.loadUi('./ui/text_editor.ui', self)
        self.icon = QIcon('./ui/images/notepad.ico')
        self.setWindowIcon(self.icon)
        self.setWindowTitle('teX')
        self.tabs = []
        self.zoom_level = 100
        self.word_count =  0
        self.line_type = 'CRLF' if os.name == 'nt' else 'LF'
        self.encoding_type = 'UTF-8'
        
        try:
            with open('settings.json','r') as file:
                self.settings_data = json.load(file)
        except FileNotFoundError:
            sys.exit(0)
        except json.JSONDecodeError as e:
            sys.exit(0)
        
        self.DARK_THEME_ENABLED = self.settings_data['DEFAULT_DARK_THEME']
        if self.settings_data['ALWAYS_SHOW_MAXIMIZED']:
            self.showMaximized()
        
        self.setAcceptDrops(True)
        self.actionNew_tab.triggered.connect(self.add_new_tabs)
        self.actionClose_tab.triggered.connect(lambda: self.close_tab(self.tabWidget.currentIndex()))
        self.actionOpen.triggered.connect(self.open_file)
        self.actionNew_Window.triggered.connect(self.create_new_window)
        self.actionAbout.triggered.connect(self.about)
        self.actionFont_size.triggered.connect(self.open_font_picker)
        self.actionZoom_in.triggered.connect(self.zoom_in)
        self.actionZoom_out_2.triggered.connect(self.zoom_out)
        self.actionRestore_default_zoom.triggered.connect(self.restore_font)
        self.actionSave.triggered.connect(self.save_file)
        self.actionSave_As.triggered.connect(self.save_file)
        self.actionDark_Theme.triggered.connect(self.dark_theme)
        self.actionFind.triggered.connect(self.findUI)
        self.actionReplace.triggered.connect(self.replace_text)
        self.actionselect_all.triggered.connect(self.select_all)
        self.actionpaste.triggered.connect(self.paste)
        self.actioncopy.triggered.connect(self.copy)
        self.actioncut.triggered.connect(self.cut)
        self.actiongo_to.triggered.connect(self.go_to_line)
        QApplication.clipboard().dataChanged.connect(self.check_clipboard)

        self.tabWidget.tabCloseRequested.connect(self.close_tab)
        self.tabWidget.currentChanged.connect(self.update_word_count)
        self.tabWidget.currentChanged.connect(self.update_eof_encoding)
        self.tabWidget.currentChanged.connect(self.update_cursor)
        self.tabWidget.setTabBarAutoHide(self.settings_data['AUTO_HIDE_TABS'])
        

        # statusbar
        self.statusBar().showMessage(f"Ln 1 , Col 1")
        self.zoom_label = QLabel(f"   {self.zoom_level} %  ")
        self.statusbar.addPermanentWidget(self.zoom_label)
        
        self.status_separator()


        self.word_count_label = QLabel(f"   {self.word_count} words   ")
        self.statusbar.addPermanentWidget(self.word_count_label)

        self.status_separator()
        
        self.line_type_label = QLabel(f"   {self.line_type}  ")
        self.statusbar.addPermanentWidget(self.line_type_label)

        self.status_separator()

        self.encoding_label = QLabel(f"   {self.encoding_type}   ")
        self.statusbar.addPermanentWidget(self.encoding_label)

        if self.DARK_THEME_ENABLED:
            self.dark_theme()
        else:
            self.setStyleSheet(self.settings_data['theme']['light-theme']['window'])
            self.DARK_THEME_ENABLED = not self.DARK_THEME_ENABLED
            self.menubar.setStyleSheet("")

        if len(args) > 1:
            for i in args[1:]:
                try:
                    self.add_new_tabs(file = i)
                except UnicodeDecodeError:
                    self.add_new_tabs()

        try:
            with open('./temp.json','r') as file:
                __restoring_data = json.load(file)
            for i in __restoring_data:
                self.add_new_tabs(**__restoring_data[i])
        except FileNotFoundError:
            self.add_new_tabs()
    
    def add_new_tabs(self, **kwargs):
        '''
        Adds new tab in tabWidget
        '''
        __tab = page.TabElement(**kwargs)
        self.tabs.append(__tab)
        __current_tab = self.tabs[-1]
        __layout = QVBoxLayout()
        __layout.addWidget(__current_tab.text_edit)
        __current_tab.current_widget.setLayout(__layout)  # set layout on QWidget
        
        self.tabWidget.addTab(__current_tab.current_widget, __current_tab.title)
        __current_tab.text_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)
        __current_tab.text_edit.setFocus()
        self.tabWidget.setTabToolTip(self.tabWidget.count() - 1, __current_tab.file)
        self.tabWidget.setTabWhatsThis(self.tabWidget.currentIndex(), __current_tab.title)
        self.word_count = __current_tab.word_count
        self.word_count_label.setText(f"   {self.word_count} words   ")
        __current_tab.text_edit.textChanged.connect(lambda: __current_tab.handle_text_changed(self))
        self.actiontime_date.triggered.connect(__current_tab.time_date)
        __current_tab.text_edit.cursorPositionChanged.connect(self.update_cursor)
        font = QFont(self.settings_data["DEFAULT_FONT"], self.settings_data["DEFAULT_FONT_SIZE"])
        __current_tab.text_edit.setFont(font)
        self.line_type_label.setText(f"   {__current_tab.line_feed}  ")
        self.statusbar.addPermanentWidget(self.line_type_label)
        self.encoding_label.setText(f"   {__current_tab.file_encoding}   ")
        __current_tab.text_edit.dragEnterEvent = self.drag_enter_event
        __current_tab.text_edit.dropEvent = self.drop_event
        self.set_scrollbar_value(__current_tab.text_edit)
        
    
    def close_tab(self, tab_index, event=None):
        __current_tab = self.tabs[tab_index]
        __current_tab_text = __current_tab.text_edit.toPlainText()
        __current_tab_name = self.tabWidget.tabText(tab_index)

        if len(__current_tab_text) == 0 and __current_tab_name == 'Untitled' and not __current_tab_name.endswith('•'):
            self.tabWidget.removeTab(tab_index)
            self.tabs.pop(tab_index)
        elif len(__current_tab_text) != 0 and __current_tab_name == 'Untitled' or __current_tab_name.endswith('•'):
            self.save_file_close(tab_index, event=None)
        elif __current_tab_name != 'Untitled' and not __current_tab_name.endswith('•') and __current_tab.save_stat:
            self.tabWidget.removeTab(tab_index)
            self.tabs.pop(tab_index)
        else:
            self.save_file()
        
        if self.tabWidget.count()==0:
            sys.exit(0)
    
    def save_dialog(self):
        dialog = QMessageBox()
        dialog.setWindowIcon(self.icon)
        dialog.setWindowTitle('Save')
        dialog.setText("Do you want to save your work?")
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        dialog.setDefaultButton(QMessageBox.Yes)
        answer = dialog.exec()
        return answer
    
    def open_file(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", self.settings_data['FILE_TYPES'], options= QFileDialog.Options())
        if filename != '':
            if len(__current_tab.text_edit.toPlainText())>0:
                self.add_new_tabs(file = filename)
            else:
                self.close_tab(self.tabWidget.currentIndex())
                self.add_new_tabs(file=filename)
    
    def save_file_close(self,tab_index,event):
        answer = self.save_dialog()
        if answer == QMessageBox.Yes:
            self.tabWidget.removeTab(tab_index)
            self.tabs.pop(tab_index)
        elif answer == QMessageBox.No:
            self.tabWidget.removeTab(tab_index)
            self.tabs.pop(tab_index)
        elif answer == QMessageBox.Cancel:
            if event is not None:
                event.ignore()
    
    def save_file(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        if __current_tab.file:
            with open(__current_tab.file , "w", encoding = __current_tab.file_encoding ) as file:
                file.write(__current_tab.text_edit.toPlainText())
            
            __current_tab.save_stat = True

        else:
            filename, _ = QFileDialog.getSaveFileName(self, "Save as", "", self.settings_data['FILE_TYPES'], options= QFileDialog.Options())
            if filename != "":
                with open(filename, "w", encoding = 'UTF-8' ) as file:               #encoding flaw
                    file.write(__current_tab.text_edit.toPlainText())
                
                __current_tab.file = filename
                __current_tab.save_stat = True

        __current_tab.title = os.path.basename(__current_tab.file)
        self.tabWidget.setTabText(self.tabWidget.currentIndex(), __current_tab.title if not __current_tab.title.endswith('•') else __current_tab.title.endswith('•'))
        
    
    def save_current(self, event = None):
        __save_count, i = 0, 0
        __tab_save = {}
        while self.tabWidget.count()>=1:
            __tab_save[__save_count] = {
                "FILE" : self.tabs[i].file,
                "SAVE_STAT" : self.tabs[i].save_stat,
                "ENCODING" : self.tabs[i].file_encoding,
                "EOL" : self.tabs[i].line_feed,
                "WORD_COUNT" : self.tabs[i].word_count,
                "TITLE" : self.tabs[i].title,
            }
            if not self.tabs[i].save_stat:
                __tab_save[__save_count]["TEXT"] = self.tabs[i].text_edit.toPlainText()
            __save_count += 1
            if event:
                self.tabWidget.removeTab(i)
                self.tabs.pop(i)


        with open('./temp.json','w') as __file:
            json.dump(__tab_save, __file, indent=4)
    
    def open_font_picker(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        font, ok = QFontDialog.getFont(__current_tab.text_edit.font(), self)
        if ok:
            cursor =  __current_tab.text_edit.textCursor()
            if cursor.hasSelection():
                cursor.mergeCharFormat(QTextCharFormat().setFont(font))
                __current_tab.text_edit.setTextCursor(cursor)

            for i in range(self.tabWidget.count()):
                self.tabs[i].text_edit.setFont(font)

            self.settings_data['DEFAULT_FONT'] = font.family()
            self.settings_data['DEFAULT_FONT_SIZE'] = font.pointSize()
            with open('./settings.json','w') as file:
                json.dump(self.settings_data, file, indent=4)
    
    def drag_enter_event(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def drop_event(self, event):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()         
            with open(file_path,"r") as file:
                if len(__current_tab.text_edit.toPlainText())>0:
                    try:
                        self.add_new_tabs(file = file_path)
                    except UnicodeDecodeError:
                        self.unknown_encoding()
                        self.add_new_tabs()
                else:
                    self.close_tab(self.tabWidget.currentIndex())
                    try:
                        self.add_new_tabs(file = file_path)
                    except UnicodeDecodeError:
                        self.unknown_encoding()
                        self.add_new_tabs()

    def select_all(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        text_edit = __current_tab.text_edit
        text_edit.selectAll()

    def set_scrollbar_value(self, plain_text_edit):
        plain_text_edit.verticalScrollBar().setSingleStep(2)
        plain_text_edit.verticalScrollBar().setPageStep(10)
        if not self.DARK_THEME_ENABLED:
            plain_text_edit.setStyleSheet(self.settings_data['THEME']['DARK_THEME']['TEXT_EDIT_STYLESHEET'])
        else: #light theme
            plain_text_edit.setStyleSheet(self.settings_data['THEME']['LIGHT_THEME']['TEXT_EDIT_STYLESHEET'])
    
    def findUI(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        search_dialog = find.SearchDialog(self, __current_tab )
        search_dialog.exec_()
    
    def replace_text(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        replace_dialog = replace.ReplaceDialog(self, __current_tab )
        replace_dialog.exec_()

    def check_clipboard(self):
        if QApplication.clipboard().text():  # If clipboard has text
            self.actionpaste.setEnabled(True)  # Enable the button
        else:
            self.actionpaste.setEnabled(False)  # Disable the button

    def paste(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        __cursor = __current_tab.text_edit.textCursor()
        __current_tab.text_edit.selectAll()  # Select all text
        __cursor.insertText(QApplication.clipboard().text())  # Insert clipboard text

    def copy(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        if __current_tab.text_edit.textCursor().hasSelection():  # If text is selected
            __current_tab.text_edit.copy()  # Copy selected text

    def cut(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        if __current_tab.text_edit.textCursor().hasSelection():  # If text is selected
            __current_tab.text_edit.cut()  # Cut selected text
    
    def go_to_line(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        replace_dialog = go_to.GoToDialog(self, __current_tab )
        replace_dialog.exec_()

    def zoom_in(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        font = __current_tab.text_edit.font()
        font.setPointSize(font.pointSize() + 2)
        self.zoom_level += 5
        self.zoom_label.setText(f'  {self.zoom_level} %  ')
        for i in range(self.tabWidget.count()):
            self.tabs[i].text_edit.setFont(font)
    
    def zoom_out(self):
        if self.zoom_level>=85:
            __current_tab = self.tabs[self.tabWidget.currentIndex()]
            font = __current_tab.text_edit.font()
            font.setPointSize(font.pointSize() - 2)
            self.zoom_level -= 5
            self.zoom_label.setText(f'  {self.zoom_level} %  ')
            for i in range(self.tabWidget.count()):
                self.tabs[i].text_edit.setFont(font)
    
    def restore_font(self):
        self.zoom_level = 100
        self.zoom_label.setText(f'  {self.zoom_level} %  ')
        font = QFont(self.settings_data['DEFAULT_FONT'], self.settings_data['DEFAULT_FONT_SIZE'])
        for i in range(self.tabWidget.count()):
            self.tabs[i].text_edit.setFont(font)
    
    def update_word_count(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        self.word_count_label.setText(f"   {__current_tab.word_count} words   ")
        #self.statusbar.addPermanentWidget(self.line_type_label)
    
    def update_eof_encoding(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        self.line_type_label.setText(f"   {__current_tab.line_feed}  ")
        self.encoding_label.setText(f"   {__current_tab.file_encoding}   ")
    
    def update_cursor(self):
        __current_tab = self.tabs[self.tabWidget.currentIndex()]
        cursor = __current_tab.text_edit.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        if cursor.hasSelection():
            length = len(cursor.selectedText())
            self.statusBar().showMessage(f"Ln {line} , Col {column} ({length} selected) ")
        else:
            self.statusBar().showMessage(f"Ln {line} , Col {column}")
    
    def dark_theme(self):
        if self.DARK_THEME_ENABLED:
            self.setStyleSheet(self.settings_data['THEME']['DARK_THEME']['WINDOW'])
            self.tabWidget.setStyleSheet(self.settings_data['THEME']['DARK_THEME']['TABWIDGET_STYLESHEET'])
            self.statusbar.setStyleSheet(self.settings_data['THEME']['DARK_THEME']['STATUSBAR_STYLESHEET'])
            self.menubar.setStyleSheet(self.settings_data['THEME']['DARK_THEME']['MENUBAR_STYLESHEET'])
        else:
            self.setStyleSheet(self.settings_data['THEME']['LIGHT_THEME']['WINDOW'])
            self.tabWidget.setStyleSheet(self.settings_data['THEME']['LIGHT_THEME']['TABWIDGET_STYLESHEET'])
            self.statusbar.setStyleSheet(self.settings_data['THEME']['LIGHT_THEME']['STATUSBAR_STYLESHEET'])
            self.menubar.setStyleSheet(self.settings_data['THEME']['LIGHT_THEME']['MENUBAR_STYLESHEET'])

        self.DARK_THEME_ENABLED = not self.DARK_THEME_ENABLED
    
    def status_separator(self):
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.VLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        
    def closeEvent(self, event):
        self.save_current(event)
    
    def create_new_window(self):
        new_instance = MyGUI()
        new_instance.show()
    
    def about(self):
        __temp = about.About()
            
        
def main():
    app = QApplication([])
    window = MyGUI(*sys.argv)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()