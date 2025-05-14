import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont


class MazeGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабиринт")
        self.setFixedSize(800, 600)
        self.maze_size = 15  # Размер лабиринта (15х15)
        self.cell_size = 30  # Размер клетки в пикселях
        self.time_limit = 180  # Лимит времени (3 минуты)
        self.current_time = 0
        self.player_pos = [1, 1]
        self.exit_pos = [self.maze_size - 2, self.maze_size - 2]
        self.maze = self.generate_maze()

        # UI Elements
        self.timer_label = QLabel(self)
        self.timer_label.setGeometry(10, 10, 200, 30)
        self.timer_label.setFont(QFont("Arial", 12))

        self.restart_button = QPushButton("Новый лабиринт", self)
        self.restart_button.setGeometry(600, 10, 150, 30)
        self.restart_button.clicked.connect(self.restart_game)

        # Game Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # 1 секунда

        self.update_timer()

    def generate_maze(self):
        """Генерация лабиринта алгоритмом BSP (без numpy)"""
        maze = [[0 for _ in range(self.maze_size)] for _ in range(self.maze_size)]

        # Создаем границы
        for i in range(self.maze_size):
            maze[0][i] = maze[-1][i] = 1
            maze[i][0] = maze[i][-1] = 1

        # Рекурсивное разделение пространства
        self.bsp_split(maze, 1, 1, self.maze_size - 2, self.maze_size - 2)

        # Добавляем вход и выход
        maze[1][1] = 0  # Старт
        maze[self.maze_size - 2][self.maze_size - 2] = 2  # Выход
        return maze

    def bsp_split(self, maze, x1, y1, x2, y2):
        """Рекурсивное разделение пространства для BSP"""
        if x2 - x1 < 1.1 or y2 - y1 < 1.1:
            return

        # Вертикальное или горизонтальное разделение
        if random.choice([True, False]):
            # Вертикальная стена
            wall_x = random.randint(x1 + 1, x2 - 1)
            for y in range(y1, y2 + 1):
                maze[y][wall_x] = 1
            # Оставляем проход
            passage_y = random.randint(y1, y2)
            maze[passage_y][wall_x] = 0
            # Рекурсия для левой и правой частей
            self.bsp_split(maze, x1, y1, wall_x - 1, y2)
            self.bsp_split(maze, wall_x + 1, y1, x2, y2)
        else:
            # Горизонтальная стена
            wall_y = random.randint(y1 + 1, y2 - 1)
            for x in range(x1, x2 + 1):
                maze[wall_y][x] = 1
            # Оставляем проход
            passage_x = random.randint(x1, x2)
            maze[wall_y][passage_x] = 0
            # Рекурсия для верхней и нижней частей
            self.bsp_split(maze, x1, y1, x2, wall_y - 1)
            self.bsp_split(maze, x1, wall_y + 1, x2, y2)

    def paintEvent(self, event):
        """Отрисовка лабиринта и персонажа"""
        painter = QPainter(self)
        painter.setPen(Qt.black)

        # Рисуем лабиринт
        for y in range(self.maze_size):
            for x in range(self.maze_size):
                rect = (x * self.cell_size + 100, y * self.cell_size + 100,
                        self.cell_size, self.cell_size)
                if self.maze[y][x] == 1:  # Стена
                    painter.setBrush(QColor(70, 70, 70))
                    painter.drawRect(*rect)
                elif self.maze[y][x] == 2:  # Выход
                    painter.setBrush(QColor(0, 200, 0))
                    painter.drawRect(*rect)

        # Рисуем игрока
        painter.setBrush(QColor(200, 0, 0))
        player_rect = (self.player_pos[0] * self.cell_size + 100,
                       self.player_pos[1] * self.cell_size + 100,
                       self.cell_size, self.cell_size)
        painter.drawEllipse(*player_rect)

    def keyPressEvent(self, event):
        """Обработка клавиш управления"""
        key = event.key()
        new_pos = self.player_pos.copy()

        if key in (Qt.Key_W, Qt.Key_Up):
            new_pos[1] -= 1
        elif key in (Qt.Key_S, Qt.Key_Down):
            new_pos[1] += 1
        elif key in (Qt.Key_A, Qt.Key_Left):
            new_pos[0] -= 1
        elif key in (Qt.Key_D, Qt.Key_Right):
            new_pos[0] += 1
        else:
            return

        # Проверка на выход за границы и стены
        if (0 <= new_pos[0] < self.maze_size and
                0 <= new_pos[1] < self.maze_size and
                self.maze[new_pos[1]][new_pos[0]] != 1):
            self.player_pos = new_pos
            self.update()

            # Проверка на победу
            if self.player_pos == self.exit_pos:
                self.win_game()

    def update_timer(self):
        """Обновление таймера"""
        self.current_time += 1
        mins, secs = divmod(self.time_limit - self.current_time, 60)
        self.timer_label.setText(f"Время: {mins:02d}:{secs:02d}")

        # Проверка на проигрыш по времени
        if self.current_time >= self.time_limit:
            self.timer.stop()
            QMessageBox.information(self, "Поражение", "Время вышло!")
            self.restart_game()

    def win_game(self):
        """Обработка победы"""
        self.timer.stop()
        QMessageBox.information(self, "Победа!",
                                f"Вы прошли лабиринт за {self.current_time} секунд!")
        self.restart_game()

    def restart_game(self):
        """Перезапуск игры"""
        self.current_time = 0
        self.player_pos = [1, 1]
        self.maze = self.generate_maze()
        self.timer.start(1000)
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = MazeGame()
    game.show()
    sys.exit(app.exec_())