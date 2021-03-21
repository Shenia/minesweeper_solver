import pygame
import random
from config import BACKGROUND_COLOUR
from config import NUMBER_OF_ROWS, NUMBER_OF_COLS, NUMBER_OF_BOMBS
from config import IMAGE_DICTIONARY, FLAGGED_IMAGE, BOMB_IMAGE, INITIAL_IMAGE, MARGIN
from config import SPACE_SIDE_LENGTH
from config import DIALOGUE_NO_STEP, DIALOGUE_WON, DIALOGUE_LOST
from config import DIALOGUE_WIDTH, DIALOGUE_HEIGHT, DIALOGUE_A_HEIGHT, DIALOGUE_A_WIDTH 
from config import DIALOGUE_OK_HEIGHT, DIALOGUE_OK_WIDTH, DIALOGUE_OK_X, DIALOGUE_OK_Y, DIALOGUE_X_HEIGHT, DIALOGUE_X_WIDTH, DIALOGUE_X_X, DIALOGUE_X_Y
from config import SOLVE_BUTTON_IMAGE, RESTART_BUTTON_IMAGE, NEW_BUTTON_IMAGE, PLAY_BUTTON_IMAGE, DISABLED_BUTTON_IMAGE
from config import BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_FIELD_MARGIN
from solver import solver_one_step, get_adjacent

def main():
    # Game Settings
    nbombs = NUMBER_OF_BOMBS
    margin = MARGIN
    space_side_length = SPACE_SIDE_LENGTH
    dialogue_width = DIALOGUE_WIDTH
    dialogue_height = DIALOGUE_HEIGHT
    button_width = BUTTON_WIDTH
    button_height = BUTTON_HEIGHT
    button_field_margin = BUTTON_FIELD_MARGIN
    background_colour = BACKGROUND_COLOUR

    # Dialogue Resolution
    dialogue_ratio_height = DIALOGUE_HEIGHT/DIALOGUE_A_HEIGHT
    dialogue_ratio_width = DIALOGUE_WIDTH/DIALOGUE_A_WIDTH
    dialogue_x_position = (DIALOGUE_X_X * dialogue_ratio_width, DIALOGUE_X_Y * dialogue_ratio_height)
    dialogue_x_size = (DIALOGUE_X_WIDTH * dialogue_ratio_width, DIALOGUE_X_HEIGHT * dialogue_ratio_height)
    dialogue_ok_position = (DIALOGUE_OK_X * dialogue_ratio_width, DIALOGUE_OK_Y * dialogue_ratio_height)
    dialogue_ok_size = (DIALOGUE_OK_WIDTH * dialogue_ratio_width, DIALOGUE_OK_HEIGHT * dialogue_ratio_height)

    # Window Setup
    pygame.init()
    global gameDisplay
    screen_size = screen_dimensions(NUMBER_OF_COLS, NUMBER_OF_ROWS, space_side_length, margin, button_height, button_field_margin)
    field_position = (margin, margin)
    space_size = (space_side_length, space_side_length)
    button_size = (button_width, button_height)
    dialogue_size = (dialogue_width, dialogue_height)
    gameDisplay = pygame.display.set_mode(screen_size)
    gameDisplay.fill(background_colour)
    pygame.display.set_caption("Minesweeper")
    
    # Object Setup
    field = Field(NUMBER_OF_COLS, NUMBER_OF_ROWS, field_position, nbombs, space_side_length)
    solve_button = Button(button_size, screen_size, SOLVE_BUTTON_IMAGE, 0, 3)
    restart_button = Button(button_size, screen_size, RESTART_BUTTON_IMAGE, 1, 3)
    new_button = Button(button_size, screen_size, NEW_BUTTON_IMAGE, 2, 3)
    dialogue = Dialogue(dialogue_size, field_position, field.get_size(), dialogue_x_position, dialogue_x_size, dialogue_ok_position, dialogue_ok_size)

    # Check Collision
    # gameDisplay.fill(background_colour, rect=dialogue.ok_rect)
    # pygame.display.update(dialogue.ok_rect)
    
    # Game Modes: play, solve, dialogue, end
    mode = "play"

    while True:
        # wait 60 ms before querying and resolving all queued events
        pygame.time.wait(60)

        for event in pygame.event.get():
            # Quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # Event: either toggling between play/solve mode, restarting a game, starting a new game, or solving the game manually (only available in play mode)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_position = pygame.mouse.get_pos()
                # solving the game manually (only when in game mode)
                if mode == "play" and field.rect.collidepoint(mouse_position):
                    manual(field, mouse_position, event.button)
                # toggling between play/solve mode (only when not in end mode)
                elif mode == "play" and solve_button.rect.collidepoint(mouse_position):
                    mode = "solve"
                    solve_button.set_button_img(PLAY_BUTTON_IMAGE)
                elif mode == "solve" and solve_button.rect.collidepoint(mouse_position):
                    mode = "play"
                    solve_button.set_button_img(SOLVE_BUTTON_IMAGE)
                # restarting a game
                elif restart_button.rect.collidepoint(mouse_position):
                    solve_button.set_button_img(SOLVE_BUTTON_IMAGE)
                    field.restart()
                    mode = "play"
                # starting a new game
                elif new_button.rect.collidepoint(mouse_position):
                    solve_button.set_button_img(SOLVE_BUTTON_IMAGE)
                    del field
                    field = Field(NUMBER_OF_COLS, NUMBER_OF_ROWS, (MARGIN, MARGIN), nbombs, SPACE_SIDE_LENGTH)
                    mode = "play"
        
        # after resolving all queued events, if in solve mode, run one solve iteration
        if mode == "solve":
            if field.edited or not field.bombs_set:
                field.edited = False
                solver_one_step(field)
            else:
                dialogue.display(DIALOGUE_NO_STEP)
                mode = "dialogue"
                while mode == "dialogue":
                    pygame.time.wait(60)
                    for event in pygame.event.get():
                        # Quit game
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()
                        elif event.type == pygame.MOUSEBUTTONUP:
                            mouse_position = pygame.mouse.get_pos()
                            if dialogue.x_rect.collidepoint(mouse_position) or dialogue.ok_rect.collidepoint(mouse_position):
                                field.redisplay()
                                mode = "play"
                                solve_button.set_button_img(SOLVE_BUTTON_IMAGE)
            
        # after resolving all queued events, if the game is won or ended, set game mode to end
        if (mode == "solve" or mode == "play") and (field.won or field.exploded):
            if field.won:
                dialogue.display(DIALOGUE_WON)
            else:
                dialogue.display(DIALOGUE_LOST)
            mode = "dialogue"
            while mode == "dialogue":
                pygame.time.wait(60)
                for event in pygame.event.get():
                    # Quit game
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    elif event.type == pygame.MOUSEBUTTONUP:
                        mouse_position = pygame.mouse.get_pos()
                        if dialogue.x_rect.collidepoint(mouse_position) or dialogue.ok_rect.collidepoint(mouse_position):
                            mode = "end"
                            solve_button.set_button_img(DISABLED_BUTTON_IMAGE)
                            field.redisplay()

# Calculate screen dimensions
# Set to have one row of buttons side-by-side, assume field width is longer than the sum of all buttons' widths
def screen_dimensions(ncol, nrow, space_side_length, margin, button_height, button_field_margin):
    screen_width = ncol * space_side_length + 2 * margin
    screen_height = nrow * space_side_length + 2 * margin + button_height + button_field_margin
    return (screen_width, screen_height)

def manual(field, mouse_position, event_button):
    position_x = (mouse_position[0] - field.position[0]) // field.space_side_length
    position_y = (mouse_position[1] - field.position[1]) // field.space_side_length
    if event_button == 1:
        field.open(position_x, position_y)
    elif event_button == 3:
        field.flag(position_x, position_y)
    return

class Dialogue:
    def __init__(self, dialogue_size, field_position, field_size, dialogue_x_position, dialogue_x_size, dialogue_ok_position, dialogue_ok_size):
        self.display_x = ((field_size[0] - dialogue_size[0]) / 2) + field_position[0]
        self.display_y = ((field_size[1] - dialogue_size[1]) / 2) + field_position[1]
        self.width = dialogue_size[0]
        self.height = dialogue_size[1]
        self.rect = pygame.Rect(self.display_x, self.display_y, self.width, self.height)

        self.x_x = self.display_x + dialogue_x_position[0]
        self.x_y = self.display_y + dialogue_x_position[1]
        self.x_width = dialogue_x_size[0]
        self.x_height = dialogue_x_size[1]
        self.x_rect = pygame.Rect(self.x_x, self.x_y, self.x_width, self.x_height)

        self.ok_x = self.display_x + dialogue_ok_position[0]
        self.ok_y = self.display_y + dialogue_ok_position[1]
        self.ok_width = dialogue_ok_size[0]
        self.ok_height = dialogue_ok_size[1]
        self.ok_rect = pygame.Rect(self.ok_x, self.ok_y, self.ok_width, self.ok_height)
    
    def display(self, image):
        display_image = pygame.transform.scale(pygame.image.load(image), (self.width, self.height))
        gameDisplay.blit(display_image, (self.display_x, self.display_y))
        pygame.display.update(self.rect)
        return
    
# TODO: set public/private functions
class Button:
    def __init__(self, button_size, screen_size, image, order, total):
        self.display_x = (screen_size[0] / (total + 1)) * (order + 1) - (button_size[0] / 2)
        self.display_y = screen_size[1] - button_size[1] - MARGIN
        self.width = button_size[0]
        self.height = button_size[1]
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
    def __init__(self, num_col, num_row, position, num_bombs, space_side_length):
        # Field size/location
        self.position = position
        self.height = num_row * space_side_length
        self.width = num_col * space_side_length
        self.rect = pygame.Rect(position[0], position[1], self.width, self.height)
        
        # Field space properties
        self.space_side_length = space_side_length
        self.num_row = num_row
        self.num_col = num_col
        self.num_bombs = num_bombs
        self.array_of_spaces = [[Space(False, x, y, self) for y in range(self.num_row)] for x in range(self.num_col)]
        self.redisplay()
        
        # Game properties
        self.edited = False
        self.exploded = False
        self.won = False
        self.bombs_set = False

    def get_size(self):
        return (self.width, self.height)

    def redisplay(self): 
        for x in range(self.num_col):
            for y in range(self.num_row):
                self.array_of_spaces[x][y].field_redisplay()
        pygame.display.update(self.rect)
                
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
                    if space.get_number() != 0:
                        clues.append(((x, y), space.get_number()))
                elif space.flagged:
                    flagged.append((x, y))
        return clues, opened, flagged

    # Restart Game
    def restart(self):
        self.exploded = False
        self.won = False
        self.edited = False
        for col in self.array_of_spaces:
            for space in col:
                space.opened = False
                space.flagged = False
                space.exploded = False
                space.set_image(INITIAL_IMAGE)
        self.redisplay()
        return

    # Open the space at position_x, position_y
    def open(self, position_x, position_y):
        self.edited = True
        # If game hasn't started, set bombs
        if self.bombs_set == False:
            self.bombs_set = True
            self.plant_bombs(position_x, position_y)
            
        # Open the space at position_x, position_y
        #TODO: add winning sequence
        self.array_of_spaces[position_x][position_y].open()
        # Determine if game is won
        if self.num_bombs == self.get_unopened() and self.exploded != True:
            self.won = True
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
    def flag(self, position_x, position_y):
        self.array_of_spaces[position_x][position_y].flag()

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
        self.rect = pygame.Rect(self.display_x, self.display_y, self.side_length, self.side_length)
        self.set_image(INITIAL_IMAGE)
                
        # Game properties
        self.has_mine = has_mine
        self.exploded = False
        # TODO: change positions to space pointers
        self.adjacent_space_positions = get_adjacent(self.position_x, self.position_y, self.field.num_col, self.field.num_row)

        # Player/solver toggle
        self.opened = False
        self.flagged = False

    def field_redisplay(self):
        gameDisplay.blit(self.image, (self.display_x, self.display_y))

    # Set and display image
    def set_image(self, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))        
    
    def display(self):
        gameDisplay.blit(self.image, (self.display_x, self.display_y))
        pygame.display.update(self.rect)
    
    # Any space can explode
    def explode(self, queue):
        newQueue = []
        for position in queue:
            space = self.field.array_of_spaces[position[0]][position[1]]
            space.exploded = True
            if space.has_mine:
                space.set_image(BOMB_IMAGE)
                space.display()
                # pygame.time.wait(50)
            for adjacent_space_position in space.adjacent_space_positions:
                if space.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].exploded == False and adjacent_space_position not in newQueue:
                    newQueue.append(adjacent_space_position)
        pygame.time.wait(100)
        if len(newQueue) != 0:
            self.explode(newQueue)
        return

    # Open space, accessed through field
    def open(self):
        if self.opened or self.flagged:
            return
        elif self.has_mine:
            self.field.exploded = True
            self.explode([(self.position_x, self.position_y)])
            return
        else:
            self.opened = True
            self.flagged = False
            num_mines = self.get_number()
            if num_mines == 0:
                self.set_image(IMAGE_DICTIONARY[0])
                self.display()
                for adjacent_space_position in self.adjacent_space_positions:
                    if self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].opened == False and self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].has_mine == False:
                        self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].open()
                return 
            elif num_mines >= 1 and num_mines <= 8:
                self.set_image(IMAGE_DICTIONARY[num_mines])
                self.display()
                return   
    
    # Flag space, accessed through field. 
    # If keep and the space is already flagged, then the space continues to stay flagged
    # Else if not keep and the space is already flagged, then the space is unflagged
    def flag(self):
        if self.opened:
            return
        elif self.flagged:
            self.flagged = False
            self.set_image(INITIAL_IMAGE)
            self.display()
            return
        else:
            self.flagged = True
            self.set_image(FLAGGED_IMAGE)
            self.display()
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