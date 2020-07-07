import random
import sqlite3


def luhn_algorithm(number: str) -> bool:
    temp_number = [int(item) for item in number]
    last_number = temp_number.pop(len(temp_number) - 1)

    for i in range(len(temp_number)):
        if i % 2 == 0:
            temp_number[i] *= 2
        if temp_number[i] > 9:
            temp_number[i] -= 9

    if (sum(temp_number) + last_number) % 10 != 0:
        return False
    else:
        return True


class Card:
    def __init__(self, number='', pin='', balance=0):
        self.number = number
        self.pin = pin
        self.balance = balance

    @staticmethod
    def generate_number() -> str:
        number_generator = random.Random()
        number_generator.seed()
        number = [4, 0, 0, 0, 0, 0]

        for _ in range(9):
            number.append(number_generator.choice(range(10)))

        number = ''.join([str(item) for item in number])
        last_number = 0
        while not luhn_algorithm(number + str(last_number)):
            last_number += 1
            if last_number > 9:
                last_number = 0

        return number + str(last_number)

    @staticmethod
    def generate_pin() -> str:
        pin_generator = random.Random()
        pin_generator.seed()

        return ''.join([str(pin_generator.choice(range(10))) for _ in range(4)])

    def generate_card(self):
        self.number = self.generate_number()
        self.pin = self.generate_pin()

    def update(self, number, pin, balance=0):
        self.__init__(number, pin, balance)


class CardDB:
    def __init__(self):
        self.connect = sqlite3.connect('card.s3db')
        self.cursor = self.connect.cursor()
        self.create()

    def create(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS card (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                number TEXT, pin TEXT, balance INTEGER DEFAULT 0
            );
        ''')

    def insert(self, card: Card):
        self.cursor.execute(f'INSERT INTO card (number, pin, balance) VALUES (?, ?, ?)',
                            (card.number, card.pin, card.balance))
        self.connect.commit()

    def is_exist(self, number):
        self.cursor.execute(f"SELECT EXISTS(SELECT 1 FROM card WHERE number = '{number}')")
        if self.cursor.fetchone():
            return True
        else:
            return False

    def get_card(self, card: Card, number):
        self.cursor.execute(f"SELECT number, pin, balance FROM card WHERE number = '{number}'")
        item = self.cursor.fetchone()
        if item:
            card.__init__(item[0], item[1], item[2])
            return True
        else:
            return False

    def update_balance(self, number, money):
        self.cursor.execute(f'''
            UPDATE card
            SET 
                balance = balance + '{money}'
            WHERE 
                number = '{number}'
        ''')
        self.connect.commit()

    def delete_card(self, number):
        self.cursor.execute(f"DELETE FROM card WHERE number = '{number}'")
        self.connect.commit()

    def get_all(self):
        self.cursor.execute('SELECT * FROM card')
        records = self.cursor.fetchall()
        for row in records:
            print(f'{row[0]} {row[1]} {row[2]} {row[3]}')

    def close(self):
        self.connect.close()


class MenuEngine:
    def __init__(self):
        self.card = Card()
        self.db = CardDB()

    def create(self):
        self.card.generate_card()
        self.db.insert(self.card)
        print("Your card has been created\n")
        print("Your card number:\n"
              f"{self.card.number}\n"
              "Your card PIN:\n"
              f"{self.card.pin}\n")

    def login(self):
        number = input("Enter your card number:\n")
        pin = input("Enter your PIN:\n")

        if self.db.get_card(self.card, number):
            if self.card.pin == pin:
                print("You have successfully logged in!\n")
                self.sub_menu()
            else:
                print("Wrong card number or PIN!\n")
        else:
            print("Wrong card number or PIN!\n")

    def income(self):
        income = int(input("Enter income:\n"))
        self.card.balance += income
        self.db.update_balance(self.card.number, income)
        print("Income was added!")

    def delete_card(self):
        self.db.delete_card(self.card.number)
        print("The account has been closed!\n")

    def transfer(self):
        print("Transfer\n")
        transfer_number = input("Enter card number:\n")
        transfer_card = Card(transfer_number)
        if not luhn_algorithm(transfer_number):
            print('Probably you made mistake in the card number. Please try again!\n')
        elif not self.db.get_card(transfer_card, transfer_number):
            print('Such a card does not exist.\n')
        else:
            money = int(input("Enter how much money you want to transfer:\n"))
            if money > self.card.balance:
                print("Not enough money!")
            else:
                transfer_card.balance += money
                self.card.balance -= money
                self.db.update_balance(transfer_number, money)
                self.db.update_balance(self.card.number, -money)
                print("Success!")

    def sub_menu(self):
        while True:
            print("1. Balance\n"
                  "2. Add income\n"
                  "3. Do transfer\n"
                  "4. Close account\n"
                  "5. Log out\n"
                  "0. Exit\n")
            choice = input()
            if choice == '1':
                print(f"Balance: {self.card.balance}")
            if choice == '2':
                self.income()
            if choice == '3':
                self.transfer()
            if choice == '4':
                self.delete_card()
                break
            if choice == '5':
                break
            if choice == '0':
                self.close()

    def close(self):
        print("Bye!")
        self.db.close()
        exit(1)

    def run(self):
        while True:
            print("1. Create an account\n"
                  "2. Log into account\n"
                  "0. Exit\n")
            choice = input()
            if choice == '1':
                self.create()
            if choice == '2':
                self.login()
            if choice == '3':
                self.db.get_all()
            if choice == '0':
                self.close()


if __name__ == "__main__":
    menu = MenuEngine()
    menu.run()
