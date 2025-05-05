import sys
import os
import time
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QSpinBox, QPushButton, QTextEdit, 
                            QFileDialog, QProgressBar, QGroupBox, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

# Import the scraper modules
import location_scrapper
import review_scrapper2

class BatchWorkerThread(QThread):
    """Worker thread for running the batch scraping operations"""
    update_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, csv_path, location_scroll, scroll_review):
        super().__init__()
        self.csv_path = csv_path
        self.location_scroll = location_scroll
        self.scroll_review = scroll_review
        self.original_print = print
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
            # Redirect print statements
            import builtins
            builtins.print = self.custom_print
            
            # Read the CSV file
            df = pd.read_csv(self.csv_path)
            if "Location" not in df.columns or "Link" not in df.columns:
                raise ValueError("CSV file must contain 'Location' and 'Link' columns")
            
            total_locations = len(df)
            self.update_signal.emit(f"📊 Found {total_locations} locations to process")
            
            processed = 0
            for index, row in df.iterrows():
                if self.stop_requested:
                    self.update_signal.emit("🛑 Scraping stopped by user.")
                    break
                
                location_name = row['Location']
                url = row['Link']
                
                # Create main folder for this location
                main_folder = location_name
                csv_folder = os.path.join(main_folder, "csv_reviews")
                html_folder = os.path.join(main_folder, "html_reviews")
                
                # Create all necessary directories
                os.makedirs(main_folder, exist_ok=True)
                os.makedirs(csv_folder, exist_ok=True)
                os.makedirs(html_folder, exist_ok=True)
                
                self.update_signal.emit(f"🔍 Processing {location_name} ({index + 1}/{total_locations})")
                
                # Step 1: Scrape location links
                if not self.stop_requested:
                    location_scrapper.locationScrapper(url, self.location_scroll)
                    
                    # Move location_links.csv to the location's folder
                    if os.path.exists("location_links.csv"):
                        os.replace("location_links.csv", os.path.join(main_folder, "location_links.csv"))
                    
                # Step 2: Get the location links
                if not self.stop_requested:
                    time.sleep(2)
                    location_links = review_scrapper2.get_location_links(os.path.join(main_folder, "location_links.csv"))
                    
                    # Process each location
                    for link in location_links:
                        if self.stop_requested:
                            break
                        review_scrapper2.scrape_reviews_and_save_csv(
                            link, self.scroll_review, csv_folder, html_folder
                        )
                
                processed += 1
                progress = int((processed / total_locations) * 100)
                self.progress_signal.emit(progress)
                
                if self.stop_requested:
                    break
            
            if not self.stop_requested:
                self.update_signal.emit("✅ All batch scraping tasks completed successfully!")
                self.progress_signal.emit(100)
            
            # Restore original print function
            builtins.print = self.original_print
            self.finished_signal.emit(not self.stop_requested)
            
        except Exception as e:
            self.update_signal.emit(f"❌ Error occurred: {str(e)}")
            builtins.print = self.original_print
            self.finished_signal.emit(False)


class BatchMapsScraperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle("Batch Google Maps Scraper")
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
        title_label = QLabel("Batch Google Maps Review Scraper")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        subtitle_label = QLabel("Process multiple locations from a CSV file")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)
        
        # ===== Input Configuration Group =====
        config_group = QGroupBox("Configuration")
        config_layout = QFormLayout()
        config_group.setLayout(config_layout)
        
        # CSV File Selection
        file_layout = QHBoxLayout()
        self.csv_path_input = QLineEdit()
        self.csv_path_input.setPlaceholderText("Select locations CSV file...")
        self.csv_path_input.setReadOnly(True)
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_csv)
        
        file_layout.addWidget(self.csv_path_input)
        file_layout.addWidget(browse_button)
        config_layout.addRow("Locations CSV:", file_layout)
        
        # Location scroll configuration
        self.location_scroll = QSpinBox()
        self.location_scroll.setRange(1, 500)
        self.location_scroll.setValue(1)
        config_layout.addRow("Location Scrolls:", self.location_scroll)
        
        # Review scroll configuration
        self.review_scroll = QSpinBox()
        self.review_scroll.setRange(1, 500)
        self.review_scroll.setValue(150)
        config_layout.addRow("Review Scrolls:", self.review_scroll)
        
        main_layout.addWidget(config_group)
        
        # ===== Action Buttons =====
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Batch Scraping")
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
        
        # Initialize thread as None
        self.worker_thread = None
        
        # Try to load the default CSV file
        default_csv = "location_links_collection.csv"
        if os.path.exists(default_csv):
            self.csv_path_input.setText(os.path.abspath(default_csv))
        
        # Show the window
        self.show()
    
    def browse_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Locations CSV File", "", "CSV Files (*.csv);;All Files (*.*)"
        )
        if file_path:
            self.csv_path_input.setText(file_path)
    
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
        if not self.csv_path_input.text():
            QMessageBox.warning(self, "Input Error", "Please select a locations CSV file.")
            return
        
        # Disable start button and enable stop button
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.clear_button.setEnabled(False)
        
        # Reset progress
        self.progress_bar.setValue(0)
        
        # Get parameters
        csv_path = self.csv_path_input.text()
        location_scroll = self.location_scroll.value()
        scroll_review = self.review_scroll.value()
        
        # Create and start worker thread
        self.worker_thread = BatchWorkerThread(csv_path, location_scroll, scroll_review)
        self.worker_thread.update_signal.connect(self.add_to_log)
        self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
        self.worker_thread.finished_signal.connect(self.scraping_finished)
        
        self.add_to_log("🚀 Starting the batch scraping process...")
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
            self.add_to_log("🎉 Batch scraping process completed successfully!")
            QMessageBox.information(self, "Success", "The batch scraping process has been completed successfully!")
        else:
            self.add_to_log("❌ Batch scraping process terminated with errors or was stopped.")
            if self.worker_thread and self.worker_thread.stop_requested:
                QMessageBox.information(self, "Stopped", "The batch scraping process was stopped by user.")
            else:
                QMessageBox.warning(self, "Error", "The batch scraping process encountered errors. Check the log for details.")


def apply_styles(app):
    """Apply modern styling to the application"""
    app.setStyle("Fusion")
    
    # Define colors
    PRIMARY_COLOR = QColor("#3A59D1")
    SECONDARY_COLOR = QColor("#3D90D7")
    ACCENT_COLOR = QColor("#7AC6D2")
    TEXT_COLOR = QColor("#333333")
    
    # Apply stylesheet
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
        
        QPushButton:disabled {{
            background-color: #cccccc;
            color: #888888;
        }}
        
        QLineEdit, QSpinBox {{
            border: 1px solid {ACCENT_COLOR.name()};
            border-radius: 4px;
            padding: 4px 8px;
            background-color: white;
        }}
        
        QProgressBar {{
            border: 1px solid {ACCENT_COLOR.name()};
            border-radius: 4px;
            text-align: center;
            background-color: white;
        }}
        
        QProgressBar::chunk {{
            background-color: {PRIMARY_COLOR.name()};
        }}
        
        QTextEdit {{
            border: 1px solid {ACCENT_COLOR.name()};
            border-radius: 4px;
            background-color: white;
        }}
    """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_styles(app)
    window = BatchMapsScraperApp()
    sys.exit(app.exec_())