from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Date
from datetime import datetime, timedelta
from collections import defaultdict, deque


class DataBaseEngine:
    engine = create_engine('sqlite:///todo.db?check_same_thread=False')
    Base = declarative_base()
    Session = sessionmaker(bind=engine)

    class Table(Base):
        __tablename__ = 'task'
        id = Column(Integer, primary_key=True)
        task = Column(String, default='')
        deadline = Column(Date, default=datetime.today())

        def __repr__(self):
            return self.task

    def create(self):
        self.Base.metadata.create_all(self.engine)

    def add(self, task, deadline):
        row = self.Table(task=task, deadline=datetime.strptime(deadline, '%Y-%m-%d'))
        self.session.add(row)
        self.session.commit()

    def get_all(self):
        return self.session.query(self.Table).all()

    def get_by_day(self):
        return self.session.query(self.Table).filter(self.Table.deadline == datetime.today().strftime('%Y-%m-%d')).all()

    def get_by_week(self):
        today = datetime.today()
        days = deque([(today + timedelta(days=i)) for i in range(7)])
        tasks = defaultdict(list)
        for day in days:
            tasks[day] = self.session.query(self.Table).filter(self.Table.deadline == day.strftime('%Y-%m-%d')).all()

        return tasks

    def get_missed(self):
        return self.session.query(self.Table).filter(self.Table.deadline < datetime.today()).all()

    def delete_item(self, id):
        self.session.query(self.Table).filter(self.Table.id == id).delete()
        self.session.commit()

    def __init__(self):
        self.create()
        self.session = self.Session()


class MenuEngine:
    def __init__(self):
        self.engine = DataBaseEngine()

    def add_task(self):
        task = input("Enter task\n")
        deadline = input("Enter deadline\n")
        self.engine.add(task, deadline)
        print("The task has been added!")

    def today_tasks(self):
        print(f"Today {datetime.today().day} {datetime.today().strftime('%b')}:")
        tasks = self.engine.get_by_day()
        if not tasks:
            print("Nothing to do!")
        else:
            for row in tasks:
                print(f'{row.id}. {row.task}')

    def week_tasks(self):
        tasks = self.engine.get_by_week()
        for day in tasks:
            print(f"{day.strftime('%A')} {day.strftime('%d')} {day.strftime('%b')}:")
            if not tasks[day]:
                print('Nothing to do!\n')
            else:
                for task in tasks[day]:
                    print(f'{task.id}. {task.task}')
                print()

    def all_tasks(self):
        print(f"All tasks:")
        tasks = self.engine.get_all()
        if not tasks:
            print("Nothing to do!")
        else:
            for row in tasks:
                print(f'{row.id}. {row.task}')

    def missed(self):
        print("Missed tasks:")
        missed = self.engine.get_missed()
        if not missed:
            print("Nothing is missed!")
        else:
            for row in missed:
                print(f"{row.id}. {row.task}. {row.deadline.strftime('%d')} {row.deadline.strftime('%b')}")
            print()

    def delete_item(self):
        print("Chose the number of the task you want to delete:")
        missed = self.engine.get_missed()
        if not missed:
            print("Nothing is to delete!")
        else:
            for row in missed:
                print(f"{row.id}. {row.task}. {row.deadline.strftime('%d')} {row.deadline.strftime('%b')}")
        to_delete = int(input())
        self.engine.delete_item(to_delete)
        print("The task has been deleted!")

    def run(self):
        while True:
            print("1) Today's tasks\n"
                  "2) Week's tasks\n"
                  "3) All tasks\n"
                  "4) Missed tasks\n"
                  "5) Add task\n"
                  "6) Delete task\n"
                  "0) Exit\n")
            choice = input()

            if choice == '1':
                self.today_tasks()
            if choice == '2':
                self.week_tasks()
            if choice == '3':
                self.all_tasks()
            if choice == '4':
                self.missed()
            if choice == '5':
                self.add_task()
            if choice == '6':
                self.delete_item()
            if choice == '0':
                exit(1)


if __name__ == "__main__":
    menu = MenuEngine()
    menu.run()
