import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QListWidget, 
    QFileDialog, QMessageBox, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path

from builder import generate_font_and_dart

class BuildThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, svg_paths, font_name, class_name, output_dir):
        super().__init__()
        self.svg_paths = svg_paths
        self.font_name = font_name
        self.class_name = class_name
        self.output_dir = output_dir

    def run(self):
        try:
            generate_font_and_dart(
                self.svg_paths,
                self.font_name,
                self.class_name,
                self.output_dir,
                lambda msg: self.progress.emit(msg)
            )
            self.finished.emit(True, "Process completed successfully!")
        except Exception as e:
            self.finished.emit(False, str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flutter SVG Font Builder")
        self.resize(800, 600)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #fff;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #fff;
                font-size: 14px;
            }
        """)
        
        self.svg_paths = set()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        central.setLayout(layout)
        
        # Header
        title = QLabel("SVG to Flutter Font Builder")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Info label
        info = QLabel("Drag and drop your SVG files into the area below.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #666;")
        layout.addWidget(info)
        
        # Drop Area / List
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.setAlternatingRowColors(True)
        
        list_controls = QHBoxLayout()
        self.add_btn = QPushButton("Add SVGs")
        self.add_folder_btn = QPushButton("Add Folder")
        self.remove_btn = QPushButton("Remove Selected")
        self.clear_btn = QPushButton("Clear All")
        
        self.add_btn.clicked.connect(self.add_svgs)
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.remove_btn.clicked.connect(self.remove_svgs)
        self.clear_btn.clicked.connect(self.clear_svgs)
        
        list_controls.addWidget(self.add_btn)
        list_controls.addWidget(self.add_folder_btn)
        list_controls.addWidget(self.remove_btn)
        list_controls.addWidget(self.clear_btn)
        
        layout.addWidget(self.list_widget, 1) # Give it stretch factor 1
        layout.addLayout(list_controls)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Settings
        settings_layout = QVBoxLayout()
        settings_title = QLabel("Tool Settings")
        settings_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        settings_layout.addWidget(settings_title)
        
        # Font Name
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Font Family Name:"))
        self.font_name_input = QLineEdit("MyIcons")
        row1.addWidget(self.font_name_input)
        settings_layout.addLayout(row1)
        
        # Class Name
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Flutter Class Name:"))
        self.class_name_input = QLineEdit("MyIcons")
        row2.addWidget(self.class_name_input)
        settings_layout.addLayout(row2)
        
        # Output Dir
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Output Directory:"))
        self.output_dir_input = QLineEdit(str(Path.home() / "Desktop" / "FlutterIcons"))
        self.output_dir_btn = QPushButton("Browse")
        self.output_dir_btn.clicked.connect(self.browse_output_dir)
        row3.addWidget(self.output_dir_input)
        row3.addWidget(self.output_dir_btn)
        settings_layout.addLayout(row3)
        
        layout.addLayout(settings_layout)
        
        # Log
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(100)
        self.log_output.setStyleSheet("background-color: #222; color: #0f0; font-family: monospace; font-size: 12px;")
        layout.addWidget(self.log_output)
        
        # Generate
        self.generate_btn = QPushButton("Generate Flutter Font")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px; 
                font-weight: bold; 
                padding: 15px; 
                background-color: #2196F3; 
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #B0BEC5;
            }
        """)
        self.generate_btn.clicked.connect(self.generate)
        layout.addWidget(self.generate_btn)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            p = Path(f)
            if p.suffix.lower() == '.svg':
                self.svg_paths.add(str(p))
                
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for p in sorted(self.svg_paths):
            self.list_widget.addItem(p)

    def add_svgs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select SVG files", "", "SVG Files (*.svg)")
        if files:
            for f in files:
                self.svg_paths.add(f)
            self.refresh_list()

    def add_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select SVG Folder")
        if directory:
            path = Path(directory)
            for f in path.rglob("*.svg"):
                self.svg_paths.add(str(f))
            for f in path.rglob("*.SVG"):
                self.svg_paths.add(str(f))
            self.refresh_list()

    def remove_svgs(self):
        selected = self.list_widget.selectedItems()
        if not selected:
            return
        for item in selected:
            self.svg_paths.discard(item.text())
        self.refresh_list()

    def clear_svgs(self):
        self.svg_paths.clear()
        self.refresh_list()
        
    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_dir_input.text())
        if directory:
            self.output_dir_input.setText(directory)

    def log(self, msg):
        self.log_output.append(msg)
        # Auto-scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def generate(self):
        if not self.svg_paths:
            QMessageBox.warning(self, "Missing SVGs", "Please add at least one SVG file.")
            return
        if not self.font_name_input.text().strip():
            QMessageBox.warning(self, "Missing Setting", "Font Family Name is required.")
            return
        if not self.class_name_input.text().strip():
            QMessageBox.warning(self, "Missing Setting", "Flutter Class Name is required.")
            return
        if not self.output_dir_input.text().strip():
            QMessageBox.warning(self, "Missing Setting", "Output Directory is required.")
            return
            
        self.generate_btn.setEnabled(False)
        self.log_output.clear()
        self.log("Starting generation...")
        
        self.thread = BuildThread(
            list(self.svg_paths),
            self.font_name_input.text().strip(),
            self.class_name_input.text().strip(),
            self.output_dir_input.text().strip()
        )
        self.thread.progress.connect(self.log)
        self.thread.finished.connect(self.on_generate_finished)
        self.thread.start()
        
    def on_generate_finished(self, success, msg):
        self.generate_btn.setEnabled(True)
        if success:
            self.log(">> " + msg)
            QMessageBox.information(self, "Success", msg)
        else:
            self.log(">> Error: " + msg)
            QMessageBox.critical(self, "Error", msg)
