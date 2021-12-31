import sqlite3
from datetime import date, datetime
import os


# TODO: Entscheidung: Ist es erlaubt, Max's Datenbank-Code zu verwenden?
def get_db(name="main.db"):
    db = sqlite3.connect(name)
    create_tables(db)
    return db


def create_tables(db):
    cursor = db.cursor()

    # create HabitAppUser table
    user_table = """CREATE TABLE IF NOT EXISTS HabitAppUser
    (PKUserID INTEGER PRIMARY KEY, UserName TEXT)"""

    cursor.execute(user_table)

    # create Habit table
    habit_table = """CREATE TABLE IF NOT EXISTS Habit
    (PKHabitID INTEGER PRIMARY KEY, FKUserID INTEGER, Name TEXT, Periodicity TEXT, CreationTime TEXT,
    FOREIGN KEY(FKUserID) REFERENCES HabitAppUser(PKUserID))"""

    cursor.execute(habit_table)

    # create Completion table
    completion_table = """CREATE TABLE IF NOT EXISTS Completion
    (PKCompletionID INTEGER PRIMARY KEY, FKHabitID INTEGER, CompletionDate TEXT, 
    FOREIGN KEY(FKHabitID) REFERENCES Habit(PKHabitID))"""

    cursor.execute(completion_table)

    db.commit()


# add data into tables
def add_user(db, user_name):
    cursor = db.cursor()
    cursor.execute("INSERT INTO HabitAppUser(UserName) VALUES (?)", [user_name])
    db.commit()
    # TODO: Sicherstellen, dass UserName nicht bereits existiert (möglicherweise mit sqlite3.IntegrityError?)


def add_habit(db, user_name, name, periodicity, creation_time=None):
    cursor = db.cursor()
    cursor.execute("SELECT PKUserID FROM HabitAppUser WHERE UserName = ?", [user_name])
    user_id = cursor.fetchall()
    if not creation_time:
        creation_time = str(datetime.now())
    cursor.execute("INSERT INTO Habit(FKUserID, Name, Periodicity, CreationTime) VALUES (?, ?, ?, ?)",
                   (user_id[0][0], name, periodicity, creation_time))
    db.commit()
    # TODO: Sicherstellen, dass User nicht schon ein Habit mit demselben Namen hat


def complete_habit(db, habit_name, user_name, check_date=None):
    cursor = db.cursor()
    cursor.execute("SELECT PKUserID FROM HabitAppUser WHERE UserName = ?", [user_name])
    user_id = cursor.fetchall()
    cursor.execute("SELECT PKHabitID FROM Habit WHERE Name = ? AND FKUserID = ?",
                   (habit_name, user_id[0][0]))  # sucht nach der HabitID des gesuchten Habits von dem User
    habit_id = cursor.fetchall()  # enthält list of tuples, weshalb das erste Element referenziert werden muss
    if not check_date:
        check_date = str(date.today())
    cursor.execute("INSERT INTO Completion(FKHabitID, CompletionDate) VALUES (?, ?)",
                   (habit_id[0][0], check_date))

# cursor.execute("INSERT INTO HabitAppUser VALUES(1, 'StephanieHochge')")
# cursor.execute("INSERT INTO Habit VALUES(1, 1, 'Brush Teeth', 'daily', '123')")
# cursor.execute("INSERT INTO Completion VALUES(1, 1, ?)", (str(date.today())))


# TODO: @Chris: kann man sich die Tabelle mit den Daten irgendwie anders anzeigen lassen als durch ein Select-Statement?
