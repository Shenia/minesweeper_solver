import pygame
import random

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
                position = pygame.mouse.get_pos()
                if position[0] >= f.position[0] and position[0] < f.position[0] + f.width and position[1] >= f.position[1] and position[1] < f.position[1] + f.height:
                    x = position[0] - f.position[0]
                    y = position[1] - f.position[1]
                    position_x = int((x - x % f.space_side_length) / f.space_side_length)
                    position_y = int((y - y % f.space_side_length) / f.space_side_length)
                    if event.button == 1:
                        f.array_of_spaces[position_x][position_y].open()
                    elif event.button == 3:
                        f.array_of_spaces[position_x][position_y].flag()

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
        self.num_row = num_row
        self.num_col = int(self.width / int(self.height / self.num_row))
        self.space_side_length = int(self.height/self.num_row)
        self.array_of_spaces = [[Space(False, x, y, self) for y in range(self.num_row)] for x in range(self.num_col)]
        rand_list = []
        for i in range(self.num_col * self.num_row):
            rand_list.append(i)
        
        for n in range(self.num_bombs):
            rand_num = random.randint(0, self.num_col * self.num_row - 1 - n)
            rand_num = rand_list.pop(rand_num) 
            x = rand_num % self.num_col
            y = int((rand_num - x) / self.num_col)
            self.array_of_spaces[x][y].has_mine = True
            print(n, x, y)

# status in ["safe", "flagged", "unknown"]
class Space:
    # player perspective
    status = "safe"
    number_of_unflagged_bombs = None

    def __init__(self, has_mine, position_x, position_y, field):
        self.field = field
        self.has_mine = has_mine
        self.opened = False
        self.position_x = position_x
        self.position_y = position_y
        self.side_length = self.field.space_side_length
        self.display_position_x = self.field.position[0] + self.position_x * self.side_length
        self.display_position_y = self.field.position[1] + self.position_y * self.side_length
        self.image = pygame.image.load("img/unopened.png")
        self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))

    def open(self):
        if self.opened:
            return
        elif self.has_mine:
            self.opened = True
            self.image = pygame.image.load("img/space_black.png")
            self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))
            return
        elif self.has_mine != True:
            num_mines = self.get_number()
            if num_mines == 0:
                self.opened = True
                self.image = pygame.image.load("img/0.png")
                self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))
                check = self.get_adjacent()
                for adjacent_space_position in check:
                    if self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].opened == False and self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].has_mine == False:
                        self.field.array_of_spaces[adjacent_space_position[0]][adjacent_space_position[1]].open()
                    else:
                        pass
                return 
            elif num_mines == 1:
                self.opened = True
                self.image = pygame.image.load("img/1.png")
                self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))
                return 
            elif num_mines == 2:
                self.opened = True
                self.image = pygame.image.load("img/2.png")
                self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))
                return 
            elif num_mines == 3:
                self.opened = True
                self.image = pygame.image.load("img/3.png")
                self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))
                return 
            elif num_mines == 4:
                self.opened = True
                self.image = pygame.image.load("img/4.png")
                self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))
                return 
            elif num_mines == 5:
                self.opened = True
                self.image = pygame.image.load("img/5.png")
                self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))
                return 
            elif num_mines == 6:
                self.opened = True
                self.image = pygame.image.load("img/6.png")
                self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))
                return 
            elif num_mines == 7:
                self.opened = True
                self.image = pygame.image.load("img/7.png")
                self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))
                return 
            elif num_mines == 8:
                self.opened = True
                self.image = pygame.image.load("img/8.png")
                self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))
                return 
            else:
                raise ValueError("Too many mines!")     
    
    def flag(self):
        if self.opened:
            return
        else:
            self.image = pygame.image.load("img/flagged.png")
            self.image = pygame.transform.scale(self.image, (self.side_length, self.side_length))
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
            check = self.get_adjacent()
            for position in check:
                if self.field.array_of_spaces[position[0]][position[1]].has_mine:
                    num = num + 1
            return num

if __name__ == '__main__':
    main()