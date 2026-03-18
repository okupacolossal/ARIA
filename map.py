import random


class Cell:
    def __init__(self, x, y, i, j, color=(60, 60, 60)):
        self.x = x
        self.y = y
        self.i = i
        self.j = j
        self.color = color
        self.passable = False


class Road:
    def __init__(self, cell1, cell2, width=1):
        self.cell1 = cell1
        self.cell2 = cell2
        self.width = width
        self.color = (60, 60, 60)


        
class Grid:
    def __init__(self, width, height, grid_pixel_width, grid_pixel_height, screen_width, screen_height):

        self.width = width 
        self.height = height

        self.cells = [[None for _ in range(height)] for _ in range(width)]
        self.roads = {}
        self.cell_size = grid_pixel_width // width
        self.cell_radius = 2
        self.cell_offset = self.cell_radius // 2

        self.density = 6

        self.offset_x = (screen_width - grid_pixel_width) // 2
        self.offset_y = (screen_height - grid_pixel_height) // 2

        self.initialized = False

    def initialize(self, chunk_size=4096):
        """Generator that builds the grid in chunks for faster loading progress."""
        chunk_size = max(1, int(chunk_size))
        steps_done = 0

        for i in range(self.width):
            x = self.offset_x + self.cell_size * i + self.cell_offset
            for j in range(self.height):
                y = self.offset_y + self.cell_size * j + self.cell_offset
                self.cells[i][j] = Cell(x=x, y=y, i=i, j=j)
                steps_done += 1
                if steps_done >= chunk_size:
                    yield steps_done
                    steps_done = 0

        for i in range(self.width):
            for j in range(self.height):
                if i + 1 < self.width:
                    self.roads[((i, j), (i + 1, j))] = Road(cell1=self.cells[i][j], cell2=self.cells[i + 1][j])
                    steps_done += 1
                    if steps_done >= chunk_size:
                        yield steps_done
                        steps_done = 0
                if j + 1 < self.height:
                    self.roads[((i, j), (i, j + 1))] = Road(cell1=self.cells[i][j], cell2=self.cells[i][j + 1])
                    steps_done += 1
                    if steps_done >= chunk_size:
                        yield steps_done
                        steps_done = 0

        if steps_done > 0:
            yield steps_done

        self.split_grid()
        self.initialized = True

    def split_grid(self):
        self.horizontal_roads_nr = self.width // self.density
        self.vertical_roads_nr = self.height // self.density

        for i in range(self.horizontal_roads_nr):
            height = i * self.density + random.randint(0, self.density - 1)

            for j in range(self.width - 1):
                self.roads[((j, height), (j + 1, height))].color = (100, 100, 100)
                self.roads[((j, height), (j + 1, height))].width = 3
                self.cells[j][height].passable = True
                self.cells[j + 1][height].passable = True

        for i in range(self.vertical_roads_nr):
            width = i * self.density + random.randint(0, self.density - 1)

            for j in range(self.height - 1):
                self.roads[((width, j), (width, j + 1))].color = (100, 100, 100)
                self.roads[((width, j), (width, j + 1))].width = 3
                self.cells[width][j].passable = True
                self.cells[width][j + 1].passable = True
                    

    