from hstest.stage_test import *
from hstest.test_case import TestCase
from enum import Enum
from typing import List, Optional
from copy import deepcopy

CheckResult.correct = lambda: CheckResult(True, '')
CheckResult.wrong = lambda feedback: CheckResult(False, feedback)


class FieldState(Enum):
    X = 'X'
    O = 'O'
    FREE = ' '


def get_state(symbol):
    if symbol == 'X':
        return FieldState.X
    elif symbol == 'O':
        return FieldState.O
    elif symbol == ' ' or symbol == '_':
        return FieldState.FREE
    else:
        return None


class TicTacToeField:

    def __init__(self, *, field: str = '', constructed=None):

        if constructed is not None:
            self.field = deepcopy(constructed)

        else:
            self.field: List[List[Optional[FieldState]]] = [
                [None for _ in range(3)] for _ in range(3)
            ]

            for row in range(3):
                for col in range(3):
                    index = (2 - row) * 3 + col
                    self.field[row][col] = get_state(field[index])

    def equal_to(self, other) -> bool:
        for i in range(3):
            for j in range(3):
                if self.field[i][j] != other.field[i][j]:
                    return False
        return True

    def has_next_as(self, other) -> bool:
        improved: bool = False
        for i in range(3):
            for j in range(3):
                if self.field[i][j] != other.field[i][j]:
                    if self.field[i][j] == FieldState.FREE and not improved:
                        improved = True
                    else:
                        return False
        return improved

    def differ_by_one(self, other) -> bool:
        have_single_difference = False
        for i in range(3):
            for j in range(3):
                if self.field[i][j] != other.field[i][j]:
                    if have_single_difference:
                        return False
                    have_single_difference = True
        return have_single_difference

    def is_close_to(self, other) -> bool:
        return (
            self.equal_to(other)
            or self.has_next_as(other)
            or other.has_next_as(self)
        )

    @staticmethod
    def parse(field_str: str):

        lines = field_str.splitlines()
        lines = [i.strip() for i in lines]
        lines = [i for i in lines if
                 i.startswith('|') and i.endswith('|')]

        for line in lines:
            if len(line) != 9:
                raise WrongAnswerException(
                    f"Line of Tic-Tac-Toe field should be 9 characters long\n"
                    f"found {len(line)} characters in \"{line}\"")
            for c in line:
                if c not in 'XO|_ ':
                    return None

        field: List[List[Optional[FieldState]]] = [
            [None for _ in range(3)] for _ in range(3)
        ]

        y: int = 2

        for line in lines:
            cols = line[2], line[4], line[6]
            x: int = 0
            for c in cols:
                state = get_state(c)
                if state is None:
                    return None
                field[y][x] = state
                x += 1
            y -= 1

        return TicTacToeField(constructed=field)

    @staticmethod
    def parse_all(output: str):
        fields = []

        lines = output.splitlines()
        lines = [i.strip() for i in lines]
        lines = [i for i in lines if len(i) > 0]

        candidate_field = ''
        inside_field = False
        for line in lines:
            if '----' in line and not inside_field:
                inside_field = True
                candidate_field = ''
            elif '----' in line and inside_field:
                field = TicTacToeField.parse(candidate_field)
                if field is not None:
                    fields += [field]
                inside_field = False

            if inside_field and line.startswith('|'):
                candidate_field += line + '\n'

        return fields


class TicTacToeTest(StageTest):
    def generate(self) -> List[TestCase]:
        tests: List[TestCase] = [
            TestCase(stdin="XXXOO__O_", attach=("XXXOO__O_", "X wins")),
            TestCase(stdin="XOXOXOXXO", attach=("XOXOXOXXO", "X wins")),
            TestCase(stdin="XOOOXOXXO", attach=("XOOOXOXXO", "O wins")),
            TestCase(stdin="XOXOOXXXO", attach=("XOXOOXXXO", "Draw")),
            TestCase(stdin="XO_OOX_X_", attach=("XO_OOX_X_", "Game not finished")),
            TestCase(stdin="XO_XO_XOX", attach=("XO_XO_XOX", "Impossible")),
            TestCase(stdin="_O_X__X_X", attach=("_O_X__X_X", "Impossible")),
            TestCase(stdin="_OOOO_X_X", attach=("_OOOO_X_X", "Impossible"))
        ]
        return tests

    def check(self, reply: str, attach: str) -> CheckResult:

        clue_input, clue_result = attach

        fields = TicTacToeField.parse_all(reply)

        if len(fields) == 0:
            return CheckResult.wrong(
                "Can't parse the field! "
                "Check if you output a field "
                "in format like in the example."
            )

        if len(fields) > 1:
            return CheckResult.wrong(
                "There are more than one field in the output! "
                "You should output a single field."
            )

        user_field = fields[0]
        input_field = TicTacToeField(field=clue_input)

        if not user_field.equal_to(input_field):
            return CheckResult.wrong(
                "Your field doesn't match expected field"
            )

        lines = reply.splitlines()
        lines = [i.strip() for i in lines]
        lines = [i for i in lines if len(i) > 0]

        last_line = lines[-1]

        outcomes = [
            "X wins",
            "O wins",
            "Draw",
            "Game not finished",
            "Impossible"
        ]

        if last_line not in outcomes:
            return CheckResult.wrong(
                "Can't parse result, "
                "should be one of the outcomes mentioned in description. "
                "\nYour last line: \"" + last_line + "\""
            )

        if last_line != clue_result:
            return CheckResult.wrong(
                "The result is incorrect. " +
                "\nShould be: \"" + clue_result + "\", " +
                "\nfound: \"" + last_line + "\". " +
                "\nCheck if your program works correctly "
                "in test examples in description."
            )

        return CheckResult.correct()


if __name__ == '__main__':
    TicTacToeTest('tictactoe.tictactoe').run_tests()
