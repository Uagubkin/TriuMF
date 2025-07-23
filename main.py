import sys
from os import name as os_name
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QListView
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt, QDir
from collections import OrderedDict

class KeyboardFileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keyboard-Driven File Manager")
        self.setGeometry(100, 100, 1200, 600)
        
        # 1. Модель файловой системы
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)
        
        # 2. Три панели
        self.panels = OrderedDict([
            ('left', QListView()),
            ('center', QListView()),
            ('right', QListView())
        ])
        
        for panel in self.panels.values():
            panel.setModel(self.model)
        
        # 3. Размещение панелей
        splitter = QSplitter()
        for panel in self.panels.values():
            splitter.addWidget(panel)
        self.setCentralWidget(splitter)
        
        # 4. Начальный путь (например, домашняя папка)
        self.current_path = QDir.homePath()
        self.update_panels()

    def keyPressEvent(self, event):
        match event.key():
            case Qt.Key.Key_Left:
                self.move_to_parent()
            case Qt.Key.Key_Right:
                self.enter_selected()
            case Qt.Key.Key_Up:
                self.move_cursor(-1)
            case Qt.Key.Key_Down:
                self.move_cursor(1)
            case _:  # Любая другая клавиша
                super().keyPressEvent(event)

    def move_to_parent(self):
        if self.current_path:
            """Переход к родительской папке"""
            current_dir = QDir(self.current_path)
            
            # Получаем родительский путь
            if current_dir.cdUp():  # Переходим на уровень выше
                self.current_path = current_dir.absolutePath()
            else:
                # Мы в корне файловой системы
                self.current_path = str()
            
            self.update_panels()

    def enter_selected(self):
        index = self.panels['center'].currentIndex()
        if index.isValid() and self.model.isDir(index):
            self.current_path = self.model.filePath(index)
            self.update_panels()

    def move_cursor(self, step):
        # Перемещение курсора в текущей панели
        current_index = self.panels["center"].currentIndex()
        new_index = self.model.index(current_index.row() + step, 0, current_index.parent())
        if new_index.isValid():
            self.panels["center"].setCurrentIndex(new_index)

    def update_panels(self):
        if self.current_path:
            self.panels["left"].setVisible(True)
            # Получаем родительский путь
            dir_obj = QDir(self.current_path)
            if dir_obj.cdUp():  # Переходим на уровень выше
                parent_path = dir_obj.absolutePath()
                
                # Левая панель (родительский каталог)
                self.panels['left'].setRootIndex(self.model.index(parent_path))
                
                # Автовыбор текущей папки в левой панели
                child_name = QDir(self.current_path).dirName()
                parent_index = self.model.index(parent_path)
                for i in range(self.model.rowCount(parent_index)):
                    idx = self.model.index(i, 0, parent_index)
                    if self.model.fileName(idx) == child_name:
                        self.panels['left'].setCurrentIndex(idx)
                        break
            else:
                # Если мы в корне (cdUp вернул False)
                self.panels['left'].setRootIndex(self.model.index(""))
        else:
            self.panels["left"].setVisible(False)
            
        # Центральная панель
        self.panels['center'].setRootIndex(self.model.index(self.current_path))
        
        # Правая панель (сбрасываем)
        self.panels['right'].setRootIndex(self.model.index(""))
    

if __name__ == "__main__":
    app = QApplication([])

    widget = KeyboardFileManager()
    widget.show()

    sys.exit(app.exec())