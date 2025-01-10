import sys
import os
import signal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QFileDialog, QScrollArea, QListWidgetItem
)
from PyQt5.QtCore import Qt

# Define games for different platforms here.
windows_games = {
    "Cytrine": "C:\\Program files\\Cytrine\\engine64.exe",
    "Cytrine dedicated server": "C:\\Program files\\Cytrine\\server64.exe"
}

mac_games = {
    "Cytrine": "/home/paul/QuakeSandbox-main/engineosx",
    "Cytrine dedicated server": "/home/paul/QuakeSandbox-main/serverosx"
}

linux_games = {
    "Cytrine": "/home/paul/QuakeSandbox-main/engine64",
    "Cytrine dedicated server": "/home/paul/QuakeSandbox-main/server64"
}

class GameLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Launcher")
        self.setGeometry(100, 100, 800, 400)

        self.main_layout = QHBoxLayout()

        # Scrollable list of games
        self.game_list = QListWidget()
        for game in set(windows_games.keys()).union(mac_games.keys(), linux_games.keys()):
            item = QListWidgetItem(game)
            self.game_list.addItem(item)
        self.game_list.currentItemChanged.connect(self.display_game_options)

        # Right panel for game options
        self.options_layout = QVBoxLayout()
        self.options_label = QLabel("Select a game")
        self.options_label.setAlignment(Qt.AlignCenter)

        self.play_windows_button = QPushButton("PLAY (Windows)")
        self.play_windows_button.clicked.connect(lambda: self.launch_game("windows"))
        self.play_windows_button.setEnabled(False)

        self.play_mac_button = QPushButton("PLAY (Mac)")
        self.play_mac_button.clicked.connect(lambda: self.launch_game("mac"))
        self.play_mac_button.setEnabled(False)

        self.play_linux_button = QPushButton("PLAY (Linux)")
        self.play_linux_button.clicked.connect(lambda: self.launch_game("linux"))
        self.play_linux_button.setEnabled(False)

        self.stop_button = QPushButton("STOP")
        self.stop_button.clicked.connect(self.stop_game)
        self.stop_button.setEnabled(False)

        self.options_layout.addWidget(self.options_label)
        self.options_layout.addWidget(self.play_windows_button)
        self.options_layout.addWidget(self.play_mac_button)
        self.options_layout.addWidget(self.play_linux_button)
        self.options_layout.addWidget(self.stop_button)
        self.options_layout.addStretch()

        self.main_layout.addWidget(self.game_list, 1)
        self.main_layout.addLayout(self.options_layout, 2)

        self.setLayout(self.main_layout)

        self.current_process = None

    def display_game_options(self, current_item):
        if current_item:
            game_name = current_item.text()
            self.options_label.setText(f"Selected: {game_name}")

            # Enable or disable buttons based on platform availability
            self.play_windows_button.setEnabled(game_name in windows_games)
            self.play_mac_button.setEnabled(game_name in mac_games)
            self.play_linux_button.setEnabled(game_name in linux_games)
            self.stop_button.setEnabled(self.current_process is not None)
        else:
            self.options_label.setText("Select a game")
            self.play_windows_button.setEnabled(False)
            self.play_mac_button.setEnabled(False)
            self.play_linux_button.setEnabled(False)
            self.stop_button.setEnabled(False)

    def launch_game(self, platform):
        current_item = self.game_list.currentItem()
        if current_item:
            game_name = current_item.text()
            if platform == "windows" and game_name in windows_games:
                game_path = windows_games[game_name]
                self.execute_game(game_path)
            elif platform == "mac" and game_name in mac_games:
                game_path = mac_games[game_name]
                self.execute_game(game_path)
            elif platform == "linux" and game_name in linux_games:
                game_path = linux_games[game_name]
                self.execute_game(game_path)

    def execute_game(self, game_path):
        if os.path.isfile(game_path):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(f'"{game_path}"')  # Enclose in quotes for spaces
                else:  # macOS/Linux
                    self.current_process = os.fork()
                    if self.current_process == 0:  # Child process
                        os.execlp("sh", "sh", "-c", f'"{game_path}"')  # Use shell execution
            except Exception as e:
                self.options_label.setText(f"Error: Unable to launch game: {e}")
        else:
            self.options_label.setText(f"Error: Path not found")

    def stop_game(self):
        if self.current_process:
            try:
                if os.name == 'nt':
                    os.system(f"taskkill /F /PID {self.current_process}")
                else:
                    os.kill(self.current_process, signal.SIGTERM)
                self.current_process = None
                self.options_label.setText("Game stopped")
                self.stop_button.setEnabled(False)
            except Exception as e:
                self.options_label.setText(f"Error stopping game: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = GameLauncher()
    launcher.show()
    sys.exit(app.exec_())
