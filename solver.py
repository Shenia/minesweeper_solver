import pygame

def solver(field):
    num_row = field.get_num_row()
    num_col = field.get_num_col()
    mapping = Mapping(num_col, num_row)
    (clues, opened) = field.get_clues()

    for opened_space in opened:
        mapping.process_opened(opened_space)

    for clue in clues:
        mapping.process_clue_mark_bombs(clue)
    
    for clue in clues:
        mapping.process_clue_mark_safe(clue)
    
    mapping.flag(field)
    mapping.open(field, (2, 3))

    print("unopened")
    for col in mapping.field:
        for space in col:
            if space.opened == False:
                print((space.x, space.y), space.opened, space.status_known, space.value)
    print("clue_space")
    for col in mapping.field:
        for space in col:
            if space.clue_space:
                print((space.x, space.y), space.num_bombs, space.known_value_total)
    return

class Mapping:
    def __init__(self, ncol, nrow):
        self.field = [[MappingSpace(x, y, get_adjacent(x, y, ncol, nrow)) for y in range(nrow)] for x in range(ncol)]

    def open(self, field, default):
        started = field.get_started()
        if not started:
            field.open(default[0], default[1])
        else:
            for col in self.field:
                for space in col:
                    if space.status_known and space.value == 0:
                        field.open(space.x, space.y)
        return

    def flag(self, field):
        for col in self.field:
            for space in col:
                if space.status_known and space.value == 1:
                    field.flag(space.x, space.y, keep = True)
        return
    
    def process_opened(self, opened_space):
        self.field[opened_space[0]][opened_space[1]].opened = True
        self.field[opened_space[0]][opened_space[1]].status_known = True
        self.field[opened_space[0]][opened_space[1]].value = 0
        return       

    def process_clue_mark_bombs(self, clue):
        space = self.field[clue[0]][clue[1]]
        num_bombs = clue[2]
        known_value_total = 0
        num_unknown_spaces = 0

        for adjacent_position in space.adjacent_positions:
            if self.field[adjacent_position[0]][adjacent_position[1]].status_known == False:
                num_unknown_spaces += 1
            if self.field[adjacent_position[0]][adjacent_position[1]].status_known == True:
                known_value_total += self.field[adjacent_position[0]][adjacent_position[1]].value
        
        space.clue_space = True
        space.num_bombs = num_bombs
        space.known_value_total = known_value_total
        space.num_unknown_spaces = num_unknown_spaces

        if num_bombs == known_value_total + num_unknown_spaces:
            for adjacent_position in space.adjacent_positions:
                if self.field[adjacent_position[0]][adjacent_position[1]].status_known == False:
                    self.field[adjacent_position[0]][adjacent_position[1]].status_known = True
                    self.field[adjacent_position[0]][adjacent_position[1]].value = 1
        
        for adjacent_position in space.adjacent_positions:
            if self.field[adjacent_position[0]][adjacent_position[1]].status_known == False:
                num_unknown_spaces += 1
            if self.field[adjacent_position[0]][adjacent_position[1]].status_known == True:
                known_value_total += self.field[adjacent_position[0]][adjacent_position[1]].value
        
        space.clue_space = True
        space.num_bombs = num_bombs
        space.known_value_total = known_value_total
        space.num_unknown_spaces = num_unknown_spaces
        return
    
    def process_clue_mark_safe(self, clue):
        space = self.field[clue[0]][clue[1]]
        space.clue_space = True
        space.num_bombs = clue[2]
        self.update_status((clue[0], clue[1]))

        if space.num_bombs == space.known_value_total:
            for adjacent_position in space.adjacent_positions:
                if self.field[adjacent_position[0]][adjacent_position[1]].status_known == False:
                    self.field[adjacent_position[0]][adjacent_position[1]].status_known = True
                    self.field[adjacent_position[0]][adjacent_position[1]].value = 0
        
        self.update_status((clue[0], clue[1]))
        return
    
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

class MappingSpace:
    def __init__(self, x, y, adjacent_positions):
        self.opened = False
        self.status_known = False
        self.value = None
        self.x = x
        self.y = y
        self.adjacent_positions = adjacent_positions
        self.clue_space = False
        self.num_bombs = None
        self.known_value_total = None
        self.num_unknown_spaces = None

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