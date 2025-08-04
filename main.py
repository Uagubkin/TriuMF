import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QListView, QAbstractItemView
from PyQt6.QtGui import QFileSystemModel, QStandardItemModel
from PyQt6.QtCore import Qt, QDir, QEvent
from collections import OrderedDict

class KeyboardFileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TriuMF")
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
            panel.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # 3. Размещение панелей
        splitter = QSplitter()
        for panel in self.panels.values():
            splitter.addWidget(panel)
        self.setCentralWidget(splitter)
        
        # 4. Начальный путь (например, домашняя папка)
        self.current_path = QDir.homePath()
        self.model.directoryLoaded.connect(self.update_panels)

        self.panels['left'].setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.panels['center'].setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.panels['right'].setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.panels['center'].installEventFilter(self)        

        self.update_panels()

    def keyPressEvent(self, event):
        match event.key():
            case Qt.Key.Key_Left:
                self.move_to_parent()
            case Qt.Key.Key_Right:
                self.enter_selected()
            case _:  # Любая другая клавиша
                super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        if (obj == self.panels['center'] and event.type() == QEvent.Type.KeyPress):
            if event.key() == Qt.Key.Key_Up:
                self.move_cursor(-1)
                return True
            elif event.key() == Qt. Key.Key_Down:
                self.move_cursor(1)
        return super().eventFilter(obj, event)

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
        current_index = self.panels['center'].currentIndex()
        new_index = self.model.index(current_index.row() + step, 0, current_index.parent())
        if new_index.isValid():
            self.panels['center'].setCurrentIndex(new_index)
            self.update_right_panel()

    def update_panels(self):
        if self.current_path:
            self.panels["left"].setModel(self.model)
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
                # Если мы в корне диска (cdUp вернул False)
                self.panels['left'].setRootIndex(self.model.index(""))
        else:
            # Очистка левой панели если в центральной панели уже выбор диска
            self.panels['left'].setModel(QStandardItemModel())
        
        # Центральная панель
        self.panels['center'].setRootIndex(self.model.index(self.current_path))
        self.panels['center'].setFocus()
        #self.select_first_item()
        
        # Правая панель (сбрасываем)
        self.update_right_panel()

    def update_right_panel(self):
        temp_index = self.panels['center'].currentIndex()
        if temp_index.isValid() and self.model.isDir(temp_index):
            self.panels['right'].setRootIndex(temp_index)
            print(self.model.filePath(temp_index))

    def select_first_item(self):
        current_index = self.model.index(self.current_path)
        print(self.model.rowCount(current_index))
        if self.model.rowCount(current_index) > 0:
            idx = self.model.index(0, 0, current_index)
            self.panels['center'].setCurrentIndex(idx)
    

if __name__ == "__main__":
    app = QApplication([])

    widget = KeyboardFileManager()
    widget.show()

    sys.exit(app.exec())