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
    gameDisplay = pygame.display.set_mode(screen_dimensions(ncol, nrow, SPACE_SIDE_LENGTH, MARGIN, BUTTON_HEIGHT, BUTTON_FIELD_MARGIN))
    gameDisplay.fill(BACKGROUND_COLOUR)
    pygame.display.set_caption("Minesweeper")
    
    # Object Setup
    field = Field(ncol, nrow, (MARGIN, MARGIN), nbombs)
    solve_button = Button(BUTTON_WIDTH, BUTTON_HEIGHT, ncol, nrow, SOLVE_BUTTON_IMAGE, 0, 3)
    save_button = Button(BUTTON_WIDTH, BUTTON_HEIGHT, ncol, nrow, SAVE_BUTTON_IMAGE, 1, 3)
    new_button = Button(BUTTON_WIDTH, BUTTON_HEIGHT, ncol, nrow, NEW_BUTTON_IMAGE, 2, 3)

    # Game Mode: play, solve, end
    mode = "play"

    while True:
        pygame.time.wait(60)

        for event in pygame.event.get():
            # Quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # Select action
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_position = pygame.mouse.get_pos()
                if mode == "play" and field.rect.collidepoint(mouse_position):
                    mouse_solver(field, mouse_position, event.button)
                elif mode == "play" and solve_button.rect.collidepoint(mouse_position):
                    mode = "solve"
                    solve_button.set_button_img(PLAY_BUTTON_IMAGE)
                elif mode == "solve" and solve_button.rect.collidepoint(mouse_position):
                    mode = "play"
                    solve_button.set_button_img(SOLVE_BUTTON_IMAGE)
                elif save_button.rect.collidepoint(mouse_position):
                    mode = "play"
                    solve_button.set_button_img(SOLVE_BUTTON_IMAGE)
                    field.restart()
                elif new_button.rect.collidepoint(mouse_position):
                    mode = "play"
                    solve_button.set_button_img(SOLVE_BUTTON_IMAGE)
                    del field
                    field = new_game(ncol, nrow, (MARGIN, MARGIN), nbombs)

        if mode == "solve":
            solver(field)
        
        if field.won or field.exploded:
            mode = "end"

# Create new game
def new_game(ncol, nrow, margin, nbombs):
    f = Field(ncol, nrow, margin, nbombs)
    return f

# Handle mouse-field interaction
def mouse_solver(field, mouse_position, event_button):
    space_position_x = (mouse_position[0] - field.position[0]) // field.space_side_length
    space_position_y = (mouse_position[1] - field.position[1]) // field.space_side_length
    if event_button == 1:
        field.open(space_position_x, space_position_y)
    elif event_button == 3:
        field.flag(space_position_x, space_position_y, False)
    return

# Calculate screen dimensions
# Set to have one row of buttons side-by-side, assume field width is longer than the sum of all buttons' widths
def screen_dimensions(ncol, nrow, space_side_length, margin, button_height, button_field_margin):
    screen_width = ncol * space_side_length + 2 * margin
    screen_height = nrow * space_side_length + 2 * margin + button_height + button_field_margin
    return (screen_width, screen_height)

# TODO: set public/private functions
class Button:
    def __init__(self, button_width, button_height, ncol, nrow, image, order, total):
        self.display_x = ((ncol * SPACE_SIDE_LENGTH + 2 * MARGIN) / (total + 1)) * (order + 1) - (button_width / 2)
        self.display_y = MARGIN + nrow * SPACE_SIDE_LENGTH + BUTTON_FIELD_MARGIN
        self.width = button_width
        self.height = button_height
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = pygame.Rect(self.display_x, self.display_y, self.width, self.height)
        self.set_button()
    
    # Set and display button image
    def set_button(self):
        gameDisplay.blit(self.image, (self.display_x, self.display_y))
        pygame.display.update(self.rect)
        return
    
    # Replace and display button image
    def set_button_img(self, img):
        self.image = pygame.image.load(img)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.set_button()
        return

# TODO: set public/private functions
class Field:
    def __init__(self, num_col, num_row, position, num_bombs):
        # Field size/location
        self.position = position
        self.height = num_row * SPACE_SIDE_LENGTH
        self.width = num_col * SPACE_SIDE_LENGTH
        self.rect = pygame.Rect(position[0], position[1], self.width, self.height)
        
        # Field space properties
        self.space_side_length = SPACE_SIDE_LENGTH
        self.num_row = num_row
        self.num_col = num_col
        self.num_bombs = num_bombs
        self.array_of_spaces = [[Space(False, x, y, self) for y in range(self.num_row)] for x in range(self.num_col)]
        
        # Game properties
        self.exploded = False
        self.won = False
        self.bombs_set = False

    # Accessible by solver
    def get_field_info(self):
        return (self.num_row, self.num_col, self.num_bombs, self.bombs_set)

    # Accessible by solver
    def get_clues(self):
        clues = []
        opened = []
        flagged = []
        for x, col in enumerate(self.array_of_spaces):
            for y, space in enumerate(col):
                if space.opened:
                    opened.append((x, y))
                if space.opened and num_bombs != 0:
                    num_bombs = space.get_number()
                    clues.append((x, y, num_bombs))
                if space.flagged:
                    flagged.append((x, y))
        return clues, opened, flagged

    # Restart Game
    def restart(self):
        self.exploded = False
        self.won = False
        for col in self.array_of_spaces:
            for space in col:
                space.opened = False
                space.flagged = False
                space.explosion_reached = False
                space.set_image(INITIAL_IMAGE)
        return

    # Open the space at position_x, position_y
    def open(self, position_x, position_y):
        # If game hasn't started, set bombs
        if self.bombs_set == False:
            self.bombs_set = True
            self.plant_bombs(position_x, position_y)
            
        # Open the space at position_x, position_y
        #TODO: add winning sequence
        self.array_of_spaces[position_x][position_y].open()
        # Determine if game is lost
        if self.exploded == True:
            print("exploded")
        # Determine if game is won
        if self.num_bombs == self.get_unopened() and self.exploded != True:
            self.won = True
            print("win")
        return

    # Return the number of unopened spaces
    def get_unopened(self):
        num = 0
        for col in self.array_of_spaces:
            for space in col:
                if space.opened == False:
                    num = num + 1
        return num
    
    # Flag the space
    # If keep and the space is already flagged, then the space continues to stay flagged
    # Else if not keep and the space is already flagged, then the space is unflagged
    def flag(self, position_x, position_y, keep):
        self.array_of_spaces[position_x][position_y].flag(keep)

    # Randomly plant bombs
    # The position passed in and the positions immediately adjacent to it will not contain bombs
    def plant_bombs(self, position_x, position_y):    
        # Each space in the field is assigned a number determined by their position. Space at position (x, y) is assigned x*ncol+y
        # The number is placed into space_list, where random positions to plant bombs are drawn from
        space_list = []
        for i in range(self.num_col * self.num_row):
            space_list.append(i)
        
        # The numbers representing bomb_free spaces are removed from space_list so that bombs won't be planted there
        bomb_free_spaces = get_adjacent(position_x, position_y, self.num_col, self.num_row)
        bomb_free_spaces.append((position_x, position_y))
        for position in bomb_free_spaces:
            num = position[1] * self.num_col + position[0]
            space_list.remove(num)
        
        # Positions are drawn randomly from space_list and removed. Bombs will be planted in drawn positions.
        for n in range(self.num_bombs):
            random_index = random.randint(0, len(space_list) - 1)
            random_number = space_list.pop(random_index) 
            x = random_number % self.num_col
            y = random_number // self.num_col
            self.array_of_spaces[x][y].has_mine = True
        return

# TODO: set public/private functions
class Space:
    def __init__(self, has_mine, position_x, position_y, field):        
        # Set field
        self.field = field
        
        # Position and display
        self.position_x = position_x
        self.position_y = position_y
        self.side_length = self.field.space_side_length
        self.display_x = self.field.position[0] + self.position_x * self.side_length
        self.display_y = self.field.position[1] + self.position_y * self.side_length
        self.set_image(INITIAL_IMAGE)
                
        # Game properties
        self.has_mine = has_mine
        self.explosion_reached = False
        # TODO: change positions to space pointers
        self.adjacent_space_positions = get_adjacent(self.position_x, self.position_y, self.field.num_col, self.field.num_row)

        # Player/solver toggle
        self.opened = False
        self.flagged = False
    
    # Set and display image
    def set_image(self, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))        
        gameDisplay.blit(self.image, (self.display_x, self.display_y))
        rect = pygame.Rect(self.display_x, self.display_y, self.side_length, self.side_length)
        pygame.display.update(rect)
    
    # Explode self, add adjacent spaces to explosion queue
    # TODO: rewrite explosion function (move to field)
    def explosion(self, queue):
        self.explode()
        for adjacent_space_position in self.adjacent_space_positions:
            if self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].explosion_reached == False and adjacent_space_position not in queue:
                queue.append(adjacent_space_position)
        return queue

    # Any space can explode
    def explode(self):
        self.explosion_reached = True
        if self.has_mine:
            self.set_image(BOMB_IMAGE)
            pygame.time.wait(100)

    # Open space, accessed through field
    def open(self):
        if self.opened or self.flagged:
            return
        elif self.has_mine:
            self.opened = True
            self.flagged = False
            self.field.exploded = True
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
    
    # Flag space, accessed through field. 
    # If keep and the space is already flagged, then the space continues to stay flagged
    # Else if not keep and the space is already flagged, then the space is unflagged
    def flag(self, keep):
        if self.opened:
            return
        elif keep and self.flagged:
            return
        elif keep == False and self.flagged:
            self.flagged = False
            self.set_image(INITIAL_IMAGE)
            return
        else:
            self.flagged = True
            self.set_image(FLAGGED_IMAGE)
            pygame.time.wait(70)
            return

    # Get the number of mines in adjacent spaces
    def get_number(self):
        if self.has_mine:
            raise ValueError("Can't get clue from exploded space")  
        else:
            num = 0
            for position in self.adjacent_space_positions:
                if self.field.array_of_spaces[position[0]][position[1]].has_mine:
                    num = num + 1
            return num

if __name__ == '__main__':
    main()