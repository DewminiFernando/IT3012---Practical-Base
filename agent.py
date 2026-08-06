# agent.py
import random
class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)

class SimpleReflexAgent:
    def sense_and_act(self, percept):
        # Rule 1: IF food is in the current cell, THEN suck
        if percept.get("food_here", False):
            return "Suck"

        # Rule 2: IF there is a wall ahead, THEN turn left
        if percept.get("wall_ahead", False):
            return "TurnLeft"

        # Rule 3: ELSE move forward
        return "MoveForward"

class ModelBasedAgent:
    def __init__(self):
        # Internal memory
        self.visited_cells = {(0, 0)}
        self.blocked_cells = set()

        # Agent's estimated internal state
        self.position = (0, 0)
        self.facing = "Up"

        # Previous information
        self.last_action = None
        self.last_percept = None

    def sense_and_act(self, percept):
        directions = ["Up", "Right", "Down", "Left"]

        offsets = {
            "Up": (0, 1),
            "Right": (1, 0),
            "Down": (0, -1),
            "Left": (-1, 0)
        }

        # ---------------------------------
        # 1. Update internal state
        # ---------------------------------

        # Update facing direction using the previous action
        if self.last_action == "TurnLeft":
            current_index = directions.index(self.facing)
            self.facing = directions[(current_index - 1) % 4]

        elif self.last_action == "TurnRight":
            current_index = directions.index(self.facing)
            self.facing = directions[(current_index + 1) % 4]

        # Update estimated position after a successful forward movement
        elif (
            self.last_action == "MoveForward"
            and self.last_percept is not None
            and not self.last_percept["wall_ahead"]
        ):
            dx, dy = offsets[self.facing]

            self.position = (
                self.position[0] + dx,
                self.position[1] + dy
            )

        # Remember the current cell
        self.visited_cells.add(self.position)

        # Sensor model: remember the wall detected ahead
        if percept["wall_ahead"]:
            dx, dy = offsets[self.facing]

            blocked_position = (
                self.position[0] + dx,
                self.position[1] + dy
            )

            self.blocked_cells.add(blocked_position)

        # ---------------------------------
        # 2. Condition-action rules
        # ---------------------------------

        if percept["food_here"]:
            action = "Suck"

        elif percept["wall_ahead"]:
            current_index = directions.index(self.facing)

            left_direction = directions[(current_index - 1) % 4]
            right_direction = directions[(current_index + 1) % 4]

            left_dx, left_dy = offsets[left_direction]
            right_dx, right_dy = offsets[right_direction]

            left_position = (
                self.position[0] + left_dx,
                self.position[1] + left_dy
            )

            right_position = (
                self.position[0] + right_dx,
                self.position[1] + right_dy
            )

            # IF wall ahead AND left side was visited/blocked,
            # THEN turn right
            if (
                left_position in self.visited_cells
                or left_position in self.blocked_cells
            ):
                action = "TurnRight"
            else:
                action = "TurnLeft"

        else:
            dx, dy = offsets[self.facing]

            forward_position = (
                self.position[0] + dx,
                self.position[1] + dy
            )

            # Avoid repeatedly visiting the same forward cell
            if forward_position in self.visited_cells:
                action = "TurnRight"
            else:
                action = "MoveForward"

        # Store current information for the next step
        self.last_action = action
        self.last_percept = percept.copy()

        return action