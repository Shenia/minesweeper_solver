import pygame
import random
from config import IMAGE_DICTIONARY, FLAGGED_IMAGE, BOMB_IMAGE, INITIAL_IMAGE, MARGIN, SPACE_SIDE_LENGTH, SOLVE_BUTTON_HEIGHT, SOLVE_BUTTON_WIDTH, BUTTON_FIELD_MARGIN, SOLVE_BUTTON_IMAGE, BACKGROUND_COLOUR

def main():
    nrow = 10
    ncol = 14
    number_of_bombs = 30
    screen_width = ncol * SPACE_SIDE_LENGTH + 2 * MARGIN
    screen_height = nrow * SPACE_SIDE_LENGTH + 2 * MARGIN + SOLVE_BUTTON_HEIGHT + BUTTON_FIELD_MARGIN
    
    pygame.init() 
    global gameDisplay 
    global clock
    gameDisplay = pygame.display.set_mode((screen_width, screen_height))
    gameDisplay.fill(BACKGROUND_COLOUR)
    clock = pygame.time.Clock()
    pygame.display.set_caption("Minesweeper")
    
    f = Field(ncol, nrow, (MARGIN, MARGIN), number_of_bombs)
    button = pygame.image.load(SOLVE_BUTTON_IMAGE)
    button = pygame.transform.scale(button, (SOLVE_BUTTON_WIDTH, SOLVE_BUTTON_HEIGHT))
    button_display_x = (ncol * SPACE_SIDE_LENGTH + 2 * MARGIN - SOLVE_BUTTON_WIDTH) / 2    
    button_display_y = MARGIN + nrow * SPACE_SIDE_LENGTH + BUTTON_FIELD_MARGIN
    gameDisplay.blit(button, (button_display_x, button_display_y))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONUP and f.exploded == False:
                mouse_position = pygame.mouse.get_pos()
                if mouse_position[0] >= f.position[0] and mouse_position[0] < f.position[0] + f.width and mouse_position[1] >= f.position[1] and mouse_position[1] < f.position[1] + f.height:
                    x = mouse_position[0] - f.position[0]
                    y = mouse_position[1] - f.position[1]
                    space_position_x = x // f.space_side_length
                    space_position_y = y // f.space_side_length
                    if event.button == 1:
                        f.open(space_position_x, space_position_y)
                    elif event.button == 3:
                        f.flag(space_position_x, space_position_y)
                elif mouse_position[0] >= button_display_x and mouse_position[0] < button_display_x + SOLVE_BUTTON_WIDTH and mouse_position[1] >= button_display_y and mouse_position[1] < button_display_y + SOLVE_BUTTON_HEIGHT:
                    print("solve")
        clock.tick(60)
    
class Field:
    array_of_spaces = [[]]
    def __init__(self, num_col, num_row, position, num_bombs):
        self.position = position
        self.num_bombs = num_bombs
        self.height = num_row * SPACE_SIDE_LENGTH
        self.width = num_col * SPACE_SIDE_LENGTH
        self.space_side_length = SPACE_SIDE_LENGTH
        self.num_row = num_row
        self.num_col = num_col
        self.array_of_spaces = [[Space(False, x, y, self) for y in range(self.num_row)] for x in range(self.num_col)]
        self.exploded = False
        self.bombs_set = False

    def open(self, position_x, position_y):
        if self.bombs_set == False:
            self.bombs_set = True
            self.plant_bombs(position_x, position_y)
            
        self.array_of_spaces[position_x][position_y].open()
    
    def flag(self, position_x, position_y):
        self.array_of_spaces[position_x][position_y].flag()

    def plant_bombs(self, position_x, position_y):    
        rand_list = []
        for i in range(self.num_col * self.num_row):
            rand_list.append(i)
        
        adjacent = get_adjacent(position_x, position_y, self.num_col, self.num_row)
        adjacent.append((position_x, position_y))
        for position in adjacent:
            num = position[1] * self.num_col + position[0]
            rand_list.remove(num)
        
        for n in range(self.num_bombs):
            random_index = random.randint(0, len(rand_list) - 1)
            random_number = rand_list.pop(random_index) 
            x = random_number % self.num_col
            y = random_number // self.num_col
            self.array_of_spaces[x][y].has_mine = True
        return

def get_adjacent(position_x, position_y, num_col, num_row):
    check = []
    if position_x == 0:
        if position_y == 0:
            check.append((0, 1))
            check.append((1, 1))
            check.append((1, 0))
        elif position_y == num_row - 1:
            check.append((position_x, position_y-1))
            check.append((position_x+1, position_y-1))
            check.append((position_x+1, position_y))
        else:
            check.append((position_x, position_y-1))
            check.append((position_x, position_y+1))
            check.append((position_x+1, position_y-1))
            check.append((position_x+1, position_y))
            check.append((position_x+1, position_y+1))
    elif position_x == num_col - 1:
        if position_y == 0:
            check.append((position_x, 1))
            check.append((position_x-1, 0))
            check.append((position_x-1, 1))
        elif position_y == num_row - 1:
            check.append((position_x-1, position_y))
            check.append((position_x-1, position_y-1))
            check.append((position_x, position_y-1))
        else:
            check.append((position_x, position_y-1))
            check.append((position_x, position_y+1))
            check.append((position_x-1, position_y-1))
            check.append((position_x-1, position_y))
            check.append((position_x-1, position_y+1))
    elif position_y == 0:
        check.append((position_x-1, position_y))
        check.append((position_x+1, position_y))
        check.append((position_x-1, position_y+1))
        check.append((position_x, position_y+1))
        check.append((position_x+1, position_y+1))
    elif position_y == num_row - 1:
        check.append((position_x-1, position_y))
        check.append((position_x+1, position_y))
        check.append((position_x-1, position_y-1))
        check.append((position_x, position_y-1))
        check.append((position_x+1, position_y-1))
    else: 
        check.append((position_x-1, position_y-1))
        check.append((position_x-1, position_y))
        check.append((position_x-1, position_y+1))
        check.append((position_x, position_y-1))
        check.append((position_x, position_y+1))
        check.append((position_x+1, position_y-1))
        check.append((position_x+1, position_y))
        check.append((position_x+1, position_y+1))
    return check

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
        self.explosion_reached = False
        self.position_x = position_x
        self.position_y = position_y
        self.side_length = self.field.space_side_length
        self.display_position_x = self.field.position[0] + self.position_x * self.side_length
        self.display_position_y = self.field.position[1] + self.position_y * self.side_length
        self.adjacent_space_positions = get_adjacent(self.position_x, self.position_y, self.field.num_col, self.field.num_row)
        self.set_image(INITIAL_IMAGE)
    
    def explosion(self, queue):
        self.explode()
        for adjacent_space_position in self.adjacent_space_positions:
            if self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].explosion_reached == False and adjacent_space_position not in queue:
                queue.append(adjacent_space_position)
        return queue

    def explode(self):
        self.explosion_reached = True
        if self.has_mine:
            self.set_image(BOMB_IMAGE)
        clock.tick(60)

    def set_image(self, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))        
        gameDisplay.blit(self.image, (self.display_position_x, self.display_position_y))
        rect = pygame.Rect(self.display_position_x, self.display_position_y, self.side_length, self.side_length)
        pygame.display.update(rect)

    def open(self):
        if self.opened or self.flagged:
            return
        elif self.has_mine:
            self.field.exploded = True
            self.opened = True
            self.flagged = False
            queue = self.explosion([])
            while queue:
                position = queue.pop(0)
                queue = self.field.array_of_spaces[position[0]][position[1]].explosion(queue)
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
    
    # def get_adjacent(self):
    #     check = []
    #     if self.position_x == 0:
    #         if self.position_y == 0:
    #             check.append((0, 1))
    #             check.append((1, 1))
    #             check.append((1, 0))
    #         elif self.position_y == self.field.num_row - 1:
    #             check.append((self.position_x, self.position_y-1))
    #             check.append((self.position_x+1, self.position_y-1))
    #             check.append((self.position_x+1, self.position_y))
    #         else:
    #             check.append((self.position_x, self.position_y-1))
    #             check.append((self.position_x, self.position_y+1))
    #             check.append((self.position_x+1, self.position_y-1))
    #             check.append((self.position_x+1, self.position_y))
    #             check.append((self.position_x+1, self.position_y+1))
    #     elif self.position_x == self.field.num_col - 1:
    #         if self.position_y == 0:
    #             check.append((self.position_x, 1))
    #             check.append((self.position_x-1, 0))
    #             check.append((self.position_x-1, 1))
    #         elif self.position_y == self.field.num_row - 1:
    #             check.append((self.position_x-1, self.position_y))
    #             check.append((self.position_x-1, self.position_y-1))
    #             check.append((self.position_x, self.position_y-1))
    #         else:
    #             check.append((self.position_x, self.position_y-1))
    #             check.append((self.position_x, self.position_y+1))
    #             check.append((self.position_x-1, self.position_y-1))
    #             check.append((self.position_x-1, self.position_y))
    #             check.append((self.position_x-1, self.position_y+1))
    #     elif self.position_y == 0:
    #         check.append((self.position_x-1, self.position_y))
    #         check.append((self.position_x+1, self.position_y))
    #         check.append((self.position_x-1, self.position_y+1))
    #         check.append((self.position_x, self.position_y+1))
    #         check.append((self.position_x+1, self.position_y+1))
    #     elif self.position_y == self.field.num_row - 1:
    #         check.append((self.position_x-1, self.position_y))
    #         check.append((self.position_x+1, self.position_y))
    #         check.append((self.position_x-1, self.position_y-1))
    #         check.append((self.position_x, self.position_y-1))
    #         check.append((self.position_x+1, self.position_y-1))
    #     else: 
    #         check.append((self.position_x-1, self.position_y-1))
    #         check.append((self.position_x-1, self.position_y))
    #         check.append((self.position_x-1, self.position_y+1))
    #         check.append((self.position_x, self.position_y-1))
    #         check.append((self.position_x, self.position_y+1))
    #         check.append((self.position_x+1, self.position_y-1))
    #         check.append((self.position_x+1, self.position_y))
    #         check.append((self.position_x+1, self.position_y+1))
    #     return check

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