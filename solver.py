import pygame

def solver(field):
    num_row = field.get_num_row()
    num_col = field.get_num_col()
    num_bombs = field.get_num_bombs()
    mapping = Mapping(num_col, num_row, num_bombs)
    (clues, opened, flagged) = field.get_clues()

    for opened_space in opened:
        mapping.process_opened(opened_space)

    for flagged_space in flagged:
        mapping.process_flagged(flagged_space)

    for clue in clues:
        mapping.process_clue(clue)
    
    for col in mapping.field:
        for space in col:
            if space.clue_space:
                mapping.process_clue_mark_bombs(space)

    for col in mapping.field:
        for space in col:
            if space.clue_space:
                mapping.process_clue_mark_safe(space)
    
    for col in mapping.field:
        for space in col:
            if space.clue_space:
                mapping.set_links(space)

    mapping.process_links()
    
    mapping.flag(field)
    mapping.open(field, (2, 3))
    return

class Mapping:
    def __init__(self, ncol, nrow, nbombs):
        self.field = [[MappingSpace(x, y, get_adjacent(x, y, ncol, nrow)) for y in range(nrow)] for x in range(ncol)]
        self.links = []
        self.num_bombs = nbombs

    def open(self, field, default):
        started = field.get_started()
        if not started:
            field.open(default[0], default[1])
        else:
            for col in self.field:
                for space in col:
                    if space.status_known and space.opened == False and space.value == 0:
                        field.open(space.x, space.y)
                        pygame.time.wait(70)
        return

    def flag(self, field):
        for col in self.field:
            for space in col:
                if space.status_known and space.value == 1:
                    field.flag(space.x, space.y, keep = True)
        return
    
    def process_flagged(self, flagged_space):
        self.field[flagged_space[0]][flagged_space[1]].status_known = True
        self.field[flagged_space[0]][flagged_space[1]].value = 1
        return
    
    def process_opened(self, opened_space):
        self.field[opened_space[0]][opened_space[1]].opened = True
        self.field[opened_space[0]][opened_space[1]].status_known = True
        self.field[opened_space[0]][opened_space[1]].value = 0
        return       

    def process_clue(self, clue):
        space = self.field[clue[0]][clue[1]]
        space.num_bombs = clue[2]       
        for adjacent_position in space.adjacent_positions:
            if self.field[adjacent_position[0]][adjacent_position[1]].opened == False:
                space.clue_space = True

    def process_clue_mark_bombs(self, space):
        self.update_status((space.x, space.y))

        if space.num_bombs == space.known_value_total + space.num_unknown_spaces:
            for adjacent_position in space.adjacent_positions:
                if self.field[adjacent_position[0]][adjacent_position[1]].status_known == False:
                    self.field[adjacent_position[0]][adjacent_position[1]].status_known = True
                    self.field[adjacent_position[0]][adjacent_position[1]].value = 1
        
        self.update_status((space.x, space.y))
        return
    
    def process_clue_mark_safe(self, space):
        self.update_status((space.x, space.y))

        if space.num_bombs == space.known_value_total:
            for adjacent_position in space.adjacent_positions:
                if self.field[adjacent_position[0]][adjacent_position[1]].status_known == False:
                    self.field[adjacent_position[0]][adjacent_position[1]].status_known = True
                    self.field[adjacent_position[0]][adjacent_position[1]].value = 0
        
        self.update_status((space.x, space.y))
        return
        
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

class Link:
    def __init__(self, num_bombs, spaces):
        self.num_bombs = num_bombs
        self.spaces = spaces
        self.delete = False

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