import ast
import operator
import re
from typing import Tuple


class AlertCalculator:
    """Класс для вычисления для какой суммы сделать уведомления

    >+15%"""
    _message: str
    _instrument: dict
    _comment: str
    _equation_str: str
    _errors: list[str] = []
    _condition: str
    _is_valid: bool

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg
    }

    def __init__(self, message: str, instrument_info: dict):
        """

        :param message: Полученное сообщение, которое нужно распарсить
        :param instrument_info: Объект результат работы get_instrument_info
        """
        self._message = message
        self._instrument = instrument_info
        self._errors = []
        self._entities: dict = {
            'c': instrument_info["price"],
            'm': instrument_info["price_in_portfolio"]
        }
        self._condition: str = ''
        self._is_valid = False

        self._split_message()

    def _split_message(self):
        """Отделяет уравнение от комментация"""
        msg = self._message.split('\n')
        if len(msg) < 2:
            self._comment = ''
        else:
            self._comment = '\n'.join(msg[1:])
        self._equation_str = msg[0]

    def _get_value_present(self, match: re.Match) -> str:
        """Подставляет с учетом процентов"""
        match = match.group()
        return str(float(self._entities[match[0]]) * (float(match[1:-1]) / 100))

    def _is_valid_formula(self, formula: str) -> bool:
        try:
            # Попытка скомпилировать формулу в абстрактное синтаксическое дерево
            tree = ast.parse(formula, mode='eval')
            # Дополнительная проверка на безопасность: только допустимые типы узлов
            for node in ast.walk(tree):
                if not isinstance(node, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Name, ast.Load,
                                         ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd,
                                         ast.Mod)):
                    return False
            return True
        except (SyntaxError, ValueError):
            return False

    def _validate(self):
        equation_str = self._equation_str.replace(' ', '')
        if not (equation_str[0] == '<' or equation_str[0] == '>'):
            self._errors.append('Должно начинаться с < или >')
            return False
        if equation_str[0] == '<':
            self._condition = 'gte'
        else:
            self._condition = 'lte'
        equation_str = equation_str[1:]

        equation_str = equation_str.replace('cur', 'c')
        equation_str = equation_str.replace('me', 'm')
        # Теперь заменить все c и m на соответствующие значения

        equation_str = re.sub(r'[c|m]\d*(\.\d*)?%', self._get_value_present, equation_str)
        equation_str = re.sub(r'\b[mc]\b', lambda x: str(self._entities[x.group()]), equation_str)

        print('stage 1 formula:', equation_str)
        if self._is_valid_formula(equation_str):
            self._is_valid = True
            self._equation_str = equation_str
            return True
        self._errors.append('Формула не валидна')
        return False

    def _infix_to_postfix(self, expression: str) -> str:
        """Обратная польская запись. Копипаст из GPT так как день писать)"""
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
        output = []
        stack = []
        digit = []

        def is_operator(c):
            return c in precedence

        def precedence_of(c):
            return precedence[c]

        for token in expression:
            if token.isdigit() or token == '.':
                # output.append(token)
                digit.append(token)
            else:
                output.append(''.join(digit))
                digit = []
            if token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # Pop the '(' from the stack
            elif is_operator(token):
                while (stack and stack[-1] != '(' and
                       precedence_of(token) <= precedence_of(stack[-1])):
                    output.append(stack.pop())
                stack.append(token)

        output.append(''.join(digit))
        while stack:
            output.append(stack.pop())

        return ' '.join(output)

    def _evaluate_postfix(self, expression: str) -> float:
        stack = []

        def apply_operator(op: str, b: float, a: float):
            if op == '+': return a + b
            if op == '-': return a - b
            if op == '*': return a * b
            if op == '/': return a / b
            if op == '^': return a ** b

        for token in expression.split():
            try:
                stack.append(float(token))
            except:
                b = stack.pop()
                a = stack.pop()
                result = apply_operator(token, b, a)
                stack.append(result)

        return stack[0]

    def _eval(self, node):
        """
        Рекурсивно вычисляет значение AST-узла.

        :param node: AST-узел.
        :return: Результат вычисления.
        """
        if isinstance(node, ast.Num):  # Для числовых констант
            return node.n
        elif isinstance(node, ast.BinOp):  # Для бинарных операций
            left = self._eval(node.left)
            right = self._eval(node.right)
            return self.OPERATORS[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):  # Для унарных операций
            operand = self._eval(node.operand)
            return self.OPERATORS[type(node.op)](operand)
        else:
            raise TypeError(node)

    def validate(self):
        val = self._validate()
        print('errors: ', self._errors)
        print('formula: ', self._equation_str)
        return val

    def calculate(self) -> Tuple[float, str, str]:
        """Записывает в бд"""
        if not self._is_valid:
            return None, None, None
        try:
            return float(self._equation_str), self._comment, self._condition
        except:
            exp = self._infix_to_postfix(self._equation_str)
            print('exp:', exp)
            res = self._evaluate_postfix(exp)
            return res, self._comment, self._condition
