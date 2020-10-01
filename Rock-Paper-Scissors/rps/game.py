from typing import List
import random
import os


# noinspection PyTypeChecker
class RockPaperScissors:
    def __init__(self):
        self.rating_path = "./rating.txt"
        self.rating = {}
        self.user_name = ""
        self.user_rating = 0
        self.options = ["rock", "paper", "scissors"]

        self.read_rating()

    def read_rating(self):
        if os.stat(self.rating_path).st_size != 0:
            with open(self.rating_path, 'r') as data:
                for line in data:
                    item: List[str, int] = line.split()
                    self.rating.update({item[0]: item[1]})

    def init_user(self, name):
        self.user_name = name
        if name in self.rating:
            self.user_rating = self.rating[name]
        else:
            self.user_rating = 0

    def get_user_name(self):
        self.init_user(input("Enter your name:"))
        print(f"Hello, {self.user_name}")

    def game_process(self, user_option):
        computer_option = random.choice(self.options)
        computer_index = self.options.index(computer_option)
        user_index = self.options.index(user_option)

        if user_index > computer_index:
            user_index -= len(self.options)

        if computer_option == user_option:
            print(f"There is a draw ({computer_option})")
            self.user_rating += 50
        elif computer_index - user_index <= len(self.options) // 2:
            print(f"Sorry, but computer chose {computer_option}")
        else:
            print(f"Well done. Computer chose {computer_option} and failed")
            self.user_rating += 100

    def end_game_process(self):
        rating_file = open(self.rating_path, 'a')
        rating_file.write(f"{self.user_name} {self.user_rating}\n")
        rating_file.close()
        print("Bye!")

    def get_options(self):
        options = input()
        if len(options) > 0:
            self.options = options.split(',')

        print("Okay, let's start")

    def run(self):
        self.get_user_name()
        self.get_options()

        while True:
            user_input = input()
            if user_input == "!exit":
                break
            elif user_input == "!rating":
                print(f"Your rating: {self.user_rating}")
            elif user_input in self.options:
                self.game_process(user_input)
            else:
                print("Invalid input")

        self.end_game_process()


game = RockPaperScissors()
game.run()
