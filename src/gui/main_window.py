"""
Main GUI Window - Sports Prediction Platform
PyQt6-based desktop application
"""

import logging
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QProgressBar, QStatusBar, QMenuBar, QMenu, QDialog,
    QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon
from pathlib import Path

logger = logging.getLogger("gui")


class ActivationDialog(QDialog):
    """License activation dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Activate Application")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Sports Forecasting Platform - Activation")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Enter your activation key below to unlock the application.\n"
            "Keys are valid for 90 days and can be renewed at any time."
        )
        layout.addWidget(instructions)
        
        # License key input
        layout.addWidget(QLabel("License Key:"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Paste your license key here...")
        layout.addWidget(self.key_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.activate_btn = QPushButton("Activate")
        self.activate_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 8px; font-weight: bold;")
        button_layout.addWidget(self.activate_btn)
        
        cancel_btn = QPushButton("Exit")
        cancel_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px;")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_key(self) -> str:
        return self.key_input.text().strip()


class SportsTab(QWidget):
    """Tab for individual sport predictions"""
    
    def __init__(self, sport_name: str):
        super().__init__()
        self.sport_name = sport_name
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"{self.sport_name} Predictions")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Games table
        self.games_table = QTableWidget()
        self.games_table.setColumnCount(5)
        self.games_table.setHorizontalHeaderLabels([
            "Time", "Matchup", "O/U Pred", "Spread Pred", "Win Pred"
        ])
        self.games_table.setMinimumHeight(300)
        layout.addWidget(self.games_table)
        
        # Refresh button
        refresh_btn = QPushButton(f"Fetch {self.sport_name} Games")
        refresh_btn.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        self.setLayout(layout)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, activation_manager, api_client, prediction_service):
        super().__init__()
        self.activation_manager = activation_manager
        self.api_client = api_client
        self.prediction_service = prediction_service
        
        self.setWindowTitle("Sports Forecasting Platform v1.0")
        self.setMinimumSize(1200, 800)
        
        self.init_ui()
        self.init_menu()
        self.update_status()
    
    def init_ui(self):
        """Initialize user interface"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout()
        
        # Header with activation status
        header_layout = QHBoxLayout()
        
        app_title = QLabel(" Sports Prediction Platform")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        app_title.setFont(title_font)
        header_layout.addWidget(app_title)
        
        header_layout.addStretch()
        
        self.status_label = QLabel("Status: Initializing...")
        self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        header_layout.addWidget(self.status_label)
        
        activate_btn = QPushButton(" Activate")
        activate_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 5px 15px;")
        activate_btn.clicked.connect(self.show_activation_dialog)
        header_layout.addWidget(activate_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tabs for each sport
        self.tabs = QTabWidget()
        
        self.sport_tabs = {}
        for sport in ["NFL", "NBA", "MLB", "NHL"]:
            tab = SportsTab(sport)
            self.sport_tabs[sport] = tab
            self.tabs.addTab(tab, sport)
        
        main_layout.addWidget(self.tabs)
        
        # Status/Log panel at bottom
        log_layout = QVBoxLayout()
        
        log_label = QLabel("System Log")
        log_font = QFont()
        log_font.setBold(True)
        log_label.setFont(log_font)
        log_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("background-color: #2c3e50; color: #ecf0f1; font-family: Courier;")
        log_layout.addWidget(self.log_text)
        
        main_layout.addLayout(log_layout)
        
        central.setLayout(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def init_menu(self):
        """Initialize menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        activate_action = file_menu.addAction("Activate License")
        activate_action.triggered.connect(self.show_activation_dialog)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        refresh_action = tools_menu.addAction("Refresh All Data")
        refresh_action.triggered.connect(self.refresh_data)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
    
    def update_status(self):
        """Update activation status display"""
        is_active, message = self.activation_manager.check_activation()
        
        if is_active:
            self.status_label.setText(f" {message}")
            self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.status_label.setText(" Not Activated")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        self.add_log(message)
    
    def show_activation_dialog(self):
        """Show activation dialog"""
        dialog = ActivationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            key = dialog.get_key()
            if key:
                success, message = self.activation_manager.activate(key)
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.update_status()
                else:
                    QMessageBox.critical(self, "Error", message)
                    self.add_log(f" Activation failed: {message}")
    
    def refresh_data(self):
        """Refresh all prediction data"""
        self.add_log(" Refreshing data from API...")
        
        for sport in ["NFL", "NBA", "MLB", "NHL"]:
            result = self.api_client.fetch_games(sport)
            if result.get("status") == "success":
                self.add_log(f" Updated {sport} games")
            else:
                self.add_log(f" Failed to update {sport}")
    
    def add_log(self, message: str):
        """Add message to log panel"""
        current = self.log_text.toPlainText()
        timestamp = __import__('datetime').datetime.now().strftime("%H:%M:%S")
        new_message = f"[{timestamp}] {message}"
        
        if current:
            self.log_text.setPlainText(current + "\n" + new_message)
        else:
            self.log_text.setPlainText(new_message)
        
        # Scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Sports Forecasting Platform",
            "Sports Prediction Platform v1.0\n\n"
            "Real-time AI-powered predictions for NFL, NBA, MLB, and NHL\n"
            "Featuring ML models, SHAP explainability, and Monte Carlo simulations\n\n"
            " 2024 Sports Analytics"
        )
