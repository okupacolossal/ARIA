
import random

class Cell:
    def __init__(self, x, y, i, j, color=(60, 60, 60)):
        self.x = x
        self.y = y
        self.i = i
        self.j = j
        self.color = color
        self.passable = True


class Road:
    def __init__(self, cell1, cell2, width=1):
        self.cell1 = cell1
        self.cell2 = cell2
        self.width = width
        self.color = (60, 60, 60)

class Building:
    def __init__(self, grid):

        self.width = random.randint(2, 8)
        self.height = random.randint(2, 4)
        self.location = (random.randint(0, grid.width - self.width), random.randint(0, grid.height - self.height))
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

        self.top_left_cell = grid.cells[self.location[0]][self.location[1]]
        self.bottom_right_cell = grid.cells[self.location[0] + self.width - 1][self.location[1] + self.height - 1]
        self.top_right_cell = grid.cells[self.location[0] + self.width - 1][self.location[1]]
        self.bottom_left_cell = grid.cells[self.location[0]][self.location[1] + self.height - 1]

        self.top_left_cell.color = self.color

        possible_cells = [grid.cells[self.location[0] + i][self.location[1] + j] for i in range(self.width) for j in range(self.height)]

        for cell in possible_cells:
            if not cell.passable:
                return

        for i in range(self.width):
            for j in range(self.height):
                cell = grid.cells[self.location[0] + i][self.location[1] + j]
                cell.color = self.color
                cell.passable = False

        # top side loop
        for i in range(self.location[0], self.location[0] + self.width):

            if i + 1 < grid.width and not grid.cells[i + 1][self.location[1]].passable:
                road = grid.roads[((i, self.location[1]), (i + 1, self.location[1]))]
                road.color = self.color
        
        for i in range(self.location[0], self.location[0] + self.width):
            if i + 1 < grid.width and not grid.cells[i + 1][self.location[1] + self.height - 1].passable:
                road = grid.roads[((i, self.location[1] + self.height - 1), (i + 1, self.location[1] + self.height - 1))]
                road.color = self.color
        
        for i in range(self.location[1], self.location[1] + self.height):
            if i + 1 < grid.height and not grid.cells[self.location[0]][i + 1].passable:
                road = grid.roads[((self.location[0], i), (self.location[0], i + 1))]
                road.color = self.color

        for i in range(self.location[1], self.location[1] + self.height):
            if i + 1 < grid.height and not grid.cells[self.location[0] + self.width - 1][i + 1].passable:
                road = grid.roads[((self.location[0] + self.width - 1, i), (self.location[0] + self.width - 1, i + 1))]
                road.color = self.color


        
class Grid:
    def __init__(self, width, height, grid_pixel_width, grid_pixel_height, screen_width, screen_height, n_blocks):

        self.width = width
        self.height = height

        self.cells = [[None for _ in range(height)] for _ in range(width)]
        self.roads = {}
        self.cell_size = grid_pixel_width // width
        self.cell_radius = 2
        self.cell_offset = self.cell_radius // 2

        self.offset_x = (screen_width - grid_pixel_width) // 2
        self.offset_y = (screen_height - grid_pixel_height) // 2

        self.initialized = False

        self.number_blocks = n_blocks
        self.buildings = []

    def initialize(self):
        """Generator that builds the grid one step at a time for visualization."""
        for i in range(self.width):
            for j in range(self.height):
                x = self.offset_x + self.cell_size * i + self.cell_offset
                y = self.offset_y + self.cell_size * j + self.cell_offset
                self.cells[i][j] = Cell(x=x, y=y, i=i, j=j)
                yield

        for i in range(self.width):
            for j in range(self.height):
                if i + 1 < self.width:
                    self.roads[((i, j), (i + 1, j))] = Road(cell1=self.cells[i][j], cell2=self.cells[i + 1][j])
                    yield
                if j + 1 < self.height:
                    self.roads[((i, j), (i, j + 1))] = Road(cell1=self.cells[i][j], cell2=self.cells[i][j + 1])
                    yield

        self.initialized = True

        self.generate_buildings()
            
    def generate_buildings(self):
        for _ in range(self.number_blocks):
            building = Building(self)
            self.buildings.append(building)

    def clear_passages(self):

        init = (12, 12)
        end = (14, 14)

        for i in range(12, 15):
            for j in range(12, 15):
                self.cells[i][j].color = (255, 255, 255)
                self.cells[i][j].passable = True

    