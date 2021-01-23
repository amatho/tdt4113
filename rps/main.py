"""Main"""

import collections
import random
from enum import Enum
import matplotlib.pyplot as plt


class Action(Enum):
    """A valid action in Rock Paper Scissors."""

    ROCK = 0
    SCISSOR = 1
    PAPER = 2

    @staticmethod
    def random():
        """Choose a random action."""
        return Action(random.randint(0, 2))

    def beaten_by(self):
        """Get which action this action is beaten by."""
        return Action((self.value - 1) % 3)

    def __eq__(self, other):
        # pylint: disable=comparison-with-callable
        return self.value == other.value

    def __gt__(self, other):
        return (self.value + 1) % 3 == other.value

    def __lt__(self, other):
        # pylint: disable=comparison-with-callable
        return (other.value + 1) % 3 == self.value

    def __str__(self):
        return str(self.name)

    def __hash__(self):
        return hash(self.value)


class Player:
    """Abstract class for a Rock Paper Scissors player."""

    def select_action(self):
        """Select which action to perform."""
        raise NotImplementedError

    def receive_result(self, their_action):
        """Receive the action of the opposing player."""
        raise NotImplementedError

    def enter_name(self):
        """Return the display name of this player."""
        raise NotImplementedError


class Random(Player):
    """A player who chooses actions randomly."""

    def select_action(self):
        return Action.random()

    def receive_result(self, their_action):
        pass

    def enter_name(self):
        return 'Random'


class Sequential(Player):
    """A player who chooses actions sequentially."""

    index = 0

    def increment(self):
        """Increment the sequence index."""

        self.index = (self.index + 1) % 3

    def select_action(self):
        action = Action(self.index)
        self.increment()
        return action

    def receive_result(self, their_action):
        pass

    def enter_name(self):
        return 'Sequential'


class MostCommmon(Player):
    """A player who uses the opponents most common action to select it's action."""

    counts = {}

    def increase_count(self, action):
        """Increse the count for the given action."""

        if action in self.counts:
            self.counts[action] += 1
        else:
            self.counts[action] = 1

    def most_common_action(self):
        """Find the action with the highest count, return None if no actions have been played."""

        return max(self.counts, key=lambda k: self.counts[k], default=None)

    def select_action(self):
        action = self.most_common_action()
        if action is not None:
            return action.beaten_by()

        return Action.random()

    def receive_result(self, their_action):
        self.increase_count(their_action)

    def enter_name(self):
        return 'Most Common'


class Historian(Player):
    """A player who looks for patterns in the opponents plays.

    The parameter ``remember`` determines the length of the sequence of actions to remember.
    """

    counts = {}

    def __init__(self, remember):
        assert remember > 0
        self.remember = remember + 1
        self.their_last_actions = collections.deque(maxlen=self.remember)

    def increase_count(self, action_tuple):
        """Increase the count for the given sequence of actions."""

        if action_tuple in self.counts:
            self.counts[action_tuple] += 1
        else:
            self.counts[action_tuple] = 1

    def most_common_action(self):
        """Find sequence with the highest count, and return the last action in it.

        Return None if not enough actions have been played, or a matching sequence was not found.
        """

        if len(self.their_last_actions) != self.remember:
            return None

        filter_condition = tuple(self.their_last_actions)[1:]
        counts_starting_with_last_action = filter(
            lambda c: c[:-1] == filter_condition, self.counts)
        sequence = max(counts_starting_with_last_action,
                       key=lambda k: self.counts[k], default=None)

        if sequence is None:
            return None
        return sequence[-1]

    def select_action(self):
        action = self.most_common_action()
        if action is not None:
            return action.beaten_by()

        return Action.random()

    def receive_result(self, their_action):
        self.their_last_actions.append(their_action)
        if len(self.their_last_actions) == self.remember:
            self.increase_count(tuple(self.their_last_actions))

    def enter_name(self):
        return 'Historian (remember={})'.format(self.remember - 1)


class SingleGame:
    """Arrange a single game between to players."""

    class Winner(Enum):
        """The possible winners of a game."""

        P1 = 0
        P2 = 1
        NEITHER = 2

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

        self.player1_action = None
        self.player2_action = None
        self.winner = None

    def perform_game(self):
        """Play the game by selecting actions and notifying players of the chosen actions."""

        if self.winner is not None:
            return

        self.player1_action = self.player1.select_action()
        self.player2_action = self.player2.select_action()

        self.player1.receive_result(self.player2_action)
        self.player2.receive_result(self.player1_action)

        if self.player1_action > self.player2_action:
            self.winner = self.Winner.P1
        elif self.player2_action > self.player1_action:
            self.winner = self.Winner.P2
        else:
            self.winner = self.Winner.NEITHER

    def show_result(self):
        """Print the result of the game."""

        print('P1 {} uses {}. P2 {} uses {}.  -> {} has won!'.format(
            self.player1.enter_name(), self.player1_action,
            self.player2.enter_name(), self.player2_action,
            self.winner.name))


class Tournament:
    """Arrange a tournament between two players, playing a given amount of games."""

    def __init__(self, player1, player2, number_of_games):
        self.player1 = player1
        self.player2 = player2
        self.player1_scores = []
        self.player2_scores = []
        self.number_of_games = number_of_games
        self.games_played = 0

    def arrange_singlegame(self):
        """Arrange a single game."""

        singlegame = SingleGame(self.player1, self.player2)
        singlegame.perform_game()
        singlegame.show_result()

        if singlegame.winner == SingleGame.Winner.P1:
            self.player1_scores.append(1)
            self.player2_scores.append(0)
        elif singlegame.winner == SingleGame.Winner.P2:
            self.player1_scores.append(0)
            self.player2_scores.append(1)
        else:
            self.player1_scores.append(0.5)
            self.player2_scores.append(0.5)

        self.games_played += 1

    def arrange_tournament(self):
        """Arrange a tournament, playing until reaching maximum games."""

        while self.games_played < self.number_of_games:
            self.arrange_singlegame()

        print('P1 {} score: {}\nP2 {} score: {}'.format(
            self.player1.enter_name(), sum(self.player1_scores),
            self.player2.enter_name(), sum(self.player2_scores)))

        x_axis = list(range(1, self.number_of_games + 1))
        plt.plot(x_axis, average_of_previous(self.player1_scores),
                 label='P1 ' + self.player1.enter_name())
        plt.plot(x_axis, average_of_previous(self.player2_scores),
                 label='P2 ' + self.player2.enter_name())
        plt.xlabel('Games played')
        plt.ylabel('Average score')
        plt.legend()
        plt.show()


def average_of_previous(nums):
    """For each value, calculate the average of this value + all previous values."""

    averages = []
    averages.append(nums[0])
    for idx, val in enumerate(nums[1:]):
        previous_average = averages[idx]
        next_average = (previous_average * (idx + 1) + val) / (idx + 2)
        averages.append(next_average)

    return averages


def main():
    """The main method."""

    tournament = Tournament(Historian(2), MostCommmon(), 100)
    tournament.arrange_tournament()


if __name__ == "__main__":
    main()
