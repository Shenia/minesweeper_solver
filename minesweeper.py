import pygame
import random
from config import IMAGE_DICTIONARY, FLAGGED_IMAGE, BOMB_IMAGE, INITIAL_IMAGE, MARGIN, SPACE_SIDE_LENGTH, BACKGROUND_COLOUR
from config import BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_FIELD_MARGIN, SOLVE_BUTTON_IMAGE, SAVE_BUTTON_IMAGE, NEW_BUTTON_IMAGE, PLAY_BUTTON_IMAGE
from config import NUMBER_OF_ROWS, NUMBER_OF_COLS, NUMBER_OF_BOMBS
from solver import solver, get_adjacent

def main():
    # Game Settings
    nrow = NUMBER_OF_ROWS
    ncol = NUMBER_OF_COLS
    nbombs = NUMBER_OF_BOMBS
    
    # Window Setup
    pygame.init() 
    global gameDisplay 
    gameDisplay = pygame.display.set_mode(set_display(ncol, nrow))
    gameDisplay.fill(BACKGROUND_COLOUR)
    pygame.display.set_caption("Minesweeper")
    
    # Objects Setup
    field = Field(ncol, nrow, (MARGIN, MARGIN), nbombs)
    solve_button = Button(ncol, nrow, SOLVE_BUTTON_IMAGE, 0, 3)
    save_button = Button(ncol, nrow, SAVE_BUTTON_IMAGE, 1, 3)
    new_button = Button(ncol, nrow, NEW_BUTTON_IMAGE, 2, 3)
    mode = "play"

    while True:
        pygame.time.wait(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_position = pygame.mouse.get_pos()
                if mode == "play" and mouse_position[0] >= field.position[0] and mouse_position[0] < field.position[0] + field.width and mouse_position[1] >= field.position[1] and mouse_position[1] < field.position[1] + field.height:
                    mouse_solver(field, mouse_position, event.button)
                elif mouse_position[0] >= solve_button.display_x and mouse_position[0] < solve_button.display_x + BUTTON_WIDTH and mouse_position[1] >= solve_button.display_y and mouse_position[1] < solve_button.display_y + BUTTON_HEIGHT:
                    if mode == "play":
                        mode = "solve"
                        solve_button.set_button_img(PLAY_BUTTON_IMAGE)
                    elif mode == "solve":
                        mode = "play"
                        solve_button.set_button_img(SOLVE_BUTTON_IMAGE)
                elif mouse_position[0] >= save_button.display_x and mouse_position[0] < save_button.display_x + BUTTON_WIDTH and mouse_position[1] >= save_button.display_y and mouse_position[1] < save_button.display_y + BUTTON_HEIGHT:
                    restart(field)
                    mode = "play"
                    solve_button.set_button_img(SOLVE_BUTTON_IMAGE)
                elif mouse_position[0] >= new_button.display_x and mouse_position[0] < new_button.display_x + BUTTON_WIDTH and mouse_position[1] >= new_button.display_y and mouse_position[1] < new_button.display_y + BUTTON_HEIGHT:
                    del field
                    field = new_game(ncol, nrow, (MARGIN, MARGIN), nbombs)
                    mode = "play"
                    solve_button.set_button_img(SOLVE_BUTTON_IMAGE)

        if mode == "solve":
            solver(field)

def new_game(ncol, nrow, margin, nbombs):
    f = Field(ncol, nrow, margin, nbombs)
    return f

def mouse_solver(field, mouse_position, event_button):
    space_position_x = (mouse_position[0] - field.position[0]) // field.space_side_length
    space_position_y = (mouse_position[1] - field.position[1]) // field.space_side_length
    if event_button == 1:
        field.open(space_position_x, space_position_y)
    elif event_button == 3:
        field.flag(space_position_x, space_position_y, False)
    return

def set_display(ncol, nrow):
    screen_width = ncol * SPACE_SIDE_LENGTH + 2 * MARGIN
    screen_height = nrow * SPACE_SIDE_LENGTH + 2 * MARGIN + BUTTON_HEIGHT + BUTTON_FIELD_MARGIN
    return (screen_width, screen_height)

def restart(field):
    field.exploded = False
    field.won = False
    for col in field.array_of_spaces:
        for space in col:
            space.opened = False
            space.flagged = False
            space.set_image(INITIAL_IMAGE)
    return

class Button:
    def __init__(self, ncol, nrow, image, order, total):
        self.display_x = ((ncol * SPACE_SIDE_LENGTH + 2 * MARGIN) / (total + 1)) * (order + 1) - (BUTTON_WIDTH / 2)
        self.display_y = MARGIN + nrow * SPACE_SIDE_LENGTH + BUTTON_FIELD_MARGIN
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (BUTTON_WIDTH, BUTTON_HEIGHT))
        self.set_button()
    
    def set_button(self):
        gameDisplay.blit(self.image, (self.display_x, self.display_y))
        rect = pygame.Rect(self.display_x, self.display_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.display.update(rect)
        return
    
    def set_button_img(self, img):
        self.image = pygame.image.load(img)
        self.image = pygame.transform.scale(self.image, (BUTTON_WIDTH, BUTTON_HEIGHT))
        self.set_button()
        return

class Field:
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
        self.won = False
        self.bombs_set = False

    def get_started(self):
        return self.bombs_set
    
    def get_num_bombs(self):
        return self.num_bombs
    
    def get_num_row(self):
        return self.num_row
    
    def get_num_col(self):
        return self.num_col

    def get_clues(self):
        clues = []
        opened = []
        flagged = []
        for x, col in enumerate(self.array_of_spaces):
            for y, space in enumerate(col):
                if space.opened:
                    num_bombs = space.get_number()
                    opened.append((x, y))
                    if num_bombs != 0:
                        clues.append((x, y, num_bombs))
                elif space.flagged:
                    flagged.append((x, y))
        return clues, opened, flagged

    def open(self, position_x, position_y):
        if self.bombs_set == False:
            self.bombs_set = True
            self.plant_bombs(position_x, position_y)
            
        self.array_of_spaces[position_x][position_y].open()
        #TODO: add winning sequence
        if self.exploded == True:
            print("exploded")
        if self.num_bombs == self.get_unopened():
            self.won = True
            print("win")
        return

    def get_unopened(self):
        num = 0
        for col in self.array_of_spaces:
            for space in col:
                if space.opened == False:
                    num = num + 1
        return num
    
    def flag(self, position_x, position_y, keep):
        self.array_of_spaces[position_x][position_y].flag(keep)

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

# status in ["safe", "flagged", "unknown"]
class Space:
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
            pygame.time.wait(100)

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
    
    def flag(self, keep):
        if keep and self.flagged:
            return
        
        if self.opened:
            return
        elif self.flagged:
            self.flagged = False
            self.set_image(INITIAL_IMAGE)
        else:
            self.flagged = True
            self.set_image(FLAGGED_IMAGE)
            pygame.time.wait(70)
            return

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
    
    def get_unopened(self):
        num = 0
        for adjacent_space_position in self.adjacent_space_positions:
            if self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].opened == False:
                num += 1
        return num

if __name__ == '__main__':
    main()