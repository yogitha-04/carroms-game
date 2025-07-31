import tkinter as tk
import math
import random

# Constants
BOARD_SIZE = 600
POCKET_RADIUS = 25
COIN_RADIUS = 10
STRIKER_RADIUS = 15
FRICTION = 0.98

class Coin:
    def __init__(self, canvas, x, y, color, radius=COIN_RADIUS):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = radius
        self.color = color
        self.id = canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color
        )

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= FRICTION
        self.vy *= FRICTION
        self.canvas.coords(
            self.id,
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius
        )

    def is_moving(self):
        return abs(self.vx) > 0.1 or abs(self.vy) > 0.1

    def check_pocketed(self):
        pockets = [(0, 0), (BOARD_SIZE, 0), (0, BOARD_SIZE), (BOARD_SIZE, BOARD_SIZE)]
        for px, py in pockets:
            if math.hypot(self.x - px, self.y - py) < POCKET_RADIUS:
                self.canvas.delete(self.id)
                return True
        return False

class CarromGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Carrom Game")

        self.canvas = tk.Canvas(root, width=BOARD_SIZE, height=BOARD_SIZE, bg="burlywood")
        self.canvas.pack()

        self.score = 0
        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Arial", 14))
        self.score_label.pack()

        self.create_board()
        self.create_coins()
        self.create_striker()

        self.canvas.bind("<Button-1>", self.aim_striker)
        self.update_game()

    def create_board(self):
        # Draw border
        self.canvas.create_rectangle(0, 0, BOARD_SIZE, BOARD_SIZE, width=10)

        # Draw pockets
        r = POCKET_RADIUS
        self.canvas.create_oval(-r, -r, r, r, fill="black")
        self.canvas.create_oval(BOARD_SIZE - r, -r, BOARD_SIZE + r, r, fill="black")
        self.canvas.create_oval(-r, BOARD_SIZE - r, r, BOARD_SIZE + r, fill="black")
        self.canvas.create_oval(BOARD_SIZE - r, BOARD_SIZE - r, BOARD_SIZE + r, BOARD_SIZE + r, fill="black")

    def create_coins(self):
        self.coins = []
        colors = ["white", "white", "white", "black", "black", "black", "red"]
        positions = [(300, 300), (310, 310), (290, 290), (290, 310), (310, 290), (300, 310), (300, 290)]
        for (x, y), color in zip(positions, colors):
            self.coins.append(Coin(self.canvas, x, y, color))

    def create_striker(self):
        self.striker = Coin(self.canvas, BOARD_SIZE / 2, BOARD_SIZE - 40, "blue", radius=STRIKER_RADIUS)
        self.ready = True

    def aim_striker(self, event):
        if not self.ready:
            return

        dx = event.x - self.striker.x
        dy = event.y - self.striker.y
        dist = math.hypot(dx, dy)
        power = min(dist / 5, 15)

        angle = math.atan2(dy, dx)
        self.striker.vx = power * math.cos(angle)
        self.striker.vy = power * math.sin(angle)
        self.ready = False

    def update_game(self):
        all_coins = [self.striker] + self.coins

        for coin in all_coins:
            coin.move()

        # Collision detection (simplified)
        for i in range(len(all_coins)):
            for j in range(i + 1, len(all_coins)):
                self.handle_collision(all_coins[i], all_coins[j])

        # Check pocketing
        for coin in self.coins[:]:
            if coin.check_pocketed():
                self.coins.remove(coin)
                self.score += 10
                self.update_score()

        if self.striker.check_pocketed():
            self.score -= 5
            self.update_score()
            self.reset_striker()
        elif not self.striker.is_moving():
            self.ready = True

        self.root.after(20, self.update_game)

    def reset_striker(self):
        self.striker = Coin(self.canvas, BOARD_SIZE / 2, BOARD_SIZE - 40, "blue", radius=STRIKER_RADIUS)
        self.ready = True

    def handle_collision(self, c1, c2):
        dx = c1.x - c2.x
        dy = c1.y - c2.y
        dist = math.hypot(dx, dy)
        if dist < c1.radius + c2.radius and dist != 0:
            angle = math.atan2(dy, dx)
            total_vx = c1.vx - c2.vx
            total_vy = c1.vy - c2.vy
            dot = total_vx * math.cos(angle) + total_vy * math.sin(angle)

            if dot > 0:
                impulse = 0.5 * dot
                c1.vx -= impulse * math.cos(angle)
                c1.vy -= impulse * math.sin(angle)
                c2.vx += impulse * math.cos(angle)
                c2.vy += impulse * math.sin(angle)

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")

if __name__ == "__main__":
    root = tk.Tk()
    game = CarromGame(root)
    root.mainloop()
