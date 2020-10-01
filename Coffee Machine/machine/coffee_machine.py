# Start machine resources
coffee_machine = {
    "water": 400,
    "milk": 540,
    "coffee beans": 120,
    "disposable cups": 9,
    "money": 550
}


# Reources used for one cup of ...
espresso = {
    "water": 250,
    "coffee beans": 16,
    "disposable cups": 1,
    "money": -4
}

latte = {
    "water": 350,
    "milk": 75,
    "coffee beans": 20,
    "disposable cups": 1,
    "money": -7
}

cappuccino = {
    "water": 200,
    "milk": 100,
    "coffee beans": 12,
    "disposable cups": 1,
    "money": -6
}


# Display machine status
def coffee_machine_status():
    print(r"""The coffee machine has:
             {water} of water
             {milk} of milk
             {coffee beans} of coffee beans
             {disposable cups} of disposable cups
             ${money} of money
             """.format(**coffee_machine))

    
# Coffee machine engine
class MakeCoffee:
    def __init__(self):
        self.coffee_type = None
        self.is_make_coffee = True
        self.coffee_list = [espresso, latte, cappuccino]

    def cook(self, coffee_type):
        self.coffee_type = int(coffee_type) - 1
        for item in self.coffee_list[self.coffee_type]:
            if self.coffee_list[self.coffee_type][item] > coffee_machine[item]:
                print("Sorry, not enough {}!".format(item))
                self.is_make_coffee = False
                break
        if self.is_make_coffee:
            print("I have enough resources, making you a coffee!")
            for item in self.coffee_list[self.coffee_type]:
                coffee_machine[item] -= self.coffee_list[self.coffee_type][item]

                
# Restore machine resources
def get_fill():
    print("Write how many ml of water do you want to add:")
    coffee_machine["water"] += int(input())
    print("Write how many ml of milk do you want to add:")
    coffee_machine["milk"] += int(input())
    print("Write how many grams of coffee beans do you want to add:\n")
    coffee_machine["coffee beans"] += int(input())
    print("Write how many disposable cups of coffee do you want to add:\n")
    coffee_machine["disposable cups"] += int(input())

    
# Get money from machine
def get_money():
    print("I gave you ${money}".format(**coffee_machine))
    coffee_machine["money"] = 0


# Buy coffee
def get_buy():
    coffee = MakeCoffee()
    print("What do you want to buy? 1 - espresso, 2 - latte, 3 - cappuccino, back - to main menu:")
    command = input()
    if command == "1":
        coffee.cook(int(command))
    if command == "2":
        coffee.cook(int(command))
    if command == "3":
        coffee.cook(int(command))
    if command == "back":
        pass


# Menu engine
class Action:
    def __init__(self):
        self.engine_command = 0
        self.done = True

    def engine(self, command):
        self.engine_command = command
        if self.engine_command == "buy":
            get_buy()
        if self.engine_command == "fill":
            get_fill()
        if self.engine_command == "take":
            get_money()
        if self.engine_command == "remaining":
            coffee_machine_status()
        if self.engine_command == "exit":
            self.get_exit()

    def get_exit(self):
        self.done = False


if __name__ == '__main__':
    action = Action()

    while action.done:
        print("Write action (buy, fill, take, remaining, exit):")
        choice = input()
        action.engine(choice)
