import os
import signal
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

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

class GameLauncher(Gtk.Window):
    def __init__(self):
        super().__init__(title="Game Launcher")
        self.set_default_size(800, 400)

        self.main_layout = Gtk.HBox(spacing=10)

        # Scrollable list of games
        self.game_list = Gtk.ListBox()
        for game in set(windows_games.keys()).union(mac_games.keys(), linux_games.keys()):
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=game)
            row.add(label)
            self.game_list.add(row)

        self.game_list.connect("row-activated", self.display_game_options)

        # Right panel for game options
        self.options_box = Gtk.VBox(spacing=10)
        self.options_label = Gtk.Label(label="Select a game")
        self.options_label.set_alignment(0.5, 0.5)

        self.play_windows_button = Gtk.Button(label="PLAY (Windows)")
        self.play_windows_button.set_sensitive(False)
        self.play_windows_button.connect("clicked", lambda btn: self.launch_game("windows"))

        self.play_mac_button = Gtk.Button(label="PLAY (Mac)")
        self.play_mac_button.set_sensitive(False)
        self.play_mac_button.connect("clicked", lambda btn: self.launch_game("mac"))

        self.play_linux_button = Gtk.Button(label="PLAY (Linux)")
        self.play_linux_button.set_sensitive(False)
        self.play_linux_button.connect("clicked", lambda btn: self.launch_game("linux"))

        self.stop_button = Gtk.Button(label="STOP")
        self.stop_button.set_sensitive(False)
        self.stop_button.connect("clicked", self.stop_game)

        self.options_box.pack_start(self.options_label, False, False, 0)
        self.options_box.pack_start(self.play_windows_button, False, False, 0)
        self.options_box.pack_start(self.play_mac_button, False, False, 0)
        self.options_box.pack_start(self.play_linux_button, False, False, 0)
        self.options_box.pack_start(self.stop_button, False, False, 0)

        self.main_layout.pack_start(self.game_list, True, True, 0)
        self.main_layout.pack_start(self.options_box, False, False, 0)

        self.add(self.main_layout)

        self.current_process = None

    def display_game_options(self, list_box, row):
        game_name = row.get_child().get_text()
        self.options_label.set_text(f"Selected: {game_name}")

        # Enable or disable buttons based on platform availability
        self.play_windows_button.set_sensitive(game_name in windows_games)
        self.play_mac_button.set_sensitive(game_name in mac_games)
        self.play_linux_button.set_sensitive(game_name in linux_games)
        self.stop_button.set_sensitive(self.current_process is not None)

    def launch_game(self, platform):
        current_row = self.game_list.get_selected_row()
        if current_row:
            game_name = current_row.get_child().get_text()
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
                self.options_label.set_text(f"Error: Unable to launch game: {e}")
        else:
            self.options_label.set_text(f"Error: Path not found")

    def stop_game(self, button):
        if self.current_process:
            try:
                if os.name == 'nt':
                    os.system(f"taskkill /F /PID {self.current_process}")
                else:
                    os.kill(self.current_process, signal.SIGTERM)
                self.current_process = None
                self.options_label.set_text("Game stopped")
                self.stop_button.set_sensitive(False)
            except Exception as e:
                self.options_label.set_text(f"Error stopping game: {e}")

if __name__ == "__main__":
    win = GameLauncher()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
