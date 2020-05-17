Todos:
1. create minesweeper game
2. implement hardcoded solving rules
    1. If the sum of 
        the number of unknown adjacent spaces, and
        the number of flagged adjacent spaces
    is equal to the number of mines in adjacent spaces, 
    then all unknown adjacent spaces contain mines. Flag all unknown adjacent spaces.
    2. If the number of flagged adjacent spaces is equal to the number of mines in adjacent spaces, 
    then all unknown adjacent spaces do not contain mines. Open all unknown adjacent spaces.
    3. The number of unflagged bombs equal to the difference between
        the number of adjacent spaces that contain mines, and
        the number of flagged adjacent spaces. And the group of unknown adjacent spaces contain the number of unflagged bombs.
    
    