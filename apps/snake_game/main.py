import tkinter as tk
import random

class SnakeGameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Snake Game")
        self.resizable(False, False)
        
        # Game Constants
        self.GAME_WIDTH = 600
        self.GAME_HEIGHT = 600
        self.SPEED = 100
        self.SPACE_SIZE = 25
        self.BODY_PARTS = 3
        self.SNAKE_COLOR = "#00FF00"
        self.FOOD_COLOR = "#FF0000"
        self.BACKGROUND_COLOR = "#000000"

        # Game State
        self.score = 0
        self.direction = 'down'
        self.snake = []
        self.food = None
        
        self.create_widgets()
        self.center_window()
        self.bind_keys()
        self.start_game()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        # Score Label
        self.label = tk.Label(self, text="Score: 0", font=('consolas', 20),
                              bg=self.BACKGROUND_COLOR, fg="white")
        self.label.pack(fill="x")

        # Game Canvas
        self.canvas = tk.Canvas(self, bg=self.BACKGROUND_COLOR, 
                                height=self.GAME_HEIGHT, width=self.GAME_WIDTH,
                                highlightthickness=0)
        self.canvas.pack()

    def bind_keys(self):
        self.bind('<Left>', lambda event: self.change_direction('left'))
        self.bind('<Right>', lambda event: self.change_direction('right'))
        self.bind('<Up>', lambda event: self.change_direction('up'))
        self.bind('<Down>', lambda event: self.change_direction('down'))
        self.bind('<space>', self.restart_game)

    def start_game(self):
        # Reset State
        self.score = 0
        self.direction = 'down'
        self.label.config(text=f"Score: {self.score}")
        self.canvas.delete("all")
        
        # Create initial snake
        self.snake = []
        for i in range(self.BODY_PARTS):
            self.snake.append([0, 0]) # Start at top-left, collapsed or spread out ideally
                                      # Let's clean coordinates
        # Actually proper init positions
        start_x = 0
        start_y = 0
        self.snake = [[start_x, start_y] for _ in range(self.BODY_PARTS)] # Actually they all overlap at start, will fix in first move or better set distinct

        self.spawn_food()
        self.next_turn()

    def spawn_food(self):
        x = random.randint(0, int(self.GAME_WIDTH / self.SPACE_SIZE) - 1) * self.SPACE_SIZE
        y = random.randint(0, int(self.GAME_HEIGHT / self.SPACE_SIZE) - 1) * self.SPACE_SIZE
        self.food = [x, y]
        
        self.canvas.create_oval(x, y, x + self.SPACE_SIZE, y + self.SPACE_SIZE, 
                                fill=self.FOOD_COLOR, tag="food")

    def next_turn(self):
        x, y = self.snake[0]

        if self.direction == 'up':
            y -= self.SPACE_SIZE
        elif self.direction == 'down':
            y += self.SPACE_SIZE
        elif self.direction == 'left':
            x -= self.SPACE_SIZE
        elif self.direction == 'right':
            x += self.SPACE_SIZE

        # Insert new head
        self.snake.insert(0, [x, y])

        # Check collision with food
        if x == self.food[0] and y == self.food[1]:
            self.score += 1
            self.label.config(text=f"Score: {self.score}")
            self.canvas.delete("food")
            self.spawn_food()
        else:
            # Remove tail if no food eaten
            del self.snake[-1]

        # Check Collisions
        if self.check_collisions():
            self.game_over()
        else:
            self.draw_snake()
            self.after(self.SPEED, self.next_turn)

    def draw_snake(self):
        self.canvas.delete("snake")
        for i, (x, y) in enumerate(self.snake):
            color = self.SNAKE_COLOR
            # Simple head distinction (optional)
            if i == 0: color = "#55FF55" # Lighter green for head
            
            self.canvas.create_rectangle(x, y, x + self.SPACE_SIZE, y + self.SPACE_SIZE, 
                                         fill=color, tag="snake")

    def change_direction(self, new_direction):
        if new_direction == 'left':
            if self.direction != 'right':
                self.direction = new_direction
        elif new_direction == 'right':
            if self.direction != 'left':
                self.direction = new_direction
        elif new_direction == 'up':
            if self.direction != 'down':
                self.direction = new_direction
        elif new_direction == 'down':
            if self.direction != 'up':
                self.direction = new_direction

    def check_collisions(self):
        head_x, head_y = self.snake[0]

        # Wall collision
        if head_x < 0 or head_x >= self.GAME_WIDTH:
            return True
        if head_y < 0 or head_y >= self.GAME_HEIGHT:
            return True

        # Tail collision
        for body_part in self.snake[1:]:
            if head_x == body_part[0] and head_y == body_part[1]:
                return True

        return False

    def game_over(self):
        self.canvas.delete("all")
        self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2,
                                text=f"GAME OVER\nScore: {self.score}\nPress [Space] to Restart", 
                                font=('consolas', 30), fill="red", justify="center")

    def restart_game(self, event=None):
        if hasattr(self, 'game_over_state') and not self.game_over_state: return 
        # Actually checking if game is running is cleaner, but simple restart logic:
        # Just calling start_game resets everything.
        # To avoid duplicated loops if accidental press, we can check a flag.
        # But `next_turn` stops calling itself on collision.
        self.start_game()

if __name__ == "__main__":
    app = SnakeGameApp()
    app.mainloop()
