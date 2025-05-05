import sys
import os
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTextEdit, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class LocationEntryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.location_data = []
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle("Location Links Collection")
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
        title_label = QLabel("Location Links Collection")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        subtitle_label = QLabel("Add links to locations for batch processing")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)
        
        # ===== Input Fields =====
        input_group_layout = QVBoxLayout()
        
        # Location name input
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Location Name:"))
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter location name (e.g., Siirt-Otel)")
        location_layout.addWidget(self.location_input)
        input_group_layout.addLayout(location_layout)
        
        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Google Maps URL (must start with http:// or https://)")
        url_layout.addWidget(self.url_input)
        input_group_layout.addLayout(url_layout)
        
        # Add button
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Entry")
        self.add_button.clicked.connect(self.add_entry)
        self.clear_button = QPushButton("Clear Fields")
        self.clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.clear_button)
        input_group_layout.addLayout(button_layout)
        
        main_layout.addLayout(input_group_layout)
        
        # ===== Data Table =====
        self.data_table = QTableWidget(0, 2)
        self.data_table.setHorizontalHeaderLabels(["Location", "URL"])
        self.data_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.data_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.data_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.data_table)
        
        # ===== Bottom Buttons =====
        bottom_button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save to CSV")
        self.save_button.clicked.connect(self.save_to_csv)
        self.save_as_button = QPushButton("Save As...")
        self.save_as_button.clicked.connect(self.save_as)
        self.remove_selected_button = QPushButton("Remove Selected")
        self.remove_selected_button.clicked.connect(self.remove_selected)
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        
        bottom_button_layout.addWidget(self.save_button)
        bottom_button_layout.addWidget(self.save_as_button)
        bottom_button_layout.addWidget(self.remove_selected_button)
        bottom_button_layout.addWidget(self.exit_button)
        
        main_layout.addLayout(bottom_button_layout)
        
        # Set initial focus
        self.location_input.setFocus()
        
        # Load existing data if file exists
        self.csv_filename = "location_links_collection.csv"
        self.load_existing_data()
        
    def load_existing_data(self):
        """Load data from the CSV file if it exists"""
        if os.path.exists(self.csv_filename):
            try:
                with open(self.csv_filename, mode='r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    headers = next(reader)  # Skip header row
                    
                    for row in reader:
                        if len(row) >= 2:
                            self.location_data.append(row)
                            
                self.update_table()
                QMessageBox.information(self, "Data Loaded", 
                                      f"Loaded {len(self.location_data)} entries from {self.csv_filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not load existing data: {str(e)}")
    
    def add_entry(self):
        """Add a new entry to the data list"""
        location = self.location_input.text().strip()
        url = self.url_input.text().strip()
        
        if not location:
            QMessageBox.warning(self, "Input Error", "Please enter a location name.")
            self.location_input.setFocus()
            return
            
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL.")
            self.url_input.setFocus()
            return
            
        if not (url.startswith("http://") or url.startswith("https://")):
            QMessageBox.warning(self, "Input Error", "URL must start with http:// or https://")
            self.url_input.setFocus()
            return
        
        # Add to data list
        self.location_data.append([location, url])
        self.update_table()
        
        # Clear input fields
        self.clear_fields()
        
        # Set focus back to location input
        self.location_input.setFocus()
    
    def clear_fields(self):
        """Clear input fields"""
        self.location_input.clear()
        self.url_input.clear()
    
    def update_table(self):
        """Update the table with current data"""
        self.data_table.setRowCount(0)  # Clear table
        
        for row_index, (location, url) in enumerate(self.location_data):
            self.data_table.insertRow(row_index)
            self.data_table.setItem(row_index, 0, QTableWidgetItem(location))
            self.data_table.setItem(row_index, 1, QTableWidgetItem(url))
    
    def remove_selected(self):
        """Remove selected rows from the table and data list"""
        selected_rows = set()
        for item in self.data_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.information(self, "Selection", "No rows selected.")
            return
        
        # Convert to list and sort in reverse order (to remove from bottom to top)
        selected_rows = sorted(list(selected_rows), reverse=True)
        
        # Remove from data list
        for row in selected_rows:
            if 0 <= row < len(self.location_data):
                del self.location_data[row]
        
        # Update table
        self.update_table()
    
    def save_to_csv(self):
        """Save data to the default CSV file"""
        if not self.location_data:
            QMessageBox.warning(self, "No Data", "No data to save.")
            return
        
        try:
            with open(self.csv_filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write header
                writer.writerow(["Location", "Link"])
                
                # Write data
                writer.writerows(self.location_data)
            
            QMessageBox.information(self, "Success", f"Saved {len(self.location_data)} entries to {self.csv_filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save data: {str(e)}")
    
    def save_as(self):
        """Save data to a user-specified CSV file"""
        if not self.location_data:
            QMessageBox.warning(self, "No Data", "No data to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if not file_path:
            return  # User canceled
            
        if not file_path.lower().endswith('.csv'):
            file_path += '.csv'
        
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write header
                writer.writerow(["Location", "Link"])
                
                # Write data
                writer.writerows(self.location_data)
            
            QMessageBox.information(self, "Success", f"Saved {len(self.location_data)} entries to {file_path}")
            
            # Update default filename if user saves to a different file
            self.csv_filename = file_path
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save data: {str(e)}")


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
        
        QLabel {{
            color: {TEXT_COLOR.name()};
        }}
        
        QTableWidget {{
            border: 1px solid {ACCENT_COLOR.name()};
            background-color: white;
            gridline-color: #DDDDDD;
        }}
        
        QHeaderView::section {{
            background-color: #EEEEEE;
            border: 1px solid #DDDDDD;
            padding: 4px;
            font-weight: bold;
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
        
        QLineEdit {{
            border: 1px solid {ACCENT_COLOR.name()};
            border-radius: 4px;
            padding: 4px 8px;
            background-color: white;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {PRIMARY_COLOR.name()};
        }}
    """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_styles(app)
    window = LocationEntryApp()
    window.show()
    sys.exit(app.exec_())