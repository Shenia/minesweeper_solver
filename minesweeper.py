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

#TODO: set public/private functions
#TODO: set game so that no solver or manual could access it after explosion
#TODO: add number of bombs remaining
#TODO: add timer
#TODO: organize field/space display/update for new game/restart/redisplay
#TODO: stop solver when buttons are clicked
#TODO: solve with comparing multiple links/multiple passes
#TODO: set min number of bombs
def main():
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
    (screen_size, field_position) = screen_dimensions(NUMBER_OF_COLS, NUMBER_OF_ROWS, SPACE_SIDE_LENGTH, MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_FIELD_MARGIN)
    field_size = (NUMBER_OF_COLS * SPACE_SIDE_LENGTH, NUMBER_OF_ROWS * SPACE_SIDE_LENGTH)
    space_size = (SPACE_SIDE_LENGTH, SPACE_SIDE_LENGTH)
    button_size = (BUTTON_WIDTH, BUTTON_HEIGHT)
    solve_button_position = ((screen_size[0] * (1 / 4) - button_size[0] / 2), (screen_size[1] - button_size[1] - MARGIN))
    restart_button_position = ((screen_size[0] * (2 / 4) - button_size[0] / 2), (screen_size[1] - button_size[1] - MARGIN))
    new_button_position = ((screen_size[0] * (3 / 4) - button_size[0] / 2), (screen_size[1] - button_size[1] - MARGIN))
    dialogue_size = (DIALOGUE_WIDTH, DIALOGUE_HEIGHT)
    dialogue_position = (((field_size[0] - dialogue_size[0]) / 2) + field_position[0], ((field_size[1] - dialogue_size[1]) / 2) + field_position[1])
    gameDisplay = pygame.display.set_mode(screen_size)
    gameDisplay.fill(BACKGROUND_COLOUR)
    pygame.display.flip()
    pygame.display.set_caption("Minesweeper")
    
    # Object Setup
    field = Field(field_position, field_size, NUMBER_OF_COLS, NUMBER_OF_ROWS, NUMBER_OF_BOMBS, SPACE_SIDE_LENGTH)
    solve_button = Button(solve_button_position, button_size, SOLVE_BUTTON_IMAGE)
    restart_button = Button(restart_button_position, button_size, RESTART_BUTTON_IMAGE)
    new_button = Button(new_button_position, button_size, NEW_BUTTON_IMAGE)
    dialogue = Dialogue(dialogue_position, dialogue_size, dialogue_x_position, dialogue_x_size, dialogue_ok_position, dialogue_ok_size)

    # Word test
    # myFont = pygame.font.SysFont("Tahoma", 12)
    # words = myFont.render("You have rolled:", 1, (250, 250, 250))
    # gameDisplay.blit(words, (0, 0))
    # pygame.display.flip()

    # Check Collision
    # gameDisplay.fill(BACKGROUND_COLOUR, rect=dialogue.ok_rect)
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
                    mode = "play"
                    field.restart()
                # starting a new game
                elif new_button.rect.collidepoint(mouse_position):
                    solve_button.set_button_img(SOLVE_BUTTON_IMAGE)
                    mode = "play"
                    field.new_game()
        
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
                                all_redisplay(field, solve_button, restart_button, new_button)
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
                            all_redisplay(field, solve_button, restart_button, new_button)

# Calculate screen dimensions
# Set to have one row of buttons side-by-side, assume field width is longer than the sum of all buttons' widths
def screen_dimensions(ncol, nrow, space_side_length, margin, button_width, button_height, button_field_margin):
    if (ncol * space_side_length + margin * 2 > button_width * 3 + margin * 2 + 10 * 2):
        screen_width = ncol * space_side_length + margin * 2
        field_x = margin
    else:
        screen_width = button_width * 3 + margin * 2 + 10 * 2
        field_x = (screen_width - NUMBER_OF_COLS * SPACE_SIDE_LENGTH) // 2
    screen_height = nrow * space_side_length + 2 * margin + button_height + button_field_margin
    field_position = (field_x, margin)
    return ((screen_width, screen_height), field_position)

def all_redisplay(field, button_1, button_2, button_3):
    gameDisplay.fill(BACKGROUND_COLOUR)
    field.redisplay()
    button_1.set_button()
    button_2.set_button()
    button_3.set_button()
    pygame.display.flip()
    return 

def manual(field, mouse_position, event_button):
    position_x = (mouse_position[0] - field.position[0]) // field.space_side_length
    position_y = (mouse_position[1] - field.position[1]) // field.space_side_length
    if event_button == 1:
        field.open(position_x, position_y)
    elif event_button == 3:
        field.flag(position_x, position_y)
    return

class Dialogue:
    def __init__(self, position, size, dialogue_x_position, dialogue_x_size, dialogue_ok_position, dialogue_ok_size):
        self.position = position
        self.size = size
        self.rect = pygame.Rect(self.position, self.size)

        self.x_x = self.position[0] + dialogue_x_position[0]
        self.x_y = self.position[1] + dialogue_x_position[1]
        self.x_size = dialogue_x_size
        self.x_rect = pygame.Rect((self.x_x, self.x_y), self.x_size)

        self.ok_x = self.position[0] + dialogue_ok_position[0]
        self.ok_y = self.position[1] + dialogue_ok_position[1]
        self.ok_size = dialogue_ok_size
        self.ok_rect = pygame.Rect((self.ok_x, self.ok_y), self.ok_size)
    
    def display(self, image):
        display_image = pygame.transform.scale(pygame.image.load(image), self.size)
        gameDisplay.blit(display_image, self.position)
        pygame.display.update(self.rect)
        return
    
class Button:
    def __init__(self, position, size, image):
        self.position = position
        self.size = size
        self.rect = pygame.Rect(self.position, self.size)
        self.set_button_img(image)
    
    # Set and display button image
    def set_button(self):
        gameDisplay.blit(self.image, self.position)
        pygame.display.update(self.rect)
        return
    
    # Replace and display button image
    def set_button_img(self, img):
        self.image = pygame.image.load(img)
        self.image = pygame.transform.scale(self.image, self.size)
        self.set_button()
        return

class Field:
    def __init__(self, position, size, num_col, num_row, num_bombs, space_side_length):
        # Field size/location
        self.position = position
        self.size = size
        self.rect = pygame.Rect(self.position, self.size)
        self.space_side_length = space_side_length
        
        # Game settings
        self.num_row = num_row
        self.num_col = num_col
        self.num_bombs = num_bombs
        
        # Game properties and display
        self.edited = False
        self.exploded = False
        self.won = False
        self.bombs_set = False
        self.array_of_spaces = [[Space((x, y), self.space_side_length, self) for y in range(self.num_row)] for x in range(self.num_col)]
        self.display()
    
    def display(self): 
        pygame.display.update(self.rect)

    #TODO: merge new_game and restart in field and space
    # New Game
    def new_game(self):
        self.exploded = False
        self.won = False
        self.edited = False
        self.bombs_set = False
        for x in range(self.num_col):
            for y in range(self.num_row):
                self.array_of_spaces[x][y].new_game()
        self.display()
        return

    # Restart Game
    def restart(self):
        self.exploded = False
        self.won = False
        self.edited = False
        for x in range(self.num_col):
            for y in range(self.num_row):
                self.array_of_spaces[x][y].restart()
        self.display()
        return
    
    # Redisplay from dialogue
    def redisplay(self):
        for x in range(self.num_col):
            for y in range(self.num_row):
                self.array_of_spaces[x][y].reset_image()
        self.display()
        return 

    # Open the space at position_x, position_y
    def open(self, position_x, position_y):
        self.edited = True
        # If game hasn't started, set bombs
        if self.bombs_set == False:
            self.bombs_set = True
            self.plant_bombs(position_x, position_y)
            
        # Open the space at position_x, position_y
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
        self.edited = True
        self.array_of_spaces[position_x][position_y].flag()

    # Randomly plant bombs
    # The position passed in and the positions immediately adjacent to it will not contain bombs
    def plant_bombs(self, position_x, position_y):    
        # Each space in the field is assigned a number determined by their position. Space at position (x, y) is assigned x*ncol+y
        # The number is placed into space_list, where random positions to plant bombs are drawn from
        space_list = []
        for x in range(self.num_col):
            for y in range(self.num_row):
                space_list.append((x, y))
        
        # The numbers representing bomb_free spaces are removed from space_list so that bombs won't be planted there
        for position in self.array_of_spaces[position_x][position_y].adjacent_space_positions:
            space_list.remove(position)
        space_list.remove((position_x, position_y))
        
        # Positions are drawn randomly from space_list and removed. Bombs will be planted in drawn positions.
        for n in range(self.num_bombs):
            random_index = random.randint(0, len(space_list) - 1)
            random_position = space_list.pop(random_index) 
            self.array_of_spaces[random_position[0]][random_position[1]].has_mine = True
        return

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

class Space:
    def __init__(self, index, side_length, field):        
        # Set field
        self.field = field
        
        # Position
        self.index = index
        self.side_length = side_length
        #TODO: change positions to space pointers
        self.adjacent_space_positions = get_adjacent(self.index[0], self.index[1], self.field.num_col, self.field.num_row)
        self.position = (self.field.position[0] + self.index[0] * self.side_length, self.field.position[1] + self.index[1] * self.side_length)
        self.rect = pygame.Rect(self.position, (self.side_length, self.side_length))

        # Set new game
        self.new_game()

    # Reset for new game
    def new_game(self):
        # Display
        self.set_image(INITIAL_IMAGE)
        # Game properties
        self.has_mine = False
        self.exploded = False
        # Player/solver toggle
        self.opened = False
        self.flagged = False
        return 

    # Restart the game
    def restart(self):
        # Display
        self.set_image(INITIAL_IMAGE)
        # Game properties
        self.exploded = False
        # Player/solver toggle
        self.opened = False
        self.flagged = False
        return 

    # Set image
    def set_image(self, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))        
        gameDisplay.blit(self.image, self.position)
    
    # Reset image
    def reset_image(self):
        gameDisplay.blit(self.image, self.position)
    
    # Display image
    def display_individual(self):
        pygame.display.update(self.rect)
    
    # Any space can explode
    def explode(self, queue):
        newQueue = []
        for index in queue:
            space = self.field.array_of_spaces[index[0]][index[1]]
            space.exploded = True
            if space.has_mine:
                space.set_image(BOMB_IMAGE)
                space.display_individual()
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
            self.explode([self.index])
            return
        else:
            self.opened = True
            self.flagged = False
            num_mines = self.get_number()
            if num_mines == 0:
                self.set_image(IMAGE_DICTIONARY[0])
                self.display_individual()
                for adjacent_space_position in self.adjacent_space_positions:
                    if self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].opened == False and self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].has_mine == False:
                        self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].open()
                return 
            elif num_mines >= 1 and num_mines <= 8:
                self.set_image(IMAGE_DICTIONARY[num_mines])
                self.display_individual()
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
            self.display_individual()
            return
        else:
            self.flagged = True
            self.set_image(FLAGGED_IMAGE)
            self.display_individual()
            return

    # Get the number of mines in adjacent spaces
    def get_number(self):
        num = 0
        for position in self.adjacent_space_positions:
            if self.field.array_of_spaces[position[0]][position[1]].has_mine:
                num = num + 1
        return num

if __name__ == '__main__':
    main()