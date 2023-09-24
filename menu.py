import tkinter as tk
import json
from main import GUI
import webbrowser


def open_link(event):
    webbrowser.open("https://github.com/mdrahman04")


scoreboard_window_open = False


class StartPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Simon Game")
        self.root.geometry("400x400")
        self.root.minsize(400, 400)
        self.root.configure(bg="black")

        title_label = tk.Label(root, text="Simon Game", font=("Courier New", 24, "bold"), fg="white", bg="black")
        title_label.pack(pady=30)
        title_label = tk.Label(root, text="Watch, Remember, Repeat!", font=("Courier New", 14), fg="#ff9b05", bg="black")
        title_label.pack(pady=10)

        play_button = tk.Button(root, text="Play Normal", command=self.start_game, font=("Arial", 16), fg="white",
                                bg="green")
        play_button.pack(pady=5)

        scoreboard_button = tk.Button(root, text="Scoreboard", command=self.show_scoreboard, font=("Arial", 16),
                                      fg="white", bg="blue")
        scoreboard_button.pack(pady=5)

        quit_button = tk.Button(root, text="Quit", command=root.destroy, font=("Arial", 16), fg="white", bg="red")
        quit_button.pack(pady=5)

        title_text = tk.Text(root, font=("Courier New", 11), fg="#ff9b05", bg="black", borderwidth=0,
                             highlightthickness=0)
        title_text.tag_configure("link", foreground="blue", underline=False)
        title_text.insert(tk.END, "(V 1.0) by mdrahman04", "link")

        title_text.tag_bind("link", "<Button-1>", open_link)
        title_text.pack(pady=(30, 20), padx=100, expand=True, fill="both", anchor="center")

    def start_game(self):
        self.root.destroy()
        game_gui = GUI()
        game_gui.run()

    def show_scoreboard(self):
        global scoreboard_window_open

        if not scoreboard_window_open:
            scoreboard_window_open = True
            scoreboard_window = tk.Toplevel(self.root)
            scoreboard_window.title("Scoreboard")
            scoreboard_window.geometry("400x465")
            scoreboard_window.minsize(400, 465)
            scoreboard_window.configure(bg="black")

            title_label = tk.Label(scoreboard_window, text="Scoreboard", font=("Courier New", 24, "bold"), fg="white",
                                   bg="black")
            title_label.pack(pady=30)

            high_score_label = tk.Label(scoreboard_window, text="High Score: 0", font=("Courier New", 16), fg="red",
                                        bg="black")
            high_score_label.pack()

            scores_label = tk.Label(scoreboard_window, text="Latest Attempts:", font=("Courier New", 16), fg="white",
                                    bg="black")
            scores_label.pack(pady=10)

            scores = self.load_scores()
            if scores:
                for i, score in enumerate(scores):
                    if i < 10:
                        score_label = tk.Label(scoreboard_window, text=f"{i + 1}. {score}", font=("Courier New", 14),
                                               fg="yellow", bg="black")
                        score_label.pack()

            high_score = self.load_high_score()
            high_score_label.config(text=f"High Score: {high_score}")

            scoreboard_window.protocol("WM_DELETE_WINDOW", lambda: self.on_scoreboard_window_close(scoreboard_window))

    def on_scoreboard_window_close(self, window):
        global scoreboard_window_open
        scoreboard_window_open = False
        window.destroy()

    def load_scores(self):
        try:
            with open("scores.json", "r") as file:
                data = json.load(file)
                if "attempts" in data:
                    return data["attempts"]
        except FileNotFoundError:
            pass
        return []

    def load_high_score(self):
        try:
            with open("scores.json", "r") as file:
                data = json.load(file)
                if "high_score" in data:
                    return data["high_score"]
        except FileNotFoundError:
            pass
        return 0


if __name__ == "__main__":
    root = tk.Tk()
    start_page = StartPage(root)
    root.mainloop()
