import random
import string

words = ['python', 'java', 'kotlin', 'javascript']
game_state = ""

while game_state != "exit":
    errors = 0  # lives
    random_position = random.randint(0, len(words) - 1)  # get random position

    word = list(words[random_position])  # random word from start list
    hidden_word = ['-' for i in range(len(word))]  # hide characters is
    buffer = []

    print()
    print("H A N G M A N")
    game_state = input("Type \"play\" to play the game, \"exit\" to quit:")
    if game_state == "play":

        # start loop
        while errors != 8:
            print()
            print(''.join(hidden_word))

            if hidden_word == word:
                errors = 8
                break

            character = input("Input a letter:")

            if len(character) > 1:
                print("You should input a single letter")
            elif character not in string.ascii_lowercase:
                print("It is not an ASCII lowercase letter")
            elif character in set(buffer):
                print("You already typed this letter")
            else:
                buffer.append(character)
                # check if user input exist in hidden word yet
                if character in set(hidden_word):
                    print("No improvements")
                    errors += 1

                # check if character exist in start word
                if character not in word:
                    print("No such letter in the word")
                    errors += 1

                # set user input at position
                for j, k in enumerate(word):
                    if character == k:
                        hidden_word[j] = character
                    else:
                        pass

        if hidden_word == word:
            print("You guessed the word!" +
                  "\nYou survived!")
        else:
            print("You are hanged!")