from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog
import sys
import os

class FileFolderDialog(QWidget):
    # Define signals for selected file and folder
    file_selected = pyqtSignal(str)
    folder_selected = pyqtSignal(str)

    def __init__(self):
        super(FileFolderDialog, self).__init__()

        self.init_ui()

        # Initialize selected path and type variables
        self.selected_path = ''
        self.selected_type = ''

    def init_ui(self):
        self.setGeometry(100, 100, 300, 100)
        self.setWindowTitle('File/Folder Dialog')

        layout = QVBoxLayout()

        btn_file = QPushButton('Select File', self)
        btn_file.clicked.connect(self.select_file)

        btn_folder = QPushButton('Select Folder', self)
        btn_folder.clicked.connect(self.select_folder)

        layout.addWidget(btn_file)
        layout.addWidget(btn_folder)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName()
        print("Selected file:", file_path)
        self.selected_path = file_path
        self.selected_type = 'file'
        self.file_selected.emit(file_path)
        self.close()  # Close the window after selecting a file

    def select_folder(self):
        dir_path = QFileDialog.getExistingDirectory()
        print("Selected folder:", dir_path)
        self.selected_path = dir_path
        self.selected_type = 'folder'
        self.folder_selected.emit(dir_path)
        self.close()  # Close the window after selecting a folder

    def get_selected_path(self):
        return self.selected_path

    def get_selected_type(self):
        return self.selected_type


def select_file_or_folder():
    app = QApplication(sys.argv)
    window = FileFolderDialog()
    window.show()

    # Connect signals to slots in the main code
    window.file_selected.connect(lambda path: print("File selected:", path))
    window.folder_selected.connect(lambda path: print("Folder selected:", path))

    # Start event loop
    app.exec_()

    # Access selected path and type from FileFolderDialog instance
    selected_path = window.get_selected_path()
    selected_type = window.get_selected_type()

    return selected_path


if __name__ == '__main__':
    selected_path = select_file_or_folder()

    print("Selected file path:", selected_path)