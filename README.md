Todos:

1. create minesweeper game (done)
2. implement hardcoded solving rules (done)
   1. For a space a, if the sum of the number of unknown adjacent spaces, and the number of flagged adjacent spaces is equal to the number of mines in adjacent spaces, then
      all unknown adjacent spaces contain mines.
   2. For a space a, if the number of flagged adjacent spaces is equal to the number of mines in adjacent spaces, then
      all unknown adjacent spaces do not contain mines.
   3. Between any two adjacent spaces a and b, let A be the set of a's unknown adjacent spaces, let B be the set of b's unknown adjacent spaces. If the size of (A - B) = the number of bombs in A - the number of bombs in B, then
      the number of bombs in (A intersect B) = the number of bombs in B, and
      the number of bombs in (B - A) = 0, and
      the number of bombs in (A - B) = the number of bombs in A - the number of bombs in B
3. optimize game
4. optimize solver
5. write clearer comments
6. set public/private functions for each class
7. change position tuples to space pointers in functions
8. rewrite explosion function
9. add winning notification
10. add losing notification
11. add clues exhausted notification/terminate solver function
12. check for consistencies in class/functions structures
13. delete print statements
14. write a better README
