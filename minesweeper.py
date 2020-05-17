import pygame
import random
from config import IMAGE_DICTIONARY, FLAGGED_IMAGE, BOMB_IMAGE, INITIAL_IMAGE

def main():
    pygame.init() 
    gameDisplay = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Minesweeper")
    clock = pygame.time.Clock()
    f = Field(15, (50, 50), 700, 500, 20)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_position = pygame.mouse.get_pos()
                if mouse_position[0] >= f.position[0] and mouse_position[0] < f.position[0] + f.width and mouse_position[1] >= f.position[1] and mouse_position[1] < f.position[1] + f.height:
                    x = mouse_position[0] - f.position[0]
                    y = mouse_position[1] - f.position[1]
                    space_position_x = x // f.space_side_length
                    space_position_y = y // f.space_side_length
                    space = f.array_of_spaces[space_position_x][space_position_y]
                    if event.button == 1:
                        space.open()
                    elif event.button == 3:
                        space.flag()

        gameDisplay.fill((10, 10, 10))

        for col in f.array_of_spaces:
            for space in col:
                gameDisplay.blit(space.image, (space.display_position_x, space.display_position_y))

        pygame.display.update()
        clock.tick(60)
    
class Field:
    array_of_spaces = [[]]
    def __init__(self, num_row, position, width, height, num_bombs):
        self.position = position
        self.num_bombs = num_bombs
        self.height = height
        self.width = width
        self.space_side_length = int(self.height/num_row)
        self.num_row = num_row
        self.num_col = int(self.width/self.space_side_length)
        self.array_of_spaces = [[Space(False, x, y, self) for y in range(self.num_row)] for x in range(self.num_col)]
        self.plant_bombs()

    def plant_bombs(self):    
        rand_list = []

        for i in range(self.num_col * self.num_row):
            rand_list.append(i)
        
        for n in range(self.num_bombs):
            random_index = random.randint(0, self.num_col * self.num_row - 1 - n)
            random_number = rand_list.pop(random_index) 
            x = random_number % self.num_col
            y = random_number // self.num_col
            self.array_of_spaces[x][y].has_mine = True
            print(n, x, y)
        return

# status in ["safe", "flagged", "unknown"]
class Space:
    # player perspective
    status = "safe"
    number_of_unflagged_bombs = None

    def __init__(self, has_mine, position_x, position_y, field):
        self.field = field
        self.has_mine = has_mine
        self.opened = False
        self.flagged = False
        self.position_x = position_x
        self.position_y = position_y
        self.side_length = self.field.space_side_length
        self.display_position_x = self.field.position[0] + self.position_x * self.side_length
        self.display_position_y = self.field.position[1] + self.position_y * self.side_length
        self.adjacent_space_positions = self.get_adjacent()
        self.set_image(INITIAL_IMAGE)

    def set_image(self, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))

    def open(self):
        if self.opened or self.flagged:
            return
        elif self.has_mine:
            self.opened = True
            self.flagged = False
            self.set_image(BOMB_IMAGE)
            return
        else:
            self.opened = True
            self.flagged = False
            num_mines = self.get_number()
            if num_mines == 0:
                self.set_image(IMAGE_DICTIONARY[0])
                for adjacent_space_position in self.adjacent_space_positions:
                    if self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].opened == False and self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].has_mine == False:
                        self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].open()
                return 
            elif num_mines >= 1 and num_mines <= 8:
                self.set_image(IMAGE_DICTIONARY[num_mines])
                return
            else:
                raise ValueError("Invalid number of mines")     
    
    def flag(self):
        if self.opened:
            return
        elif self.flagged:
            self.flagged = False
            self.set_image(INITIAL_IMAGE)
        else:
            self.flagged = True
            self.set_image(FLAGGED_IMAGE)
            return
    
    def get_adjacent(self):
        check = []
        if self.position_x == 0:
            if self.position_y == 0:
                check.append((0, 1))
                check.append((1, 1))
                check.append((1, 0))
            elif self.position_y == self.field.num_row - 1:
                check.append((self.position_x, self.position_y-1))
                check.append((self.position_x+1, self.position_y-1))
                check.append((self.position_x+1, self.position_y))
            else:
                check.append((self.position_x, self.position_y-1))
                check.append((self.position_x, self.position_y+1))
                check.append((self.position_x+1, self.position_y-1))
                check.append((self.position_x+1, self.position_y))
                check.append((self.position_x+1, self.position_y+1))
        elif self.position_x == self.field.num_col - 1:
            if self.position_y == 0:
                check.append((self.position_x, 1))
                check.append((self.position_x-1, 0))
                check.append((self.position_x-1, 1))
            elif self.position_y == self.field.num_row - 1:
                check.append((self.position_x-1, self.position_y))
                check.append((self.position_x-1, self.position_y-1))
                check.append((self.position_x, self.position_y-1))
            else:
                check.append((self.position_x, self.position_y-1))
                check.append((self.position_x, self.position_y+1))
                check.append((self.position_x-1, self.position_y-1))
                check.append((self.position_x-1, self.position_y))
                check.append((self.position_x-1, self.position_y+1))
        elif self.position_y == 0:
            check.append((self.position_x-1, self.position_y))
            check.append((self.position_x+1, self.position_y))
            check.append((self.position_x-1, self.position_y+1))
            check.append((self.position_x, self.position_y+1))
            check.append((self.position_x+1, self.position_y+1))
        elif self.position_y == self.field.num_row - 1:
            check.append((self.position_x-1, self.position_y))
            check.append((self.position_x+1, self.position_y))
            check.append((self.position_x-1, self.position_y-1))
            check.append((self.position_x, self.position_y-1))
            check.append((self.position_x+1, self.position_y-1))
        else: 
            check.append((self.position_x-1, self.position_y-1))
            check.append((self.position_x-1, self.position_y))
            check.append((self.position_x-1, self.position_y+1))
            check.append((self.position_x, self.position_y-1))
            check.append((self.position_x, self.position_y+1))
            check.append((self.position_x+1, self.position_y-1))
            check.append((self.position_x+1, self.position_y))
            check.append((self.position_x+1, self.position_y+1))
        return check

    def get_number(self):
        if self.has_mine:
            return -1
        else:
            num = 0
            check = self.adjacent_space_positions
            for position in check:
                if self.field.array_of_spaces[position[0]][position[1]].has_mine:
                    num = num + 1
            return num

if __name__ == '__main__':
    main()