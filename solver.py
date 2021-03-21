import pygame
DEFAULT_OPEN_SPACE = (2, 3)

# TODO: add clues exhausted sequence
# TODO: optimize space/time
# TODO: finish commenting
def solver_one_step(field):
    # Get clues from field
    (num_row, num_col, num_bombs, started) = field.get_field_info()
    (clues, opened, flagged) = field.get_clues()

    # Create Mapping for abstration of the field
    mapping = Mapping(num_col, num_row, num_bombs, started)

    # Mark opened spaces in mapping
    for opened_space in opened:
        mapping.process_opened(opened_space)

    # Mark flagged spaces in mapping
    for flagged_space in flagged:
        mapping.process_flagged(flagged_space)

    # Process clues: mark clue_spaces in mapping to be processed
    for clue in clues:
        mapping.process_clue(clue[0], clue[1])
    
    # Mark bombs from clues(Rule 1): if the number of unopened adjacent spaces = the number of adjacent bombs, mark all adjacent unopened as bombs
    for col in mapping.field:
        for space in col:
            if space.clue_space:
                mapping.process_clue_mark_bombs(space)

    # Mark safe spaces from clues(Rule 2): if the number of flagged adjacent spaces = the number of adjacent bombs, mark all adjacent unflagged as safe
    for col in mapping.field:
        for space in col:
            if space.clue_space:
                mapping.process_clue_mark_safe(space)
    
    # Rule 3: for every MappingSpace marked as clue_space, add a link to Mapping, 
    # Each link is a set of unopened, unknown spaces followed by the number of bombs that exist amonst the set of spaces
    for col in mapping.field:
        for space in col:
            if space.clue_space:
                mapping.set_links(space)

    # Process Rule 3
    mapping.process_links()
    
    # Flag known bombs in game field according to mapping
    mapping.flag(field)

    # Open known safe spaces in game field according to mapping. If the game hasn't started, open the space at the position DEFAULT_OPEN_SPACE
    mapping.open(field, DEFAULT_OPEN_SPACE)
    return

# TODO: set public/private functions
class Mapping:
    def __init__(self, ncol, nrow, nbombs, started):
        self.field = [[MappingSpace(x, y, get_adjacent(x, y, ncol, nrow)) for y in range(nrow)] for x in range(ncol)]
        self.links = []
        self.num_bombs = nbombs
        self.started = started

    # If the game has started, open the spaces that are marked as unopened and bomb-free on the Mapping object in the playing field
    # If the game has not started, open the space at the postion that is passed in
    def open(self, field, default):
        if not self.started:
            field.open(default[0], default[1])
        else:
            for col in self.field:
                for space in col:
                    if space.status_known and space.opened == False and space.value == 0:
                        field.open(space.x, space.y)
                        pygame.time.wait(70)
        return

    # For all spaces marked as a bomb space, flag the spaces in the playing field as a bomb space
    def flag(self, field):
        for col in self.field:
            for space in col:
                if space.status_known and space.flagged == False and space.value == 1:
                    field.flag(space.x, space.y)
                    pygame.time.wait(70)
        return
    
    # Given a position of a space
    # mark the MappingSpace at that position as flagged
    def process_flagged(self, flagged_space):
        self.field[flagged_space[0]][flagged_space[1]].flagged = True
        self.field[flagged_space[0]][flagged_space[1]].status_known = True
        self.field[flagged_space[0]][flagged_space[1]].value = 1
        return
    
    # Given the position of a space
    # mark the MappingSpace at that position as opened
    def process_opened(self, opened_space):
        self.field[opened_space[0]][opened_space[1]].opened = True
        self.field[opened_space[0]][opened_space[1]].status_known = True
        self.field[opened_space[0]][opened_space[1]].value = 0
        return       

    # Given the position of and the number of bombs around an opened space
    # update the number of bombs around a MappingSpace at the same position.
    # if there are unopened spaces around that space
    # then mark this space as a clue_space
    def process_clue(self, clue_space, num_bombs):
        space = self.field[clue_space[0]][clue_space[1]]
        space.num_bombs = num_bombs       
        for adjacent_position in space.adjacent_positions:
            if self.field[adjacent_position[0]][adjacent_position[1]].opened == False:
                space.clue_space = True
    
    # Given the position of an opened space
    # if the number of bombs around that space is equal to the sum of the number of known bombs around that space and the number of unopened spaces around that space
    # then mark all unopened MappingSpaces around the MappingSpace at the given position as a bomb space
    def process_clue_mark_bombs(self, space):
        self.update_status((space.x, space.y))

        if space.num_bombs == space.known_value_total + space.num_unknown_spaces:
            for adjacent_position in space.adjacent_positions:
                if self.field[adjacent_position[0]][adjacent_position[1]].status_known == False:
                    self.field[adjacent_position[0]][adjacent_position[1]].status_known = True
                    self.field[adjacent_position[0]][adjacent_position[1]].value = 1
        
        self.update_status((space.x, space.y))
        return
    
    # Given the position of an opened space
    # if the number of bombs around that space is equal to the sum of the number of known bombs around that space
    # then mark all unopened MappingSpaces around the MappingSpace at the given position as a bomb-free space
    def process_clue_mark_safe(self, space):
        self.update_status((space.x, space.y))

        if space.num_bombs == space.known_value_total:
            for adjacent_position in space.adjacent_positions:
                if self.field[adjacent_position[0]][adjacent_position[1]].status_known == False:
                    self.field[adjacent_position[0]][adjacent_position[1]].status_known = True
                    self.field[adjacent_position[0]][adjacent_position[1]].value = 0
        
        self.update_status((space.x, space.y))
        return

    # 
    def set_links(self, space):
        self.update_status((space.x, space.y))
        if space.num_unknown_spaces == 0:
            return
        
        unknown_spaces = set()
        num_known_bombs = 0

        for adjacent_position in space.adjacent_positions:
            if self.field[adjacent_position[0]][adjacent_position[1]].status_known == False:
                unknown_spaces.add((adjacent_position[0], adjacent_position[1]))
        
        for adjacent_position in space.adjacent_positions:
            if self.field[adjacent_position[0]][adjacent_position[1]].status_known and self.field[adjacent_position[0]][adjacent_position[1]].value == 1:
                num_known_bombs += 1

        link = Link(space.num_bombs - num_known_bombs, unknown_spaces)
        self.links.append(link)
        return
    
    def process_links(self):
        num_known_bombs = 0
        unknown_spaces = set()
        
        for col in self.field:
            for space in col:
                if space.status_known and space.value == 1:
                    num_known_bombs += 1
                if space.status_known == False:
                    unknown_spaces.add((space.x, space.y))

        link = Link(self.num_bombs - num_known_bombs, unknown_spaces)
        self.links.append(link)

        additionalLinks = []

        #TODO: find a better way to do this
        for i1, link1 in enumerate(self.links):
            for i2, link2 in enumerate(self.links):
                if link2.spaces.issuperset(link1.spaces):
                    if len(link2.spaces.difference(link1.spaces)) != 0:
                        link2.spaces = link2.spaces.difference(link1.spaces)
                        link2.num_bombs = link2.num_bombs - link1.num_bombs
                elif ((link2.num_bombs - link1.num_bombs) == len(link2.spaces.difference(link1.spaces))):
                    links = [Link(0, link1.spaces.difference(link2.spaces)), Link(link1.num_bombs, link2.spaces.intersection(link1.spaces)), Link((link2.num_bombs - link1.num_bombs), link2.spaces.difference(link1.spaces))]
                    additionalLinks.extend(links)

        self.links.extend(additionalLinks)
        
        for link in self.links:
            if link.num_bombs == 0:
                for position in link.spaces:
                    if self.field[position[0]][position[1]].status_known == False:
                        self.field[position[0]][position[1]].status_known = True
                        self.field[position[0]][position[1]].value = 0
            elif link.num_bombs == len(link.spaces):
                for position in link.spaces:
                    if self.field[position[0]][position[1]].status_known == False:
                        self.field[position[0]][position[1]].status_known = True
                        self.field[position[0]][position[1]].value = 1       
        for link in self.links:
            print(link.num_bombs, link.spaces)
        print("end")         
        return
    
    # Given a MappingSpace's position in the 2D array, update the MappingSpace's known number of bombs and the number of spaces with unknown status in the Mapping object
    def update_status(self, position):
        space = self.field[position[0]][position[1]]
        known_value_total = 0
        num_unknown_spaces = 0

        for adjacent_position in space.adjacent_positions:
            if self.field[adjacent_position[0]][adjacent_position[1]].status_known == False:
                num_unknown_spaces += 1
            if self.field[adjacent_position[0]][adjacent_position[1]].status_known == True:
                known_value_total += self.field[adjacent_position[0]][adjacent_position[1]].value
        
        space.known_value_total = known_value_total
        space.num_unknown_spaces = num_unknown_spaces
        return

# TODO: set public/private functions
# The smallest of clues
class Link:
    def __init__(self, num_bombs, spaces):
        self.num_bombs = num_bombs
        self.spaces = spaces
        self.delete = False

# TODO: set public/private functions
# Spaces on the abstract player map
class MappingSpace:
    def __init__(self, x, y, adjacent_positions):
        self.opened = False
        self.flagged = False
        self.status_known = False
        self.value = None
        self.x = x
        self.y = y
        self.adjacent_positions = adjacent_positions
        self.clue_space = False
        self.num_bombs = None
        self.known_value_total = None
        self.num_unknown_spaces = None


# Given the dimensions of a 2D array and the position in the array, return an array of horizontally, vertically, diagonally adjacent spaces
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