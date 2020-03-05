""" A module containing a formulation of the rubiks cube. At the moment, this is only for a 3x3x3 cube but I will be extending this.

Contains three classes that describe different aspects of a cube. Each NxNxN Rubik's Cube is made up of NxNxN cubies which in turns have six faces (some internally facing).

Some methods in this formulation are there to fit the specification of a solving agent.
"""

import numpy as np
import random

# For referencing positive and negative directions later on.
COORDS_1 = [-1, 1]

# Creating positional coordinates for each of the 27 cubies
COORDS_2 = [1, 0, -1]
COORDS_3 = [np.array([-x, y, z]) for z in COORDS_2 for y in COORDS_2 for x in COORDS_2]

SIDES = ["U", "F", "R", "B", "L", "D"]
SIDES_2 = ["Up", "Front", "Right", "Back", "Left", "Down"]

# The normal vector of each sides of the Rubiks cube
NORMS = {"U": np.array([0, 0, 1]), "D": np.array([0, 0, -1]), "F": np.array([0, -1, 0]),
         "B": np.array([0, 1, 0]), "R": np.array([1, 0, 0]), "L": np.array([-1, 0, 0]), }

# Matrices defining clockwise rotations of each side of the cube
C_WISE = {"U": np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]]), "F": np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]]),
          "R": np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]]), "D": np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]]),
          "B": np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]]), "L": np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])}

COLOURS = ["W", "G", "R", "B", "O", "Y"]  # White, Green, Red, Blue, Orange, and Yellow

# OPPOSING_SIDES = {"U": "D", "D": "U", "R": "L", "L": "R", "F": "B", "B": "F"}  # Currently Redundant


class Face:
    """"""
    def __init__(self, norm, colour="Black"):
        self.norm = norm  # The normal vector of the face
        self.colour = colour

    def copy(self):
        """Creates a deep copy of a Face."""
        new = Face(np.array(self.norm[:]), self.colour[:])
        return new

    def __str__(self):
        """String representation of a face."""
        return "Normal:" + str(self.norm) + "\nColour:" + self.colour


class Cubie:
    def __init__(self, coordinates, faces=[]):
        # The cubie's current coordinates in space
        self.coordinates = coordinates
        
        # A list of Face instances
        self.faces = faces

        # Initialising 6 faces for the cubie with norms in x, y, and z directions
        if self.faces == []:
            for i in range(3):
                for j in COORDS_1:
                    # Creates faces with norms in the 6 unit directions
                    norm = np.zeros(3)
                    norm[i] = j
                    self.faces.append(Face(norm))

    def copy(self):
        """Creates a deep copy of a Cubie. For use by operators in creating new states."""
        new_cubie = Cubie(self.coordinates[:])
        new_cubie.faces = [face.copy() for face in self.faces]
        return new_cubie

    def x(self):
        return self.coordinates[0]

    def y(self):
        return self.coordinates[1]

    def z(self):
        return self.coordinates[2]

    def in_side(self, side):
        """Verifies if the Cubie is contained in the side given."""
        if side == "U":
            return self.z() == 1
        if side == "D":
            return self.z() == -1
        if side == "F":
            return self.y() == -1
        if side == "B":
            return self.y() == 1
        if side == "R":
            return self.x() == 1
        if side == "L":
            return self.x() == -1

# Generating a list of cubies with a solved arrangement
SOLVED_CUBIES = [Cubie(np.array([x, y, z])) for x in COORDS_2 for y in COORDS_2 for z in COORDS_2]


class Cube:
    def __init__(self, cubies=SOLVED_CUBIES):
        self.cubies = cubies

        # Initialising cubies with non-black colours on their outward faces
        if cubies == SOLVED_CUBIES:
            for cubie in self.cubies:
                for face in cubie.faces:
                    # Upwards side is white
                    if cubie.z() == 1 and face.norm[2] == 1:
                        face.colour = "W"
                    # Downwards side is yellow
                    if cubie.z() == -1 and face.norm[2] == -1:
                        face.colour = "Y"
                    # Right side is red
                    if cubie.x() == 1 and face.norm[0] == 1:
                        face.colour = "R"
                    # Left side is orange
                    if cubie.x() == -1 and face.norm[0] == -1:
                        face.colour = "O"
                    # Backwards side is green
                    if cubie.y() == 1 and face.norm[1] == 1:
                        face.colour = "G"
                    # Front side is blue
                    if cubie.y() == -1 and face.norm[1] == -1:
                        face.colour = "B"

    def copy(self):
        """Performs a deep copy of a Cube for use in operators in creating new states."""
        new_cubies = [cubie.copy() for cubie in self.cubies]
        new_cube = Cube(new_cubies)
        return new_cube

    def move(self, side, number_of_turns=1):
        """Given a side to turn and the number of time to turn it 90 degrees clockwise, returns a new cube having
        performed this action.
        """
        # Creating a deep copy of the 
        new = self.copy()
        
        turn = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        # Creating a matrix that will perform the desired rotation given the number_of_turns of said side
        for i in range(number_of_turns):
            turn = turn.dot(C_WISE[side])

        # Performing rotation of the coordinates and the norms of its faces for each of the cubies in the side 
        for i, cubie in enumerate(new.cubies):
            if self.cubies[i].in_side(side):
                for j in range(len(cubie.faces)):
                    old_face_norm = self.cubies[i].faces[j].norm
                    cubie.faces[j].norm = old_face_norm.dot(turn)
                cubie.coordinates = self.cubies[i].coordinates.dot(turn)
        return new

    def can_move(self, side, number_of_turns):
        """Required method for an agent. Always True as you can make any turn in any state of a Rubik's cube."""
        return True

    def cube_array(self):
        """Generates a 6 x 3 x 3 list representing the faces of the Rubiks cube."""
        cube_sides = {}

        for side in SIDES:
            cube_sides[side] = []
        
        # Todo Break this loop into helper functions for clarity and simplicity
        for coord in COORDS_3:
            for cubie in self.cubies:
                # Making sure that the cubes cubies are processed in the correct order
                if np.array_equal(cubie.coordinates, coord):  
                    
                    
                    for side in SIDES:
                        if cubie.in_side(side):
                            for face in cubie.faces:
                                
                                # Checking that the face of the cubie has the same norm as the side we are processing
                                if np.array_equal(face.norm, NORMS[side]):
                                    cube_sides[side].append(face.colour)

        new_list = [cube_sides["U"], cube_sides["F"], reversal(cube_sides["R"]), reversal(cube_sides["B"]),
                    cube_sides["L"], reversal(cube_sides["D"])]
        
        final_list = [nine_to_3x3(side) for side in new_list]
        return final_list

    def __str__(self):
        text = ""
        
        # Appends the string representation of each side to text
        for i, side in enumerate(self.cube_array()):
            text += SIDES_2[i] + " side\n"
            for line in side:
                text += str(line) + "\n"
        return text

    def __eq__(self, other):
        # Todo Check that this function works for all cases
        return self.cube_array() == other.cube_array()

#### HELPER FUNCTIONS ####

def reversal(side):
    """Takes a list and reverses every sublist of 3 elements like below:
    [1, 2, 3, 4, 5, 6, 7, 8, 9] becomes [3, 2, 1, 6, 5, 4, 9, 8, 7].
    
    Used for certain sides that are processed incorrectly in .cube_array().
    """
    new_side = []
    k = int(len(side) / 3)  # Only reverses every sublist of 
    
    for i in range(k):
        for j in range(3):
            new_side.append(side[k * i - j + 2])
    return new_side


assert reversal([1, 2, 3, 4, 5, 6, 7, 8, 9]) == [3, 2, 1, 6, 5, 4, 9, 8, 7], "Reversal Fails"


def nine_to_3x3(listy):
    """Reshapes a list of length 9 to a 3 x 3 list."""
    new_side = []
    k = int(len(listy) / 3)
    
    for i in range(k):
        intermediate = []
        for j in range(3):
            intermediate.append(listy.pop(0))
            
        new_side.append(intermediate)
    return new_side


assert nine_to_3x3([1, 2, 3, 4, 5, 6, 7, 8, 9]) == [[1, 2, 3], [4, 5, 6], [7, 8, 9]], "nine_to_3x3 Fails"


#### GOAL TESTING ####
# These methods will be used by a solving agent.

GOAL_CUBE = Cube()  # Since Cube() returns a perfectly solved cube when given no arguments.


# Does not work as .__eq__() Cube method is not properly functioning.
def goal_test(c):
    """Required method for solving agent"""
    return c == GOAL_CUBE


def goal_message(s):
    return "You've solved our rudimentary Rubik's Cube. Great!"


class Operator:
    def __init__(self, name, precond, state_transf):
        self.name = name
        
        self.precond = precond  # Function that checks that preconditions are met for carrying out the move.
        self.state_transf = state_transf

    def possible(self, s):
        return self.precond(s)

    def __call__(self, s):
        return self.state_transf(s)

    def __str__(self):
        return self.name


#### CREATING OPERATORS ####
OPERATORS = []
turns_90 = [1, 3]  # Clockwise and Anticlockwise turns
# turns_90_180 = [1, 2, 3]  # Uncomment if you would like to add half turns.

# Creating operators for the turning of any specifced side.
for i in turns_90:
    for side in SIDES:
        op = Operator("Turns the " + str(side) + " side clockwise of the cube " + str(i) + " times",
                      lambda c, side1=side, j=i: c.can_move(side1, j),
                      lambda c, side1=side, j=i: c.move(side1, j))
        OPERATORS.append(op)

def scramble(cube, turn_number, show_turns=False):
    """Returns a Cube that has be randomly scrambled by turn_number turns."""
    for i in range(turn_number):
        action = random.choice(OPERATORS)
        if show_turns:
            print()
            print(action)
        new_c = action(cube)
        cube = new_c
    return cube


#### INITIALISE A STARTING SCRAMBLED STATE ####
INITIAL_STATE = scramble(GOAL_CUBE, 30)
