'''
Description: Breadth-first-search pathfinding visualizer written in Python
AuthorName: Christian Aiello
Date Created: May 3 2022
Last Modified: December 11 2022
'''
import pygame, random
from pygame.locals import *
from math import sin, pi, sqrt

# rgb
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
OLIVE = (119, 149, 86)
GREY = (180, 180, 180)
ANTIQUE_WHITE = (235, 236, 208)

# constants
H_SQUARES = 20
W_SQUARES = 20
HEIGHT = H_SQUARES * 32
WIDTH = W_SQUARES * 32
SQUARE_SIZE = WIDTH // W_SQUARES
FPS = 60
# initialize pygame and display
pygame.init()
DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pathfinding Visualizer")


class Graph:
    def __init__(self):
        self.matrix = [[Node() for _ in range(W_SQUARES)] for _ in range(H_SQUARES)]
        self.start = (0, 0)
        self.end = (H_SQUARES - 1, W_SQUARES - 1)
        self.matrix[0][0] = Node("s")
        self.matrix[H_SQUARES - 1][W_SQUARES - 1] = Node("e")
        self.current = None
        self.visited = set()
        self.queue = []
        self.searching = False
        self.found = False
        self.path = []
        self.path_matrix = [
            [Node() for _ in range(W_SQUARES)] for _ in range(H_SQUARES)
        ]
        self.maze = []

    def display(self, display):
        display.fill(WHITE)
        for i, row in enumerate(self.matrix):
            for j, col in enumerate(row):
                pygame.draw.line(
                    display,
                    BLACK,
                    (j * SQUARE_SIZE, i * SQUARE_SIZE),
                    (j * SQUARE_SIZE, i * SQUARE_SIZE + SQUARE_SIZE - 1),
                )

                pygame.draw.line(
                    display,
                    BLACK,
                    (j * SQUARE_SIZE + SQUARE_SIZE - 1, i * SQUARE_SIZE),
                    (
                        j * SQUARE_SIZE + SQUARE_SIZE - 1,
                        i * SQUARE_SIZE + SQUARE_SIZE - 1,
                    ),
                )

                pygame.draw.line(
                    display,
                    BLACK,
                    (j * SQUARE_SIZE, i * SQUARE_SIZE),
                    (j * SQUARE_SIZE + SQUARE_SIZE - 1, i * SQUARE_SIZE),
                )

                pygame.draw.line(
                    display,
                    BLACK,
                    (j * SQUARE_SIZE, i * SQUARE_SIZE + SQUARE_SIZE - 1),
                    (
                        j * SQUARE_SIZE + SQUARE_SIZE - 1,
                        i * SQUARE_SIZE + SQUARE_SIZE - 1,
                    ),
                )

                if col.val == 1:
                    sprite = pygame.image.load(f"assets/wall.png")
                elif col.val == "e":
                    sprite = pygame.image.load(f"assets/end.png")
                elif col.val == "s":
                    sprite = pygame.image.load(f"assets/start.png")

                if (i, j) in self.visited:
                    display.blit(
                        pygame.image.load(f"assets/visited.png"),
                        (j * SQUARE_SIZE + 1, i * SQUARE_SIZE + 1),
                    )
                else:
                    display.blit(
                        pygame.image.load(f"assets/floor.png"),
                        (j * SQUARE_SIZE + 1, i * SQUARE_SIZE + 1),
                    )

                if col.val == 1:
                    sprite = pygame.image.load(f"assets/wall.png")
                    if not col.new:
                        display.blit(sprite, (j * SQUARE_SIZE + 1, i * SQUARE_SIZE + 1))
                if col.val == "s":
                    if not (self.current == self.start):
                        display.blit(sprite, (j * SQUARE_SIZE + 1, i * SQUARE_SIZE + 1))
                elif col.val == "e":
                    if not (self.current == self.end):
                        display.blit(sprite, (j * SQUARE_SIZE + 1, i * SQUARE_SIZE + 1))

        for i, row in enumerate(self.matrix):
            for j, col in enumerate(row):
                if col.val == 1:
                    sprite = pygame.image.load(f"assets/wall.png")
                    if col.new:
                        sprite = pygame.transform.scale(
                            sprite,
                            (
                                (16 + (16 * sqrt(2)) * sin(col.x)),
                                (16 + (16 * sqrt(2)) * sin(col.x)),
                            ),
                        )
                        display.blit(
                            sprite,
                            (
                                j * SQUARE_SIZE
                                + (SQUARE_SIZE - (16 + 24 * sin(col.x))) // 2,
                                i * SQUARE_SIZE
                                + (SQUARE_SIZE - (16 + 24 * sin(col.x))) // 2,
                            ),
                        )
                        if round(col.x, 3) == round(3 * pi / 4, 3):
                            col.new = False
                            col.x = 0
                        else:
                            col.x += pi / 8

        for i, row in enumerate(self.path_matrix):
            for j, col in enumerate(row):
                if col.val == 1:
                    sprite = pygame.image.load(f"assets/path.png")
                    if col.new:
                        sprite = pygame.transform.scale(
                            sprite,
                            (
                                (16 + (16 * sqrt(2)) * sin(col.x)),
                                (16 + (16 * sqrt(2)) * sin(col.x)),
                            ),
                        )
                        display.blit(
                            sprite,
                            (
                                j * SQUARE_SIZE
                                + (SQUARE_SIZE - (16 + 24 * sin(col.x))) // 2,
                                i * SQUARE_SIZE
                                + (SQUARE_SIZE - (16 + 24 * sin(col.x))) // 2,
                            ),
                        )
                        if round(col.x, 3) == round(3 * pi / 4, 3):
                            col.new = False
                            col.x = 0
                        else:
                            col.x += pi / 8
                    elif not col.new and (i, j) not in self.path:
                        display.blit(sprite, (j * SQUARE_SIZE + 1, i * SQUARE_SIZE + 1))
                    if (i, j) == self.start:
                        sprite = pygame.image.load(f"assets/start.png")
                        if not (self.current == self.start):
                            display.blit(
                                sprite, (j * SQUARE_SIZE + 1, i * SQUARE_SIZE + 1)
                            )
                    elif (i, j) == self.end:
                        sprite = pygame.image.load(f"assets/end.png")
                        if not (self.current == self.end):
                            display.blit(
                                sprite, (j * SQUARE_SIZE + 1, i * SQUARE_SIZE + 1)
                            )

        if self.current == self.start:
            pos = pygame.mouse.get_pos()
            pos = (pos[0] - SQUARE_SIZE // 2, pos[1] - SQUARE_SIZE // 2)
            display.blit(pygame.image.load(f"assets/start.png"), pos)
        elif self.current == self.end:
            pos = pygame.mouse.get_pos()
            pos = (pos[0] - SQUARE_SIZE // 2, pos[1] - SQUARE_SIZE // 2)
            display.blit(pygame.image.load(f"assets/end.png"), pos)

    def recursive_division(self, start_x, end_x, start_y, end_y, root=False):
        if root:
            self.maze = []
            self.matrix = [[Node() for _ in range(W_SQUARES)] for _ in range(H_SQUARES)]
            self.start = (0, 0)
            self.end = (H_SQUARES - 1, W_SQUARES - 1)
            self.matrix[0][0] = Node("s")
            self.matrix[H_SQUARES - 1][W_SQUARES - 1] = Node("e")

        length_x = end_x - start_x
        length_y = end_y - start_y
        x_midpoint = (start_x + end_x) // 2
        y_midpoint = (start_y + end_y) // 2

        if length_x > 0 and length_y > 0:
            if length_x >= length_y and length_x > 2:
                all_open_y = list(set(range(start_y, end_y)) - {y_midpoint})
                if all_open_y != []:
                    open_y = random.choice(all_open_y)
                else:
                    return

                valid = True
                if start_y - 1 in range(H_SQUARES):
                    if (start_y - 1, x_midpoint) not in self.maze:
                        valid = False
                if end_y in range(H_SQUARES):
                    if (end_y, x_midpoint) not in self.maze:
                        valid = False

                if valid:
                    for y in range(start_y, end_y):
                        if y != open_y and self.matrix[y][x_midpoint].val not in (
                            "s",
                            "e",
                        ):
                            self.maze.append((y, x_midpoint))

                    self.recursive_division(start_x, x_midpoint, start_y, end_y)
                    self.recursive_division(x_midpoint + 1, end_x, start_y, end_y)
            elif length_y > length_x and length_y > 2:
                all_open_x = list(set(range(start_x, end_x)) - {x_midpoint})
                if all_open_x != []:
                    open_x = random.choice(all_open_x)
                else:
                    return

                valid = True
                if start_x - 1 in range(W_SQUARES):
                    if (y_midpoint, start_x - 1) not in self.maze:
                        valid = False
                if end_x in range(W_SQUARES):
                    if (y_midpoint, end_x) not in self.maze:
                        valid = False

                if valid:
                    for x in range(start_x, end_x):
                        if x != open_x and self.matrix[y_midpoint][x].val not in (
                            "s",
                            "e",
                        ):
                            self.maze.append((y_midpoint, x))

                    self.recursive_division(start_x, end_x, start_y, y_midpoint)
                    self.recursive_division(start_x, end_x, y_midpoint + 1, end_y)

    def bfs(self):
        steps = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        visited = self.visited
        queue = self.queue

        if self.start not in visited:
            visited.add(self.start)
        if [self.start] not in queue:
            queue.append([self.start])

        while queue:
            path = queue.pop(0)
            s = path[-1]

            if self.matrix[s[0]][s[1]].val == "e":
                self.found = True
                return path

            for step in steps:
                neighbour = (s[0] + step[0], s[1] + step[1])
                if (
                    neighbour[0] in range(H_SQUARES)
                    and neighbour[1] in range(W_SQUARES)
                    and self.matrix[neighbour[0]][neighbour[1]].val != 1
                    and neighbour not in visited
                ):
                    new_path = list(path)
                    new_path.append(neighbour)
                    visited.add(neighbour)
                    queue.append(new_path)
            return None

        self.visited = set()


class Node:
    def __init__(self, val=0, new=False):
        self.val = val
        self.new = new
        self.x = 0


graph = Graph()


def main():
    start_end_node = False
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            if (
                pygame.mouse.get_pressed()[0]
                and (not graph.searching)
                and (not graph.found)
                and graph.maze == []
            ):
                mouse_pos = pygame.mouse.get_pos()
                col = mouse_pos[0] // SQUARE_SIZE
                row = mouse_pos[1] // SQUARE_SIZE
                if not start_end_node:
                    if (row, col) == graph.current:
                        break
                    graph.current = (row, col)

                    if row in range(H_SQUARES) and col in range(W_SQUARES):
                        if (
                            graph.matrix[row][col].val == 0
                            or graph.matrix[row][col].val == 1
                        ):
                            graph.matrix[row][col].val = 1 - graph.matrix[row][col].val
                            if graph.matrix[row][col].val == 1:
                                graph.matrix[row][col].new = True
                        else:
                            start_end_node = True

            if event.type == MOUSEBUTTONDOWN:
                if graph.found and graph.path == [] and graph.maze == []:
                    graph.searching = False
                    graph.queue = []
                    graph.visited = set()
                    graph.found = False
                    graph.path_matrix = [
                        [Node() for _ in range(W_SQUARES)] for _ in range(H_SQUARES)
                    ]
            if event.type == MOUSEBUTTONUP:
                if graph.current == graph.start:
                    mouse_pos = pygame.mouse.get_pos()
                    col = mouse_pos[0] // SQUARE_SIZE
                    row = mouse_pos[1] // SQUARE_SIZE

                    if graph.matrix[row][col].val == 0:
                        (
                            graph.matrix[graph.start[0]][graph.start[1]].val,
                            graph.matrix[row][col].val,
                        ) = (0, "s")
                        graph.start = (row, col)
                elif graph.current == graph.end:
                    mouse_pos = pygame.mouse.get_pos()
                    col = mouse_pos[0] // SQUARE_SIZE
                    row = mouse_pos[1] // SQUARE_SIZE

                    if graph.matrix[row][col].val == 0:
                        (
                            graph.matrix[graph.end[0]][graph.end[1]].val,
                            graph.matrix[row][col].val,
                        ) = (0, "e")
                        graph.end = (row, col)

                graph.current = None
                start_end_node = False

            if event.type == KEYDOWN:
                if event.key == pygame.K_SPACE and graph.maze == []:
                    graph.searching = not graph.searching
                    if graph.searching == False or graph.found:
                        graph.queue = []
                        graph.visited = set()
                        graph.found = False
                        graph.path_matrix = [
                            [Node() for _ in range(W_SQUARES)] for _ in range(H_SQUARES)
                        ]
                        graph.searching = False
                if event.key == pygame.K_g:
                    if not graph.searching and not graph.found:
                        graph.recursive_division(0, W_SQUARES, 0, H_SQUARES, root=True)

        if graph.searching:
            if not graph.found:
                for _ in range(5):
                    path = graph.bfs()
                    if path:
                        graph.path = path
                        for (i, j) in path:
                            graph.path_matrix[i][j].val = 1
                        break
            if graph.found or graph.queue == []:
                graph.found = True
                for i in range(1):
                    if graph.path != []:
                        (i, j) = graph.path.pop(0)
                        graph.path_matrix[i][j].new = True
                    else:
                        graph.searching = False

        if graph.maze != []:
            (i, j) = graph.maze.pop(0)
            graph.matrix[i][j].val = 1
            graph.matrix[i][j].new = True

        graph.display(DISPLAY)
        pygame.display.update()

    pygame.quit()


main()
