import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

CELL_SIZE = 10
WIDTH = 190
HEIGHT = 95
MIN_ROOM_SIZE = 6
TIME_LIMIT = 60

WALL = 0
SPACE = 1

class MazeGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабиринт")
        self.setFixedSize(WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE + 40)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.maze = []
        self.player_x = 0
        self.player_y = 0
        self.end = (0, 0)

        self.time_left = TIME_LIMIT
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.timer_label = QLabel(self)
        self.timer_label.setGeometry(10, HEIGHT * CELL_SIZE + 5, 200, 30)
        self.timer_label.setStyleSheet("font-size: 16px;")

        self.restart_button = QPushButton("Перегенерировать", self)
        self.restart_button.setGeometry(WIDTH * CELL_SIZE - 160, HEIGHT * CELL_SIZE + 5, 150, 30)
        self.restart_button.clicked.connect(self.generate_maze)

        self.generate_maze()

    def generate_maze(self):
        self.maze = [[WALL for _ in range(WIDTH)] for _ in range(HEIGHT)]

        class Node:
            def __init__(self, x, y, w, h, maze):
                self.x, self.y = x, y
                self.w, self.h = w, h
                self.maze = maze
                self.left = None
                self.right = None

            def split(self):
                if self.left or self.right:
                    return False
                split_h = random.choice([True, False])
                if split_h and self.h >= MIN_ROOM_SIZE * 2 :
                    split = random.randint(MIN_ROOM_SIZE, self.h - MIN_ROOM_SIZE)
                    self.left = Node(self.x, self.y, self.w, split, self.maze)
                    self.right = Node(self.x, self.y + split, self.w, self.h - split, self.maze)
                    return True
                elif not split_h and self.w >= MIN_ROOM_SIZE * 2 :
                    split = random.randint(MIN_ROOM_SIZE, self.w - MIN_ROOM_SIZE)
                    self.left = Node(self.x, self.y, split, self.h, self.maze)
                    self.right = Node(self.x + split, self.y, self.w - split, self.h, self.maze)
                    return True
                return False

            def create_rooms(self):
                if self.left or self.right:
                    if self.left:
                        self.left.create_rooms()
                    if self.right:
                        self.right.create_rooms()
                    if self.left and self.right:
                        #connect(self.left.get_center(), self.right.get_center())
                        connect(self.left.get_random_point(), self.right.get_random_point())

                else:
                    x1, y1 = self.x + 1, self.y + 1
                    x2, y2 = self.x + self.w - 2 , self.y + self.h - 2
                    for y in range(y1, y2 + 1):
                        for x in range(x1, x2 + 1):
                            self.maze[y][x] = SPACE

            def get_random_point(self):
                x = random.randint(self.x + 1, self.x + self.w - 2)
                y = random.randint(self.y + 1, self.y + self.h - 2)
                return (x, y)

        def connect(a, b):
            # Добавляем 1–3 случайных перехода между областями
            count = random.randint(1, 1)
            for _ in range(count):
                x1, y1 = a
                x2, y2 = b

                if random.choice([True, False]):
                    cx = random.randint(min(x1, x2), max(x1, x2))
                    for x in range(min(x1, x2), max(x1, x2) + 1):
                        self.maze[y1][x] = SPACE
                    for y in range(min(y1, y2), max(y1, y2) + 1):
                        self.maze[y][x2] = SPACE
                else:
                    cy = random.randint(min(y1, y2), max(y1, y2))
                    for y in range(min(y1, y2), max(y1, y2) + 1):
                        self.maze[y][x1] = SPACE
                    for x in range(min(x1, x2), max(x1, x2) + 1):
                        self.maze[y2][x] = SPACE

        def split_all(node, depth):
            if depth <= 0:
                return
            if node.split():
                split_all(node.left, depth - 1)
                split_all(node.right, depth - 1)

        root = Node(0, 0, WIDTH, HEIGHT, self.maze)
        split_all(root, 1000)
        root.create_rooms()

        self.player_x, self.player_y = 1, 1
        while self.maze[self.player_y][self.player_x] != SPACE:
            self.player_x += 1
            self.player_y += 1

        self.end = (WIDTH - 2, HEIGHT - 2)
        while self.maze[self.end[1]][self.end[0]] != SPACE:
            self.end = (self.end[0] - 1, self.end[1] - 1)

        self.time_left = TIME_LIMIT
        self.timer.start(1000)
        self.update_timer()
        self.update()

    def update_timer(self):
        self.time_left -= 1
        self.timer_label.setText(f"Осталось времени: {self.time_left} сек.")
        if self.time_left <= 0:
            self.timer.stop()
            self.show_message("Время вышло! Попробуйте снова.")

    def keyPressEvent(self, event):
        key = event.key()
        dx, dy = 0, 0
        if key in (Qt.Key_W, Qt.Key_Up): dy = -1
        elif key in (Qt.Key_S, Qt.Key_Down): dy = 1
        elif key in (Qt.Key_A, Qt.Key_Left): dx = -1
        elif key in (Qt.Key_D, Qt.Key_Right): dx = 1

        nx = self.player_x + dx
        ny = self.player_y + dy

        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
            if self.maze[ny][nx] == SPACE:
                self.player_x = nx
                self.player_y = ny
                self.update()

        if (self.player_x, self.player_y) == self.end:
            self.timer.stop()
            self.show_message("Поздравляем! Вы прошли лабиринт.")

    def show_message(self, text):
        msg = QMessageBox(self)
        msg.setWindowTitle("Результат")
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        self.generate_maze()

    def paintEvent(self, event):
        painter = QPainter(self)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                color = QColor(30, 30, 30) if self.maze[y][x] == WALL else QColor(220, 220, 220)
                painter.setBrush(color)
                painter.drawRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        # Цель
        painter.setBrush(QColor(200, 0, 0))
        painter.drawRect(self.end[0] * CELL_SIZE, self.end[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        # Игрок
        painter.setBrush(QColor(0, 200, 0))
        painter.drawRect(self.player_x * CELL_SIZE, self.player_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

# Запуск
if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = MazeGame()
    game.show()
    sys.exit(app.exec_())
