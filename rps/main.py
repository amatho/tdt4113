"""Main"""

import random
from enum import Enum


class Action(Enum):
    ROCK = 0
    SCISSOR = 1
    PAPER = 2

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return (self.value + 1) % 3 == other.value

    def __lt__(self, other):
        return (other.value + 1) % 3 == self.value

    def __str__(self):
        return str(self.name)


class Player:
    def select_action(self):
        raise NotImplementedError

    def receive_result(self):
        raise NotImplementedError

    def enter_name(self):
        raise NotImplementedError



class Random(Player):
    def select_action(self):
        pass

def main():
    print(Action.PAPER == Action.PAPER)


if __name__ == "__main__":
    main()
