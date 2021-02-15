import numpy as np
from main import Calculator, Function, Operator, Queue, Stack


def test_queue():
    print('Queue.enqueue() 1, 3, 5, 7')
    queue = Queue()
    queue.enqueue(1)
    queue.enqueue(3)
    queue.enqueue(5)
    queue.enqueue(7)

    print('Queue.dequeue() loop')
    for item in queue:
        print('Item: %s Len: %d' % (item, len(queue)))


def test_stack():
    print('Stack.push() 1, 3, 5, 7')
    stack = Stack()
    stack.push(1)
    stack.push(3)
    stack.push(5)
    stack.push(7)

    print('Stack.pop() loop')
    for item in stack:
        print('Item: %s Len: %d' % (item, len(stack)))


def test_func():
    print('Testing Function')
    exp = Function(np.exp)
    sin = Function(np.sin)
    exp.execute(sin.execute(3.14 / 2))


def test_operator():
    print('Testing Operator')
    add_op = Operator(operation=np.add, strength=0)
    mul_op = Operator(operation=np.multiply, strength=1)
    res = add_op.execute(1, mul_op.execute(2, 3))
    print(f'1 + 2 * 3 = {res}')


def test_parse_text():
    print('Testing Calculator.parse_text()')
    calc = Calculator()
    calc.parse_text('exp (1 add 2 mul 3)')
    print(calc.input_queue)


def test_build_rpn():
    print('Testing Calculator.build.rpn()')
    calc = Calculator()
    calc.input_queue.enqueue(calc.functions['exp'])
    calc.input_queue.enqueue('(')
    calc.input_queue.enqueue(1)
    calc.input_queue.enqueue(calc.operators['add'])
    calc.input_queue.enqueue(2)
    calc.input_queue.enqueue(calc.operators['mul'])
    calc.input_queue.enqueue(3)
    calc.input_queue.enqueue(')')
    calc.build_rpn()
    print(calc.output_queue)


def test_eval_rpn():
    print('Testing Calculator.eval_rpn()')
    calc = Calculator()
    calc.output_queue.enqueue(1)
    calc.output_queue.enqueue(2)
    calc.output_queue.enqueue(3)
    calc.output_queue.enqueue(calc.operators['mul'])
    calc.output_queue.enqueue(calc.operators['add'])
    calc.output_queue.enqueue(calc.functions['exp'])
    print(f'RPN Evualation: {calc.eval_rpn()}')


def test_calculate_expression():
    print('Testing Calculator.calculate_expression()')
    calc = Calculator()
    print(f"Result = {calc.calculate_expression('exp(1 add 2 mul 3)')}")


test_queue()
test_stack()
test_func()
test_operator()
test_parse_text()
test_build_rpn()
test_eval_rpn()
test_calculate_expression()
