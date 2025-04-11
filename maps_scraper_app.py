import sys
import os
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QSpinBox, QPushButton, QTextEdit, 
                            QFileDialog, QProgressBar, QGroupBox, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette

# Import the scraper modules
import location_scrapper
import review_scrapper2

class WorkerThread(QThread):
    """Worker thread for running the scraping operations without freezing the UI"""
    update_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, url, scroll_location, scroll_review, folder_name, html_folder_name):
        super().__init__()
        self.url = url
        self.scroll_location = scroll_location
        self.scroll_review = scroll_review
        self.folder_name = folder_name
        self.html_folder_name = html_folder_name
        self.csv_path = "location_links.csv"
        # Store original print function
        self.original_print = print
        # Flag to check if stop was requested
        self.stop_requested = False
    
    def custom_print(self, *args, **kwargs):
        """Custom print function that sends output to our signal"""
        text = " ".join(map(str, args))
        self.update_signal.emit(text)
        self.original_print(*args, **kwargs)
    
    def stop(self):
        """Request the thread to stop"""
        self.stop_requested = True
        self.update_signal.emit("⚠️ Stop requested. Finishing current operation...")
    
    def run(self):
        try:
            # Create a print redirection using monkeypatching at the module level
            import builtins
            builtins.print = self.custom_print
            
            # Step 1: Scrape location links
            self.update_signal.emit("🔍 Starting location scraping...")
            
            if not self.stop_requested:
                location_scrapper.locationScrapper(self.url, self.scroll_location)
                self.progress_signal.emit(25)
                self.update_signal.emit("📋 Location links scraped successfully.")
            
            # Step 2: Wait a bit and then get the links
            if not self.stop_requested:
                time.sleep(2)
                self.update_signal.emit("📊 Processing location links...")
                location_links = review_scrapper2.get_location_links(self.csv_path)
                total_links = len(location_links)
                self.update_signal.emit(f"🏢 Found {total_links} locations to process.")
                self.progress_signal.emit(30)
            
            # Step 3: Scrape reviews for each location
            if not self.stop_requested:
                for i, link in enumerate(location_links):
                    if self.stop_requested:
                        self.update_signal.emit("🛑 Scraping stopped by user.")
                        break
                        
                    progress = 30 + int(70 * ((i + 1) / total_links))
                    self.update_signal.emit(f"🔍 Processing location {i+1}/{total_links}...")
                    review_scrapper2.scrape_reviews_and_save_csv(
                        link, self.scroll_review, self.folder_name, self.html_folder_name
                    )
                    self.progress_signal.emit(progress)
            
            if not self.stop_requested:
                self.update_signal.emit("✅ All scraping tasks completed successfully!")
                self.progress_signal.emit(100)
            
            # Restore the original print function
            builtins.print = self.original_print
            self.finished_signal.emit(not self.stop_requested)
            
        except Exception as e:
            self.update_signal.emit(f"❌ Error occurred: {str(e)}")
            # Restore the original print function
            import builtins
            builtins.print = self.original_print
            self.finished_signal.emit(False)


class MapsScraperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle("Google Maps Scraper")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(700, 500)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== Header =====
        header_layout = QVBoxLayout()
        title_label = QLabel("Google Maps Location & Review Scraper")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        subtitle_label = QLabel("Scrape location links and reviews from Google Maps")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)
        
        # ===== Input Configuration Group =====
        config_group = QGroupBox("Configuration")
        config_layout = QFormLayout()
        config_group.setLayout(config_layout)
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Google Maps search URL...")
        config_layout.addRow(QLabel("Google Maps URL:"), self.url_input)
        
        # Scroll config
        scroll_layout = QHBoxLayout()
        self.location_scroll = QSpinBox()
        self.location_scroll.setRange(1, 100)
        self.location_scroll.setValue(10)
        self.review_scroll = QSpinBox()
        self.review_scroll.setRange(1, 500)
        self.review_scroll.setValue(150)
        
        scroll_layout.addWidget(QLabel("Location Scrolls:"))
        scroll_layout.addWidget(self.location_scroll)
        scroll_layout.addSpacing(20)
        scroll_layout.addWidget(QLabel("Review Scrolls:"))
        scroll_layout.addWidget(self.review_scroll)
        config_layout.addRow("Scroll Settings:", scroll_layout)
        
        # Folder names
        folder_layout = QHBoxLayout()
        self.folder_name = QLineEdit("Şanlıurfa_Müzeler")
        self.html_folder_name = QLineEdit("HTML_Reviews_Şanlıurfa_Müzeler")
        
        folder_layout.addWidget(QLabel("CSV Folder:"))
        folder_layout.addWidget(self.folder_name)
        folder_layout.addSpacing(20)
        folder_layout.addWidget(QLabel("HTML Folder:"))
        folder_layout.addWidget(self.html_folder_name)
        config_layout.addRow("Output Folders:", folder_layout)
        
        main_layout.addWidget(config_group)
        
        # ===== Action Buttons =====
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Scraping")
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.start_scraping)
        
        self.stop_button = QPushButton("Stop Scraping")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.clicked.connect(self.stop_scraping)
        self.stop_button.setEnabled(False)
        
        self.clear_button = QPushButton("Clear Log")
        self.clear_button.setMinimumHeight(40)
        self.clear_button.clicked.connect(self.clear_log)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        main_layout.addLayout(button_layout)
        
        # ===== Progress Bar =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setMinimumHeight(30)
        main_layout.addWidget(self.progress_bar)
        
        # ===== Log Output =====
        log_group = QGroupBox("Progress Log")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 10))
        self.log_output.setMinimumHeight(200)
        log_layout.addWidget(self.log_output)
        
        main_layout.addWidget(log_group)
        
        # Load the last URL if available
        self.load_previous_config()
        
        # Initialize thread as None
        self.worker_thread = None
        
        # Show the window
        self.show()
        
    def load_previous_config(self):
        try:
            self.url_input.setText("https://www.google.com/maps/search/m%C3%BCze+near+%C5%9Eanl%C4%B1urfa/@37.1824636,38.7526177,13z/data=!4m2!2m1!6e1?entry=ttu&g_ep=EgoyMDI1MDQwOS4wIKXMDSoASAFQAw%3D%3D")
        except:
            pass
    
    def add_to_log(self, message):
        self.log_output.append(message)
        # Auto-scroll to the bottom
        cursor = self.log_output.textCursor()
        cursor.movePosition(cursor.End)
        self.log_output.setTextCursor(cursor)
    
    def clear_log(self):
        self.log_output.clear()
    
    def start_scraping(self):
        # Validate inputs
        if not self.url_input.text():
            QMessageBox.warning(self, "Input Error", "Please enter a valid Google Maps URL.")
            return
        
        # Disable start button and enable stop button
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.clear_button.setEnabled(False)
        
        # Reset progress
        self.progress_bar.setValue(0)
        
        # Get parameters
        url = self.url_input.text()
        scroll_location = self.location_scroll.value()
        scroll_review = self.review_scroll.value()
        folder_name = self.folder_name.text()
        html_folder_name = self.html_folder_name.text()
        
        # Create and start worker thread
        self.worker_thread = WorkerThread(
            url, scroll_location, scroll_review, folder_name, html_folder_name
        )
        self.worker_thread.update_signal.connect(self.add_to_log)
        self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
        self.worker_thread.finished_signal.connect(self.scraping_finished)
        
        self.add_to_log("🚀 Starting the scraping process...")
        self.worker_thread.start()
    
    def stop_scraping(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.add_to_log("🛑 Requesting to stop scraping...")
            self.worker_thread.stop()
            self.stop_button.setEnabled(False)
            self.stop_button.setText("Stopping...")
    
    def scraping_finished(self, success):
        # Re-enable start button and disable stop button
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stop_button.setText("Stop Scraping")
        self.clear_button.setEnabled(True)
        
        if success:
            self.add_to_log("🎉 Scraping process completed successfully!")
            QMessageBox.information(self, "Success", "The scraping process has been completed successfully!")
        else:
            self.add_to_log("❌ Scraping process terminated with errors or was stopped.")
            if self.worker_thread and self.worker_thread.stop_requested:
                QMessageBox.information(self, "Stopped", "The scraping process was stopped by user.")
            else:
                QMessageBox.warning(self, "Error", "The scraping process encountered errors. Check the log for details.")


def apply_styles(app):
    """Apply modern styling to the application with the provided color palette"""
    app.setStyle("Fusion")
    
    # Define color constants from the color palette
    PRIMARY_COLOR = QColor("#3A59D1")       # Dark blue
    SECONDARY_COLOR = QColor("#3D90D7")     # Medium blue
    ACCENT_COLOR = QColor("#7AC6D2")        # Light blue/teal
    BACKGROUND_COLOR = QColor("#B5FCCD")    # Mint green
    TEXT_COLOR = QColor("#333333")          # Dark gray for text
    
    # Define a color palette
    palette = QPalette()
    
    # Set colors
    palette.setColor(QPalette.Window, QColor(245, 245, 245))  # Light background
    palette.setColor(QPalette.WindowText, TEXT_COLOR)
    palette.setColor(QPalette.Base, QColor(255, 255, 255))    # White
    palette.setColor(QPalette.AlternateBase, BACKGROUND_COLOR.lighter(115))
    palette.setColor(QPalette.ToolTipBase, PRIMARY_COLOR)
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, TEXT_COLOR)
    palette.setColor(QPalette.Button, SECONDARY_COLOR.lighter(130))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, PRIMARY_COLOR)
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    # Apply the palette
    app.setPalette(palette)
    
    # Set stylesheet for additional customization
    app.setStyleSheet(f"""
        QMainWindow, QDialog {{
            background-color: #F5F5F5;
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {ACCENT_COLOR.name()};
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
            background-color: white;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: {PRIMARY_COLOR.name()};
        }}
        
        QPushButton {{
            background-color: {SECONDARY_COLOR.name()};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {PRIMARY_COLOR.name()};
        }}
        
        QPushButton:pressed {{
            background-color: {PRIMARY_COLOR.darker(120).name()};
        }}
        
        QPushButton:disabled {{
            background-color: #cccccc;
            color: #888888;
        }}
        
        #start_button {{
            background-color: {PRIMARY_COLOR.name()};
        }}
        
        #stop_button {{
            background-color: #D13A3A;  /* Red color for stop button */
        }}
        
        #stop_button:hover {{
            background-color: #B03030;
        }}
        
        QLineEdit, QSpinBox {{
            border: 1px solid {ACCENT_COLOR.name()};
            border-radius: 4px;
            padding: 4px 8px;
            background-color: white;
        }}
        
        QLineEdit:focus, QSpinBox:focus {{
            border: 2px solid {PRIMARY_COLOR.name()};
        }}
        
        QProgressBar {{
            border: 1px solid {ACCENT_COLOR.name()};
            border-radius: 4px;
            text-align: center;
            background-color: white;
        }}
        
        QProgressBar::chunk {{
            background-color: {PRIMARY_COLOR.name()};
            width: 10px;
            margin: 0.5px;
        }}
        
        QTextEdit {{
            border: 1px solid {ACCENT_COLOR.name()};
            border-radius: 4px;
            background-color: white;
        }}
        
        QLabel {{
            color: {TEXT_COLOR.name()};
        }}
        
        QLabel[title="true"] {{
            color: {PRIMARY_COLOR.name()};
            font-weight: bold;
        }}
    """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_styles(app)
    window = MapsScraperApp()
    sys.exit(app.exec_())