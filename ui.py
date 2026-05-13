import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QListWidget, 
    QFileDialog, QMessageBox, QTextEdit, QFrame,
    QTabWidget, QScrollArea, QGridLayout, QSpinBox,
    QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtSvgWidgets import QSvgWidget
from pathlib import Path

from builder import generate_font_and_dart

class BuildThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, svg_paths, font_name, class_name, output_dir, font_height, normalize):
        super().__init__()
        self.svg_paths = svg_paths
        self.font_name = font_name
        self.class_name = class_name
        self.output_dir = output_dir
        self.font_height = font_height
        self.normalize = normalize

    def run(self):
        try:
            generate_font_and_dart(
                self.svg_paths,
                self.font_name,
                self.class_name,
                self.output_dir,
                self.font_height,
                self.normalize,
                lambda msg: self.progress.emit(msg)
            )
            self.finished.emit(True, "Process completed successfully!")
        except Exception as e:
            self.finished.emit(False, str(e))


class IconGalleryItem(QWidget):
    def __init__(self, svg_path):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)
        
        self.svg_widget = QSvgWidget(svg_path)
        self.svg_widget.setFixedSize(64, 64)
        layout.addWidget(self.svg_widget, 0, Qt.AlignmentFlag.AlignCenter)
        
        name = Path(svg_path).name
        label = QLabel(name)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 10px; color: #555;")
        label.setMaximumWidth(80)
        layout.addWidget(label)
        
        self.setFixedSize(100, 110)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flutter SVG Font Builder")
        self.resize(900, 700)
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
            QLineEdit, QSpinBox {
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
            QTabWidget::pane {
                border: 1px solid #ccc;
                background: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #e1e1e1;
                border: 1px solid #ccc;
                padding: 10px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
        """)
        
        self.svg_paths = set()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        
        # Header
        header = QWidget()
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)
        title = QLabel("SVG to Flutter Font Builder")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        info = QLabel("Drag and drop your SVG files into the area below.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #666;")
        header_layout.addWidget(info)
        main_layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- TAB 1: GENERATOR ---
        self.tab_generator = QWidget()
        self.tabs.addTab(self.tab_generator, "Generator")
        gen_layout = QVBoxLayout()
        self.tab_generator.setLayout(gen_layout)
        
        # List Area
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.setAlternatingRowColors(True)
        gen_layout.addWidget(self.list_widget, 1)
        
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
        gen_layout.addLayout(list_controls)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        gen_layout.addWidget(line)
        
        # Settings
        settings_grid = QGridLayout()
        
        # Row 1: Font Name
        settings_grid.addWidget(QLabel("Font Family Name:"), 0, 0)
        self.font_name_input = QLineEdit("MyIcons")
        settings_grid.addWidget(self.font_name_input, 0, 1)
        
        # Row 2: Class Name
        settings_grid.addWidget(QLabel("Flutter Class Name:"), 1, 0)
        self.class_name_input = QLineEdit("MyIcons")
        settings_grid.addWidget(self.class_name_input, 1, 1)
        
        # Row 3: Output Dir
        settings_grid.addWidget(QLabel("Output Directory:"), 2, 0)
        dir_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit(str(Path.home() / "Desktop" / "FlutterIcons"))
        self.output_dir_btn = QPushButton("Browse")
        self.output_dir_btn.clicked.connect(self.browse_output_dir)
        dir_layout.addWidget(self.output_dir_input)
        dir_layout.addWidget(self.output_dir_btn)
        settings_grid.addLayout(dir_layout, 2, 1)
        
        # Row 4: Font Height & Normalize
        settings_grid.addWidget(QLabel("Font Height:"), 3, 0)
        h_layout = QHBoxLayout()
        self.font_height_input = QSpinBox()
        self.font_height_input.setRange(64, 2048)
        self.font_height_input.setValue(512)
        h_layout.addWidget(self.font_height_input)
        
        self.normalize_check = QCheckBox("Normalize Icon Sizes")
        self.normalize_check.setChecked(True)
        h_layout.addWidget(self.normalize_check)
        h_layout.addStretch()
        settings_grid.addLayout(h_layout, 3, 1)
        
        gen_layout.addLayout(settings_grid)
        
        # Log
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(80)
        self.log_output.setStyleSheet("background-color: #222; color: #0f0; font-family: monospace; font-size: 11px;")
        gen_layout.addWidget(self.log_output)
        
        # Generate Button
        self.generate_btn = QPushButton("Generate Flutter Font")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px; 
                font-weight: bold; 
                padding: 12px; 
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
        gen_layout.addWidget(self.generate_btn)
        
        # --- TAB 2: ICON GALLERY ---
        self.tab_gallery = QWidget()
        self.tabs.addTab(self.tab_gallery, "Icon Gallery")
        gallery_layout = QVBoxLayout()
        self.tab_gallery.setLayout(gallery_layout)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.gallery_content = QWidget()
        self.gallery_grid = QGridLayout()
        self.gallery_grid.setSpacing(10)
        self.gallery_content.setLayout(self.gallery_grid)
        self.scroll_area.setWidget(self.gallery_content)
        gallery_layout.addWidget(self.scroll_area)

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
                
        self.refresh_ui()

    def refresh_ui(self):
        self.refresh_list()
        self.refresh_gallery()

    def refresh_list(self):
        self.list_widget.clear()
        for p in sorted(self.svg_paths):
            self.list_widget.addItem(p)

    def refresh_gallery(self):
        # Clear existing items
        while self.gallery_grid.count():
            item = self.gallery_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Add new items
        cols = 6
        for i, p in enumerate(sorted(self.svg_paths)):
            row = i // cols
            col = i % cols
            item_widget = IconGalleryItem(p)
            self.gallery_grid.addWidget(item_widget, row, col)
        
        # Add a stretch item to push everything up
        self.gallery_grid.setRowStretch(self.gallery_grid.rowCount(), 1)

    def add_svgs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select SVG files", "", "SVG Files (*.svg)")
        if files:
            for f in files:
                self.svg_paths.add(f)
            self.refresh_ui()

    def add_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select SVG Folder")
        if directory:
            path = Path(directory)
            for f in path.rglob("*.svg"):
                self.svg_paths.add(str(f))
            for f in path.rglob("*.SVG"):
                self.svg_paths.add(str(f))
            self.refresh_ui()

    def remove_svgs(self):
        selected = self.list_widget.selectedItems()
        if not selected:
            return
        for item in selected:
            self.svg_paths.discard(item.text())
        self.refresh_ui()

    def clear_svgs(self):
        self.svg_paths.clear()
        self.refresh_ui()
        
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
            self.output_dir_input.text().strip(),
            self.font_height_input.value(),
            self.normalize_check.isChecked()
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

