import tkinter as tk
import math
import random
import json
import os


class Game:
    def __init__(self):
        self.pattern = []
        self.pattern_index = 0
        self.user_pattern = []
        self.score = 0
        self.round = 1
        self.game_over_flag = False
        self.attempts = []
        self.load_scores()

    def load_scores(self):
        try:
            with open("scores.json", "r") as file:
                data = json.load(file)
                self.high_score = data["high_score"]
                if "attempts" in data:
                    self.attempts = data["attempts"]
        except FileNotFoundError:
            self.high_score = 0
            self.attempts = []

    def save_scores(self):
        data = {
            "high_score": self.high_score,
            "attempts": self.attempts
        }
        with open("scores.json", "w") as file:
            json.dump(data, file)

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_scores()

    def generate_pattern(self):
        colors = ["red", "blue", "green", "yellow"]
        self.pattern = [random.choice(colors) for _ in range(self.round)]
        self.pattern_index = 0

    def check_pattern(self, button_color):
        if not self.game_over_flag:
            if self.pattern_index < len(self.pattern) and self.pattern[self.pattern_index] == button_color:
                self.user_pattern.append(button_color)
                self.pattern_index += 1
                if self.pattern_index == len(self.pattern):
                    self.score += 1
                    self.pattern_index = 0
                    return True
            else:
                self.game_over()
        return False

    def game_over(self):
        self.game_over_flag = True
        self.user_pattern = []
        self.pattern = []
        self.pattern_index = 0
        self.attempts.insert(0, self.score)
        self.update_high_score()
        self.save_scores()


class Button:
    def __init__(self, color, canvas, angle, radius, game, gui):
        self.color = color
        self.game = game
        self.canvas = canvas
        self.angle = angle
        self.radius = radius
        self.gui = gui
        self.button = self.draw_button()
        self.flash_border = None
        self.flash_counter = 0
        self.enabled = True

    def draw_button(self):
        x = math.cos(math.radians(self.angle)) * self.radius
        y = math.sin(math.radians(self.angle)) * self.radius

        button = self.canvas.create_oval(
            200 + x - 40, 200 + y - 40, 200 + x + 40, 200 + y + 40,
            fill=self.color, outline="white", width=1, state=tk.NORMAL
        )

        border = self.canvas.create_oval(
            200 + x - 41, 200 + y - 41, 200 + x + 41, 200 + y + 41,
            outline="white", width=1, state=tk.HIDDEN
        )

        self.flash_border = border

        return button

    def flash(self):
        if self.flash_counter < len(self.game.pattern):
            self.canvas.itemconfig(self.flash_border, state=tk.NORMAL)
            self.canvas.itemconfig(self.button, outline="black", width=2, fill="white")
            self.canvas.update()
            self.canvas.after(400)
            self.canvas.itemconfig(self.flash_border, state=tk.HIDDEN)
            self.canvas.itemconfig(self.button, outline="white", width=1, fill=self.color)
            self.canvas.update()
            self.canvas.after(400)
            self.flash_counter += 1

    def reset_flash_counter(self):
        self.flash_counter = 0

    def is_inside_button(self, x, y):
        x1, y1, x2, y2 = self.canvas.coords(self.button)
        return x1 <= x <= x2 and y1 <= y <= y2

    def on_hover(self, event):
        self.canvas.itemconfig(self.button, outline="black", width=2)

    def on_leave(self, event):
        self.canvas.itemconfig(self.button, outline="white", width=1)

    def button_clicked(self, event):
        if self.gui.player_input_enabled and self.enabled:
            if self.is_inside_button(event.x, event.y):
                if not self.game.game_over_flag:
                    if self.color == self.game.pattern[self.game.pattern_index]:
                        if self.game.check_pattern(self.color):
                            if len(self.game.user_pattern) == len(self.game.pattern):
                                for button in self.gui.buttons:
                                    button.reset_flash_counter()
                                self.game.round += 1
                                self.gui.start_round()
                    else:
                        self.game.game_over()
                        self.gui.display_message("Game Over. Try again.")
                        self.gui.reset_game()
                        self.gui.player_input_enabled = False
                        self.enabled = False


class Scoreboard:
    def __init__(self, window, gui):
        self.gui = gui
        self.window = window
        self.score_label = tk.Label(window, text="SCORE: 0", font=("Courier New", 20, "bold"), fg="yellow", bg="black")
        self.score_label.pack(pady=10)

        self.high_score_label = tk.Label(window, text="High Score: 0", font=("Courier New", 16), fg="white", bg="black")
        self.high_score_label.pack(pady=5)

    def update_score(self):
        if self.gui.game is not None:
            self.score_label.config(text=f"SCORE: {self.gui.game.score}")

    def update_high_score(self):
        self.high_score_label.config(text=f"High Score: {self.gui.game.high_score}")


class GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Simon Game")
        self.window.geometry("600x630")
        self.window.configure(bg="black")
        self.window.minsize(500, 630)
        frame = tk.Frame(self.window)
        frame.pack(side=tk.TOP, pady=10)
        self.canvas = tk.Canvas(self.window, width=400, height=400, bg="black")
        self.canvas.pack()
        self.game = Game()
        self.scoreboard = Scoreboard(self.window, self)
        self.message_label = tk.Label(self.window, text="", pady=10, font=("Courier New", 14), fg="orange", bg="black")
        self.message_label.pack()
        self.buttons = []
        self.setup_buttons()
        self.setup_gui()
        self.scoreboard.update_high_score()
        self.player_input_enabled = False

        button_frame = tk.Frame(self.window, bg="black")
        button_frame.pack(pady=10)

        menu_button = tk.Button(button_frame, text="Menu", command=self.open_menu, font=("Arial", 16), fg="white", bg="blue")
        start_button = tk.Button(button_frame, text="Start Game", command=self.start_game, font=("Arial", 16), fg="white", bg="green")

        menu_button.pack(side=tk.LEFT, padx=10)
        start_button.pack(side=tk.LEFT, padx=10)

    def setup_buttons(self):
        for i, color in enumerate(["red", "blue", "green", "yellow"]):
            button = Button(color, self.canvas, i * 90, 80, self.game, self)
            self.canvas.tag_bind(button.button, "<Button-1>", button.button_clicked)
            self.canvas.tag_bind(button.button, "<Enter>", button.on_hover)
            self.canvas.tag_bind(button.button, "<Leave>", button.on_leave)
            self.buttons.append(button)

    def setup_gui(self):
        self.player_input_enabled = False

    def start_game(self):
        self.reset_game()
        self.start_round()
        self.scoreboard.update_high_score()

    def start_round(self):
        if not self.game.game_over_flag:
            self.game.generate_pattern()
            self.scoreboard.update_score()
            self.player_input_enabled = False
            self.play_pattern(self.game.pattern)
            self.game.game_over_flag = False
            self.game.user_pattern = []
            self.message_label.config(text="Repeat the shown pattern in order")

    def reset_game(self):
        self.game.game_over_flag = False
        self.game.score = 0
        self.game.round = 1
        for button in self.buttons:
            button.enabled = True

    def play_pattern(self, pattern):
        delay = 1000
        flash_duration = 800

        for button in self.buttons:
            self.canvas.itemconfig(button.button, state=tk.DISABLED)

        for color in pattern:
            for button in self.buttons:
                if button.color == color:
                    button.flash()
            delay += flash_duration + 200

        self.window.after(delay, self.reset_pattern_index)

        self.allow_player_input()

    def reset_pattern_index(self):
        if self.game is not None:
            self.game.pattern_index = 0

    def allow_player_input(self):
        self.player_input_enabled = True
        for button in self.buttons:
            self.canvas.itemconfig(button.button, state=tk.NORMAL)

    def display_message(self, message):
        self.message_label.config(text=message)

    def open_menu(self):
        self.window.destroy()
        os.system("python menu.py")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    game_gui = GUI()
    game_gui.run()
