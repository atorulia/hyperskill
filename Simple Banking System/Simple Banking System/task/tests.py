from hstest.test_case import CheckResult
from hstest.stage_test import StageTest, WrongAnswerException
from hstest.test_case import TestCase
from shutil import copy2
import sqlite3
import random
import re
import os

card_number = ''
pin = ''
second_card_number = ''
second_pin = ''
are_all_inputs_read = False
db_file_name = 'card.s3db'
temp_db_file_name = 'temp.s3db'


def get_credentials(output: str, count=0):
    number = re.findall(r'400000\d{10}', output, re.MULTILINE)
    if not number:
        raise WrongAnswerException('You are printing the card number incorrectly. '
                                   'The card number should look like in the example: 400000DDDDDDDDDD, where D is a digit.')

    PIN = re.findall(r'^\d{4}$', output, re.MULTILINE)
    if not PIN:
        raise WrongAnswerException('You are printing the card PIN incorrectly. '
                                   'The PIN should look like in the example: DDDD, where D is a digit.')
    if count == 2:
        return (number[0], PIN[0]), (number[1], PIN[1])
    else:
        return number[0], PIN[0]


def test_card_generation(output: str, value_to_return):
    global card_number, pin, are_all_inputs_read
    are_all_inputs_read = False
    credentials = get_credentials(output)
    card_number = credentials[0]
    pin = credentials[1]
    return value_to_return


def test_difference_between_generations(output: str, value_to_return):
    global card_number, pin, are_all_inputs_read
    credentials = get_credentials(output)
    another_card_number = credentials[0]

    if another_card_number == card_number:
        return CheckResult.wrong('Your program generates two identical card numbers!')
    are_all_inputs_read = True

    return value_to_return


def test_sign_in_with_correct_credentials(output: str, value_to_return):
    global card_number, pin
    return '{}\n{}'.format(card_number, pin)


def test_output_after_correct_sign_in(output: str, value_to_return):
    global are_all_inputs_read
    are_all_inputs_read = True
    if 'successfully' not in output.lower():
        return CheckResult.wrong(
            'There is no \'successfully\' in your output after signing in with correct credentials')
    return value_to_return


def test_sign_in_with_wrong_pin(output: str, value_to_return):
    global card_number, pin
    wrong_pin = pin
    while pin == wrong_pin:
        wrong_pin = ''.join(list(map(str, random.sample(range(1, 10), 4))))
    return '{}\n{}\n'.format(card_number, wrong_pin)


def test_output_after_wrong_pin(output: str, value_to_return):
    global are_all_inputs_read
    are_all_inputs_read = True
    if 'wrong' not in output.lower():
        return CheckResult.wrong(
            'There is no \'wrong\' in your output after signing in with correct credentials')
    return value_to_return


def test_sign_in_with_wrong_card_number(output: str, value_to_return):
    global card_number, pin
    wrong_card_number = card_number
    while wrong_card_number == card_number:
        temp = [4, 0, 0, 0, 0, 0]
        for _ in range(10):
            temp.append(random.randint(1, 9))
        wrong_card_number = ''.join(list(map(str, temp)))
    return '{}\n{}\n'.format(wrong_card_number, pin)


def test_output_after_wrong_card_number(output: str, value_to_return):
    global are_all_inputs_read
    are_all_inputs_read = True
    if 'wrong' not in output.lower():
        return CheckResult.wrong(
            'There is no \'wrong\' in your output after signing in with correct credentials')
    return value_to_return


def is_passed_luhn_algorithm(number):
    luhn = [int(char) for char in str(number)]
    for i, num in enumerate(luhn):
        if (i + 1) % 2 == 0:
            continue
        temp = num * 2
        luhn[i] = temp if temp < 10 else temp - 9
    return sum(luhn) % 10 == 0


def test_luhn_algorithm(output: str, value_to_return):
    global are_all_inputs_read

    numbers = re.findall(r'400000\d{10}', output, re.MULTILINE)

    for number in numbers:
        if not is_passed_luhn_algorithm(number):
            return CheckResult.wrong('The card number \'{}\' doesn\'t pass luhn algorithm!'.format(number))

    are_all_inputs_read = True
    return '0'


def check_db(output: str, value_to_return):
    if not os.path.exists(db_file_name):
        return CheckResult.wrong('Can\'t find db file named \'{}\''.format(db_file_name))
    try:
        copy2(db_file_name, temp_db_file_name)
    except Exception:
        return CheckResult.wrong('Can\'t copy database file!')

    try:
        with sqlite3.connect(db_file_name) as db:
            response = db.execute(
                'SELECT name FROM sqlite_master WHERE type = \'table\' AND name NOT LIKE \'sqlite_%\';')
            for _ in response.fetchall():
                if 'card' in _:
                    break
            else:
                return CheckResult.wrong('Your database doesn\'t have a table named \'card\'')
    except Exception as exp:
        return CheckResult.wrong('Can\'t connect to the database!')

    correct_columns = (('ID', 'INTEGER'), ('NUMBER', 'TEXT'), ('PIN', 'TEXT'), ('BALANCE', 'INTEGER'))

    try:
        with sqlite3.connect(db_file_name) as db:
            response = db.execute('PRAGMA table_info(card);')
            real_columns = response.fetchall()
            for correct_column in correct_columns:
                for real_column in real_columns:
                    real_column = [str(element).upper() for element in real_column]
                    if correct_column[0] in real_column and correct_column[1] in real_column:
                        break
                else:
                    return CheckResult.wrong('Your table should have columns described in the stage instructions.\n'
                                             'Make sure you use INTEGER type not INT.')
    except Exception:
        return CheckResult.wrong('Can\'t connect to the database!')

    return CheckResult.correct()


def check_db_rows(output: str, value_to_return):
    numbers = re.findall(r'400000\d{10}', output, re.MULTILINE)

    with sqlite3.connect(db_file_name) as db:
        rows = db.execute('SELECT * FROM card').fetchall()
        for number in numbers:
            is_found = False
            for row in rows:
                if number in row:
                    is_found = True
            if not is_found:
                return CheckResult.wrong('Your database doesn’t save newly created cards.\n'
                                         'Make sure you commit your DB changes right after saving a new card in the database!')
    return CheckResult.correct()


def test_add_income(output: str, value_to_return):
    global card_number, pin, are_all_inputs_read
    are_all_inputs_read = False
    credentials = get_credentials(output)
    card_number = credentials[0]
    pin = credentials[1]
    return '2\n{}\n{}\n2\n10000'.format(card_number, pin)


def test_second_add_income(output: str, value_to_return):
    global card_number
    expected_balance = 10000
    with sqlite3.connect(db_file_name) as db:
        result = db.execute('SELECT * FROM card WHERE number = {}'.format(card_number)).fetchone()
        balance = result[3]
        if balance != expected_balance:
            return CheckResult.wrong(
                'Account balance is wrong after adding income. Expected {}'.format(expected_balance))
    return '2\n15000'


def test_balance_after_second_income(output: str, value_to_return):
    global card_number, are_all_inputs_read
    expected_balance = 25000
    with sqlite3.connect(db_file_name) as db:
        result = db.execute('SELECT * FROM card WHERE number = {}'.format(card_number)).fetchone()
        balance = result[3]
        if balance != expected_balance:
            return CheckResult.wrong(
                'Account balance is wrong after adding income. Expected {}'.format(expected_balance))
    are_all_inputs_read = True
    return value_to_return


def test_transfer(output: str, value_to_return):
    global card_number, pin, second_card_number, second_pin, are_all_inputs_read
    are_all_inputs_read = False
    credentials = get_credentials(output, count=2)
    card_number, pin = credentials[0]
    second_card_number, second_pin = credentials[1]
    doesnt_pass_luhn = 4000003972196502
    return '2\n{}\n{}\n3\n{}'.format(card_number, pin, doesnt_pass_luhn)


def test_transfer_doesnt_pass_luhn(output: str, value_to_return):
    if 'mistake'.lower() not in output.lower():
        return CheckResult.wrong('You should not allow to transfer to a card number that doesn\'t pass '
                                 'the Luhn algorithm.\n Instead output \'{}\''.format(
            'Probably you made mistake in card number. Please try again!'))
    doesnt_exist_card = 3000003972196503
    return '3\n{}'.format(doesnt_exist_card)


def test_transfer_doesnt_exist_card(output: str, value_to_return):
    global second_card_number
    if 'not exist' not in output.lower():
        return CheckResult.wrong('You should not allow to transfer to a card number that does not exist.'
                                 '\nYpu should print \'{}\''.format('Such a card does not exist.'))
    return '3\n{}\n10000'.format(second_card_number)


def test_transfer_not_enough_money(output: str, value_to_return):
    global second_card_number
    if 'not enough money' not in output.lower():
        return CheckResult.wrong('You should not allow a transfer if there is not enough money '
                                 'in the account to complete it.\n')
    return '2\n20000\n3\n{}\n10000'.format(second_card_number)


def test_balance_after_transfer(output: str, value_to_return):
    global card_number, second_card_number, are_all_inputs_read
    with sqlite3.connect(db_file_name) as db:
        first = db.execute('SELECT * FROM card WHERE number = {}'.format(card_number)).fetchone()
        second = db.execute('SELECT * FROM card WHERE number = {}'.format(second_card_number)).fetchone()
        first_balance = first[3]
        second_balance = second[3]
        if first_balance != 10000:
            return CheckResult.wrong('Incorrect account balance of the card used to make the transfer.')
        if second_balance != 10000:
            return CheckResult.wrong('Incorrect account balance of the card to which the transfer was made.')
    are_all_inputs_read = True
    return '0'


def test_closing_account(output: str, value_to_return):
    global card_number, pin, are_all_inputs_read
    are_all_inputs_read = False
    credentials = get_credentials(output)
    card_number, pin = credentials[0], credentials[1]
    return '2\n{}\n{}\n4'.format(card_number, pin)


def test_rows_after_closing_account(output: str, value_to_return):
    global card_number, are_all_inputs_read
    with sqlite3.connect(db_file_name) as db:
        rows = db.execute('SELECT * FROM card WHERE number = \'{}\''.format(card_number)).fetchall()
        if rows:
            return CheckResult.wrong('After closing an account, the card number should be deleted from the database.')
    are_all_inputs_read = True
    return value_to_return


class BankingSystem(StageTest):

    def generate(self):
        return [
            TestCase(
                stdin='0',
                check_function=check_db,
            ),
            TestCase(
                stdin=[
                    '1',
                    lambda output: test_card_generation(output, '1'),
                    lambda output: test_difference_between_generations(output, '0')
                ]),
            TestCase(
                stdin='1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n0',
                check_function=check_db_rows
            ),
            TestCase(
                stdin=[
                    '1',
                    lambda output: test_card_generation(output, '2'),
                    lambda output: test_sign_in_with_correct_credentials(output, None),
                    lambda output: test_output_after_correct_sign_in(output, '0')
                ]),
            TestCase(
                stdin=[
                    '1',
                    lambda output: test_card_generation(output, '2'),
                    lambda output: test_sign_in_with_wrong_pin(output, None),
                    lambda output: test_output_after_wrong_pin(output, '0')
                ]),
            TestCase(
                stdin=[
                    '1',
                    lambda output: test_card_generation(output, '2'),
                    lambda output: test_sign_in_with_wrong_card_number(output, None),
                    lambda output: test_output_after_wrong_card_number(output, '0')
                ]),
            TestCase(
                stdin=[
                    '1\n1\n1\n1\n1\n1\n1\n1',
                    lambda output: test_luhn_algorithm(output, '0'),
                ]),
            TestCase(
                stdin=[
                    '1',
                    lambda output: test_add_income(output, None),
                    lambda output: test_second_add_income(output, None),
                    lambda output: test_balance_after_second_income(output, '0'),
                ]),
            TestCase(
                stdin=[
                    '1\n1',
                    lambda output: test_transfer(output, None),
                    lambda output: test_transfer_doesnt_pass_luhn(output, None),
                    lambda output: test_transfer_doesnt_exist_card(output, None),
                    lambda output: test_transfer_not_enough_money(output, None),
                    lambda output: test_balance_after_transfer(output, None),
                ]),
            TestCase(
                stdin=[
                    '1',
                    lambda output: test_closing_account(output, None),
                    lambda output: test_rows_after_closing_account(output, '0')
                ]
            )
        ]

    def check(self, reply: str, attach) -> CheckResult:
        if are_all_inputs_read:
            return CheckResult.correct()
        else:
            return CheckResult.wrong('You didn\'t read all inputs!')

    def after_all_tests(self):
        if os.path.exists('temp.s3db'):
            copy2('temp.s3db', 'card.s3db')
            os.remove('temp.s3db')


if __name__ == '__main__':
    BankingSystem('banking.banking').run_tests()
