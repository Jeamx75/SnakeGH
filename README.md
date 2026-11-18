# 🐍 SnakeGH

**SnakeGH** is a feature-rich, classic arcade-style Snake game built entirely in Python using **Tkinter**. It features custom pixel-art snake sprites with directional rotation, a gold bonus fruit mechanic, progressive difficulty scaling, high score persistence, and a clean retro dark-mode interface.

---

## 🕹️ Features

* **Custom Pixel-Art Snake Head:** Tailored 24×24 pixel art sprite that dynamically rotates depending on movement direction (Up, Down, Left, Right) complete with animated eyes and forked tongue.
* **Progressive Difficulty:** The game speeds up as your score increases, scaling up every level.
* **Gold Bonus Fruit:** Spawns periodically, worth 3 points, with a visual blinking warning before it expires.
* **Persistent High Scores:** Automatically saves your best score locally (`snake_highscore.txt`) across gaming sessions.
* **Pause & Resume:** Full support for pausing the game mid-action without losing your momentum.
* **Zero External Dependencies:** Built strictly using Python's standard library and Tkinter—no extra installation packages required!

---

## 🎮 Controls

| Key / Control | Action |
| :--- | :--- |
| **Arrow Keys** or **W, A, S, D** | Move Snake (Up, Left, Down, Right) |
| **Spacebar** | Start Game / Play Again |
| **P** | Pause / Resume Game |

---

## 🚀 Getting Started

### Prerequisites
* Python 3.x installed on your system.

### Running the Game
1. Clone or download this repository.
2. Open your terminal or command prompt in the project directory.
3. Run the script:
   ```bash
   python snakegh.py
