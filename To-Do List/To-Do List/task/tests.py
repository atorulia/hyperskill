from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from hstest.check_result import CheckResult
from hstest.stage_test import StageTest
from hstest.test_case import TestCase
from datetime import datetime, timedelta
from typing import List
import os
import shutil

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

menu = """
1) Today's tasks
2) Week's tasks
3) All tasks
4) Missed tasks
5) Add task
6) Delete task
0) Exit
""".strip().lower()

weekdays = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday'
]


class ToDoList(StageTest):
    db_name = 'todo.db'
    tasks_before_delete = None
    is_completed = False

    def generate(self) -> List[TestCase]:
        return [
            TestCase(
                stdin='0',
                check_function=ToDoList.check_menu
            ),
            TestCase(
                stdin='0',
                check_function=self.check_db_file
            ),
            TestCase(
                stdin=[self.clear_table,
                       self.check_empty_list,
                       self.check_weeks_tasks,
                       self.check_added_task]

            ),
            TestCase(
                stdin=[self.check_deadlines_all_tasks,
                       self.ignore_output,
                       self.check_weeks_task_output]
            ),

            TestCase(
                stdin=[self.check_missed_tasks,
                       self.check_missed_tasks_ignore_output,
                       self.check_list_of_missed_tasks]
            ),

            TestCase(
                stdin=[
                    self.check_delete_task,
                    self.delete_tasks,
                    self.check_if_tasks_deleted
                ]
            )
        ]

    @staticmethod
    def check_menu(reply, attach):
        if menu in reply.lower():
            return CheckResult.correct()
        else:
            return CheckResult.wrong('Your program doesn\'t show the menu from example')

    def check_db_file(self, reply, attach):
        if not os.path.exists('todo.db'):
            return CheckResult.wrong('You didn\'t create the database file. It should be name todo.db')
        shutil.copy2('todo.db', 'temp.db')

        tables_in_db = self.execute('SELECT  name FROM sqlite_master '
                                    'WHERE type =\'table\' AND name '
                                    'NOT LIKE \'sqlite_%\';')
        tables_in_db = [table[0] for table in tables_in_db]
        if 'task' not in tables_in_db:
            return CheckResult.wrong('Your database doesn\'t have \'task\' table.')

        columns_in_table = self.execute('PRAGMA table_info(task)')
        columns_in_table = [[*column[1:3]] for column in columns_in_table]
        correct_columns = ['id', 'INTEGER'], ['task', 'VARCHAR'], ['deadline', 'DATE']
        for column in correct_columns:
            if column not in columns_in_table:
                CheckResult.wrong(
                    'Your table should contain \'{}\' column with \'{}\' type'.format(column[0], column[1]))
        return CheckResult.correct()

    def clear_table(self, output):
        self.execute('DELETE FROM task')
        return '1'

    def check_empty_list(self, output):
        if 'nothing' not in output.lower():
            return CheckResult.wrong('When the to-do list is empty you should output \'Nothing to do!\'')
        return '2'

    def check_weeks_tasks(self, output):
        for day in weekdays:
            if day not in output.lower():
                return CheckResult.wrong(
                    'There is no {} in the output.\nIn week\'s task you should output all the tasks for 7 days.'.format(
                        day.title()))

        today = datetime.today().date()
        return '5\nFirst task\n{}\n5\nSecond task\n{}\n1'.format(today, today)

    def check_added_task(self, output):
        tasks = self.execute('SELECT * FROM task')
        if not tasks:
            return CheckResult.wrong('You should save tasks in the database!')
        for task in tasks:
            task = list(task)
            if 'First task' in task:
                today = datetime.today().date()
                if not str(today) in task:
                    return CheckResult.wrong('You saved wrong deadline for the tasks. Expected {}'.format(today))
                break
        else:
            return CheckResult.wrong('You didn\'t save just added task!')
        for task in tasks:
            task = list(task)
            if 'Second task' in task:
                today = datetime.today().date()
                if not str(today) in task:
                    return CheckResult.wrong('You saved wrong deadline for the tasks. Expected {}'.format(today))
                break
        else:
            return CheckResult.wrong('You didn\'t save just added task!')
        self.execute("DELETE FROM task")
        self.is_completed = True
        return '0'

    def check_deadlines_all_tasks(self, output):
        self.execute('DELETE FROM task')
        first_date = datetime.today().date()
        second_date = first_date + timedelta(days=3)
        last_date = first_date + timedelta(days=6)
        test_input = "5\nDeadline is today\n{}\n5\nDeadline in 3 days\n{}\n5\nDeadline in 6 days\n{}" \
            .format(first_date, second_date, last_date).strip()
        return test_input

    def ignore_output(self, output):
        return '2'

    def check_weeks_task_output(self, output):
        first_date = datetime.today().date()
        second_date = first_date + timedelta(days=3)
        last_date = first_date + timedelta(days=6)
        first_date_month = first_date.strftime('%b').lower()
        second_date_month = second_date.strftime('%b').lower()
        last_date_month = last_date.strftime('%b').lower()
        first_date_day = first_date.day
        second_date_day = second_date.day
        last_date_day = last_date.day
        first_date_weekday = weekdays[first_date.weekday()]
        second_date_weekday = weekdays[second_date.weekday()]
        last_date_weekday = weekdays[last_date.weekday()]

        blocks = output.strip().split('\n\n')[:-1]
        if len(blocks) != 7:
            return CheckResult.wrong('There is should be 7 days when you output the week\'s task.\n'
                                     'Make sure that you print empty lines before and after output and between each day')

        first_block = blocks[0].lower()
        second_block = blocks[3].lower()
        last_block = blocks[6].lower()

        if (first_date_month not in first_block
                or str(first_date_day) not in first_block
                or first_date_weekday not in first_block):
            return CheckResult.wrong('When you output the week\'s tasks the first date should be today\'s date.\n'
                                     'You should print weekday, number of the day and the short form of the month.')

        if 'deadline is today' not in first_block:
            return CheckResult.wrong('When you output the week\'s tasks the first date doesn\'t contain added task.')

        if (second_date_month not in second_block
                or str(second_date_day) not in second_block
                or second_date_weekday not in second_block):
            return CheckResult.wrong(
                'When you output the week\'s tasks the fourth date should be the day that in 4 days from today.\n'
                'You should print weekday, number of the day and the short form of the month.')

        if 'deadline in 3 days' not in second_block:
            return CheckResult.wrong(
                'When you output the week\'s tasks the fourth date doesn\'t contain added task for which deadline is in 4 days.')

        if (last_date_month not in last_block
                or str(last_date_day) not in last_block
                or last_date_weekday not in last_block):
            return CheckResult.wrong(
                'When you output the week\'s tasks the last date should be the day that in 6 days from today.\n'
                'You should print weekday, number of the day and the short form of the month.')

        if 'deadline in 6 days' not in last_block:
            return CheckResult.wrong(
                'When you output the week\'s tasks the last date doesn\'t contain added task for which deadline is in 6 days.')

        self.is_completed = True
        return '0'

    def check_missed_tasks(self, output):
        today = datetime.today().date()
        minus_one_day = today - timedelta(days=1)
        minus_two_days = today - timedelta(days=2)
        return '5\nFirst missed task\n{}\n5\nSecond missed task\n{}'.format(minus_two_days, minus_one_day)

    def check_missed_tasks_ignore_output(self, output):
        return '4'

    def check_list_of_missed_tasks(self, output):
        if 'missed tasks' not in output.lower():
            return CheckResult.wrong('Your program doesn\'t show missed tasks!')

        blocks = output.strip().split('\n\n')
        if len(blocks) != 2:
            return CheckResult.wrong(
                'There is something wrong with format of output. Please make sure that you print only one empty line after printing missed tasks!')

        tasks = blocks[0].lower()

        if ('first missed task' not in tasks
                or 'second missed task' not in tasks):
            return CheckResult.wrong('When you print missed task you don\'t print all of them!')

        lines = tasks.splitlines()
        index_of_first_task = 0
        index_of_second_task = 0
        for i, line in enumerate(lines):
            if 'first missed task' in line:
                index_of_first_task = i
            if 'second missed task' in line:
                index_of_second_task = i

        if index_of_first_task > index_of_second_task:
            return CheckResult.wrong('Missed tasks should be sorted by their deadlines!')

        self.is_completed = True
        return '0'

    def check_delete_task(self, output):
        self.execute('DELETE FROM task')
        first_date = datetime.today().date()
        second_date = first_date + timedelta(days=3)
        last_date = first_date + timedelta(days=6)
        test_input = "5\nDeadline is today\n{}\n5\nDeadline in 3 days\n{}\n5\nDeadline in 6 days\n{}\n6" \
            .format(first_date, second_date, last_date).strip()
        return test_input

    def delete_tasks(self, output):
        ToDoList.tasks_before_delete = len(self.execute('SELECT * FROM task'))
        return '1\n6\n1\n6\n1'

    def check_if_tasks_deleted(self, output):
        tasks_after_delete = len(self.execute('SELECT * FROM task'))
        if not tasks_after_delete < ToDoList.tasks_before_delete:
            return CheckResult.wrong('Once a task has been deleted, there should be less rows in the table.')
        self.is_completed = True
        return '0'

    def after_all_tests(self):
        if not os.path.exists('todo.db'):
            return
        with open('todo.db', 'w') as main_db:
            if os.path.exists('temp.db'):
                temp_file = open('temp.db', 'r')
                main_db.write(temp_file.read())
                temp_file.close()
                os.remove('temp.db')

    def check(self, reply, attach):
        if self.is_completed:
            self.is_completed = False
            return CheckResult.correct()
        else:
            return CheckResult.wrong('Your program doesn\'t read all inputs!')

    def execute(self, query: str):
        db = DbTool('main.db')
        try:
            result = db.session.execute(query).fetchall()
        except Exception:
            result = None
        db.session.close()
        return result


class DbTool:

    def __init__(self, file):
        self.engine = create_engine('sqlite:///todo.db?check_same_thread=false')
        self.session = sessionmaker(bind=self.engine)()

    def close(self):
        self.session.close()

    Base = declarative_base()

    class Task(Base):
        __tablename__ = 'task'
        id = Column(Integer, primary_key=True)
        task = Column(String)
        deadline = Column(Date)


if __name__ == '__main__':
    ToDoList('todolist.todolist').run_tests()
