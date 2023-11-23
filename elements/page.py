from PyQt5.QtWidgets import *
from datetime import datetime
import os
import chardet

class TabElement:
    def __init__(self, file = None, **kwargs):
        super(TabElement, self).__init__()
        self.current_widget = QWidget()
        self.text_edit = QPlainTextEdit(self.current_widget)
        self.file = kwargs.get('FILE', file)
        self.save_stat = kwargs.get('SAVE_STATUS', False if self.file is None else True )
        self.file_encoding = kwargs.get('ENCODING', self.return_file_encoding())
        self.text = kwargs['TEXT'] if 'TEXT' in kwargs else self.return_text()
        self.text_edit.setPlainText(self.text)
        self.line_feed = kwargs.get('EOL', self.check_EOL())
        self.word_count = self.return_word_count() if self.save_stat and 'TEXT' not in kwargs else kwargs.get('WORD_COUNT',self.return_word_count())
        self.title = kwargs.get('TITLE', 'Untitled' if self.file is None else os.path.basename(self.file) )

    def return_file_encoding(self):
        if self.file is not None:
            with open(self.file , mode= 'rb') as __file:
                __result =  chardet.detect(__file.read())
            print(type(__result['encoding']))
            
            return __result['encoding'] if __result['encoding'] else 'UTF-8'
        
        return 'UTF-8'
    
    def check_EOL(self):
        try:
            with open(self.file, 'rb') as __file:
                __temp = __file.read()
            
            if b'\n' in __temp and b'\r\n' not in __temp:
                return 'LF'
            elif b'\r\n' in __temp:
                return 'CRLF'
            
        except TypeError:
            return 'CRLF'if os.name == 'nt' else 'LF'
    
    def return_word_count(self):
        try:
            return len(self.text.split())
        except:
            return len(self.text_edit.toPlainText().split())
    
    def return_text(self):
        if self.file:
            with open(self.file, 'r', encoding= self.file_encoding) as __file:
                __temp = __file.read()
            self.text_edit.setPlainText(__temp)
            return __temp
        else:
            return ''
    
    def handle_text_changed(self,parent):
        if self.title != 'Untitled' and self.save_stat and not parent.tabWidget.tabText(parent.tabWidget.currentIndex()).endswith('•'):
            self.title += '•'
            parent.tabWidget.setTabText(parent.tabWidget.currentIndex() , self.title)
            self.save_stat = False

        self.word_count = len(self.text_edit.toPlainText().split())
        parent.word_count_label.setText(f"   {self.word_count} words   ")
    
    def time_date(self):
        __current_time = datetime.now().strftime('%H:%M:%S')
        __current_date = datetime.now().strftime('%Y-%m-%d')
        __current_day = datetime.now().strftime('%A')
        __text_to_insert = __current_time + " " + __current_date + " " + __current_day
        cursor = self.text_edit.textCursor()
        cursor.insertText(__text_to_insert)