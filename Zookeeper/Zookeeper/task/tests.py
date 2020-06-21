from hstest.stage_test import StageTest
from hstest.test_case import TestCase
from hstest.check_result import CheckResult
from animals import *

CheckResult.correct = lambda: CheckResult(True, '')
CheckResult.wrong = lambda feedback: CheckResult(False, feedback)

animal_index = {
    '0': (camel, 'camel'),
    '1': (lion, 'lion'),
    '2': (deer, 'deer'),
    '3': (goose, 'goose'),
    '4': (bat, 'bat'),
    '5': (rabbit, 'rabbit')
}

the_end_message = 'See you!'


class Zookeeper(StageTest):

    def generate(self):
        tests = [
            TestCase(stdin='1\nexit', attach='1\nexit'),
            TestCase(stdin='3\nexit', attach='3\nexit'),
            TestCase(stdin='5\nexit', attach='5\nexit'),
            TestCase(stdin='0\n2\n4\nexit', attach='0\n2\n4\nexit'),
            TestCase(stdin='0\n1\n2\n3\n4\n5\nexit', attach='0\n1\n2\n3\n4\n5\nexit'),
        ]
        return tests

    def check(self, reply, attach):
        indexes = list(map(str, range(6)))

        included_animals = attach.replace('\nexit', '').split('\n')
        excluded_animals = [index for index in indexes if index not in included_animals]

        for index in included_animals:
            if animal_index[index][0].strip() not in reply:
                return CheckResult.wrong("The " + animal_index[index][1] + " wasn't printed but was expected")

        for index in excluded_animals:
            if animal_index[index][0].strip() in reply:
                return CheckResult.wrong("The " + animal_index[index][1] + " was printed but wasn't expected")

        if the_end_message not in reply:
            return CheckResult.wrong("You should print '{}' at the end of the program".format(the_end_message))

        return CheckResult.correct()


if __name__ == '__main__':
    Zookeeper('zookeeper.zookeeper').run_tests()
