#include <wx-3.2/wx/wx.h>
#include <map>
#include <string>
#include <set>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <cstdlib>
#include <iostream>

// Define games for different platforms
std::map<std::string, std::string> windows_games = {
    {"Cytrine", "C:\\Program files\\Cytrine\\engine64.exe"},
    {"Cytrine dedicated server", "C:\\Program files\\Cytrine\\server64.exe"}
};

std::map<std::string, std::string> linux_games = {
    {"Cytrine", "/home/paul/QuakeSandbox-main/engine64"},
    {"Cytrine dedicated server", "/home/paul/QuakeSandbox-main/server64"}
};

class GameLauncher : public wxFrame {
private:
    wxListBox* game_list;
    wxBoxSizer* options_box;
    wxStaticText* options_label;
    wxButton* play_windows_button;
    wxButton* play_linux_button;
    wxButton* stop_button;
    pid_t current_process;

public:
    GameLauncher(const wxString& title)
        : wxFrame(NULL, wxID_ANY, title, wxDefaultPosition, wxSize(800, 400)), current_process(0) {
        
        // Create game list
        wxBoxSizer* main_layout = new wxBoxSizer(wxHORIZONTAL);
        game_list = new wxListBox(this, wxID_ANY, wxDefaultPosition, wxDefaultSize, 0, nullptr, wxLB_SINGLE);
        std::set<std::string> game_names;
        for (const auto& pair : windows_games) game_names.insert(pair.first);
        for (const auto& pair : linux_games) game_names.insert(pair.first);

        for (const auto& game : game_names) {
            game_list->Append(game);
        }

        game_list->Bind(wxEVT_LISTBOX, &GameLauncher::onGameSelected, this);

        // Create options box
        options_box = new wxBoxSizer(wxVERTICAL);
        options_label = new wxStaticText(this, wxID_ANY, "Select a game");
        
        play_windows_button = new wxButton(this, wxID_ANY, "PLAY (Windows)");
        play_linux_button = new wxButton(this, wxID_ANY, "PLAY (Linux)");
        stop_button = new wxButton(this, wxID_ANY, "STOP");

        play_windows_button->Enable(false);
        play_linux_button->Enable(false);
        stop_button->Enable(false);

        play_windows_button->Bind(wxEVT_BUTTON, &GameLauncher::onLaunchGame, this, wxID_ANY);
        play_linux_button->Bind(wxEVT_BUTTON, &GameLauncher::onLaunchGame, this, wxID_ANY);
        stop_button->Bind(wxEVT_BUTTON, &GameLauncher::onStopGame, this);

        options_box->Add(options_label, 0, wxALL, 5);
        options_box->Add(play_windows_button, 0, wxALL, 5);
        options_box->Add(play_linux_button, 0, wxALL, 5);
        options_box->Add(stop_button, 0, wxALL, 5);

        main_layout->Add(game_list, 1, wxEXPAND | wxALL, 10);
        main_layout->Add(options_box, 0, wxALIGN_CENTER_VERTICAL | wxALL, 10);

        SetSizer(main_layout);
    }

    void onGameSelected(wxCommandEvent& event) {
        wxString game_name = game_list->GetStringSelection();
        
        // Update label
        wxString label_text = "Selected: " + game_name;
        options_label->SetLabel(label_text);
        
        // Enable buttons based on availability
        play_windows_button->Enable(windows_games.find(std::string(game_name.mb_str())) != windows_games.end());
        play_linux_button->Enable(linux_games.find(std::string(game_name.mb_str())) != linux_games.end());
        stop_button->Enable(current_process != 0);
    }

    void onLaunchGame(wxCommandEvent& event) {
        wxString platform = event.GetEventObject() == play_windows_button ? "windows" : "linux";
        wxString game_name = game_list->GetStringSelection();
        std::string game_path;

        if (platform == "windows" && windows_games.find(std::string(game_name.mb_str())) != windows_games.end()) {
            game_path = windows_games[std::string(game_name.mb_str())];
        } else if (platform == "linux" && linux_games.find(std::string(game_name.mb_str())) != linux_games.end()) {
            game_path = linux_games[std::string(game_name.mb_str())];
        }

        if (!game_path.empty()) {
            execute_game(game_path);
        }
    }

    void onStopGame(wxCommandEvent& event) {
        stop_game();
    }

private:
    void execute_game(const std::string& game_path) {
        if (access(game_path.c_str(), F_OK) != -1) {
            try {
                #ifdef _WIN32
                    // Windows-specific implementation would go here
                    system(("\"" + game_path + "\"").c_str());
                #else
                    current_process = fork();
                    if (current_process == 0) {
                        execl("/bin/sh", "sh", "-c", game_path.c_str(), NULL);
                        exit(1);
                    }
                #endif
            } catch (const std::exception &e) {
                options_label->SetLabel("Error: Unable to launch game: " + std::string(e.what()));
            }
        } else {
            options_label->SetLabel("Error: Path not found");
        }
    }

    void stop_game() {
        if (current_process != 0) {
            try {
                #ifdef _WIN32
                    // Windows-specific implementation would go here
                    system(("taskkill /F /PID " + std::to_string(current_process)).c_str());
                #else
                    kill(current_process, SIGTERM);
                #endif
                current_process = 0;
                options_label->SetLabel("Game stopped");
                stop_button->Enable(false);
            } catch (const std::exception &e) {
                options_label->SetLabel("Error stopping game: " + std::string(e.what()));
            }
        }
    }
};

class Launcher : public wxApp {
public:
    virtual bool OnInit() {
        GameLauncher* launcher = new GameLauncher("Game Launcher");
        launcher->Show(true);
        return true;
    }
};

wxIMPLEMENT_APP(Launcher);
