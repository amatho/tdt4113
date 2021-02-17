"""Main"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable
import numbers
import numpy as np


class Container(ABC):
    """Abstract container for a collection type."""

    def __init__(self) -> None:
        super().__init__()
        self._items = []

    def __len__(self) -> int:
        """Return the size of the container."""
        return len(self._items)

    def __str__(self) -> str:
        return str(self._items)

    def is_empty(self) -> bool:
        """Check if list is empty."""
        return len(self) == 0

    def clear(self):
        """Clear the items from the container."""
        self._items = []

    @abstractmethod
    def peek(self) -> object:
        """Return the top item without removing it."""


class Stack(Container):
    """A first-in last-out data collection."""

    def pop(self) -> object:
        """Pop off the top item."""
        return self._items.pop()

    def push(self, item: object):
        """Push an item onto the stack."""
        self._items.append(item)

    def peek(self) -> object:
        return self._items[-1]

    def __iter__(self) -> Stack:
        return self

    def __next__(self) -> object:
        if self.is_empty():
            raise StopIteration
        return self.pop()


class Queue(Container):
    """A first-in first-out data collection."""

    def enqueue(self, item):
        """Put an item onto the queue."""
        self._items.append(item)

    def dequeue(self) -> object:
        """Get the first item and remove it from the queue."""
        return self._items.pop(0)

    def peek(self) -> object:
        return self._items[0]

    def __iter__(self) -> Queue:
        return self

    def __next__(self) -> object:
        if self.is_empty():
            raise StopIteration
        return self.dequeue()


class Function:
    # pylint: disable=too-few-public-methods
    """A mathematical unary function."""

    def __init__(self, func: Callable) -> None:
        self.func = func

    def execute(self, element: numbers.Number, debug=False) -> numbers.Number:
        """Execute the function on the given element and return the result."""

        if not isinstance(element, numbers.Number):
            raise TypeError('The element must be a number')
        result = self.func(element)

        if debug is True:
            print(f'Function: {self.func.__name__}({element}) = {result}')

        return result


class Operator:
    # pylint: disable=too-few-public-methods
    """A binary mathematical operation."""

    def __init__(self, operation: Callable, strength: int) -> None:
        self.operation = operation
        self.strength = strength

    def execute(self, num_a: numbers.Number, num_b: numbers.Number) -> numbers.Number:
        """Execute the operator on the given operands and return the result."""

        for operand in num_a, num_b:
            if not isinstance(operand, numbers.Number):
                raise TypeError('The operands must be numbers')

        return self.operation(num_a, num_b)


class Calculator:
    """A simple mathematical calculator."""

    NUMBER_CHARS = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '.'}
    FUNC_OR_OP_CHARS = {}

    def __init__(self) -> None:
        self.functions = {'exp': Function(np.exp),
                          'log': Function(np.log),
                          'sin': Function(np.sin),
                          'cos': Function(np.cos),
                          'sqrt': Function(np.sqrt)}

        self.operators = {'add': Operator(np.add, 0),
                          'sub': Operator(np.subtract, 0),
                          'mul': Operator(np.multiply, 1),
                          'div': Operator(np.divide, 1)}

        self.input_queue = Queue()
        self.output_queue = Queue()

    def parse_text(self, text: str):
        """Parse the given text and put the result on the input queue."""

        self.input_queue.clear()

        index = 0
        while index < len(text):
            if text[index] == ' ':
                index += 1
                continue

            if text[index].isalpha():
                start = index
                while index < len(text) and text[index].isalpha():
                    index += 1
                word = text[start:index].lower()
                if word in self.operators:
                    self.input_queue.enqueue(self.operators[word])
                elif word in self.functions:
                    self.input_queue.enqueue(self.functions[word])
                else:
                    raise TypeError(f'Invalid operator or function `{word}`')

            elif text[index].isdecimal() or text[index] == '-' or text[index] == '.':
                start = index
                while index < len(text) and \
                        (text[index].isdecimal() or text[index] == '-' or text[index] == '.'):
                    index += 1
                num = text[start:index]
                try:
                    num = int(num)
                except TypeError:
                    num = float(num)
                self.input_queue.enqueue(num)

            elif text[index] == '(' or text[index] == ')':
                self.input_queue.enqueue(text[index])
                index += 1

            else:
                raise TypeError(f'Invalid character `{text[index]}`')

    def build_rpn(self):
        """Build a RPN representation on the output queue."""

        self.output_queue.clear()
        op_stack = Stack()

        for elem in self.input_queue:
            if isinstance(elem, numbers.Number):
                self.output_queue.enqueue(elem)
            elif isinstance(elem, Function):
                op_stack.push(elem)
            elif elem == '(':
                op_stack.push(elem)
            elif elem == ')':
                while op_stack.peek() != '(':
                    self.output_queue.enqueue(op_stack.pop())
                op_stack.pop()
            elif isinstance(elem, Operator):
                while not (op_stack.is_empty()
                           or (isinstance(op_stack.peek(), Operator)
                               and op_stack.peek().strength < elem.strength)
                           or op_stack.peek() == '('):
                    self.output_queue.enqueue(op_stack.pop())
                op_stack.push(elem)
            else:
                raise TypeError('Invalid element on the input queue')

        for elem in op_stack:
            self.output_queue.enqueue(elem)

    def eval_rpn(self) -> numbers.Number:
        """Evaluate the RPN representation on the output queue and return the result."""

        stack = Stack()

        for elem in self.output_queue:
            if isinstance(elem, numbers.Number):
                stack.push(elem)
            elif isinstance(elem, Function):
                num = stack.pop()
                res = elem.execute(num)
                stack.push(res)
            elif isinstance(elem, Operator):
                num_b = stack.pop()
                num_a = stack.pop()
                res = elem.execute(num_a, num_b)
                stack.push(res)
            else:
                raise TypeError(
                    f'Invalid element `{elem}` on the output queue')

        assert len(stack) == 1
        return stack.pop()

    def calculate_expression(self, text: str) -> numbers.Number:
        """Calculate the given expression and return the result."""

        self.parse_text(text)
        self.build_rpn()
        return self.eval_rpn()


def main():
    """The main method."""

    calc = Calculator()
    print(calc.calculate_expression('1 add 2 mul 3 div 2'))
    print(calc.calculate_expression('EXP (1 ADD 2 MUL 3)'))
    print(calc.calculate_expression(
        '((15 div (7 sub (1 add 1))) mul 3) sub (2 add (1 add 1))'))


if __name__ == "__main__":
    main()
