import sqlite3
from sqlite3 import Error
from datetime import datetime


def get_db(name):
    """create a sqlite database connection with the specified table schema and the passed name

    :param name: the name of the database connection (type: str)
    :return: a database connection to the sqlite database with the specified name (type: sqlite3 connection)
    """
    try:
        database = sqlite3.connect(name)
    except Error as e:  # TODO: Entscheiden: drin lassen oder rausnehmen?
        print(e)
    else:
        database.execute("PRAGMA foreign_keys = 1")  # otherwise, on delete cascade does not work
        create_tables(database)
        return database


def create_tables(database):
    """create the data schema for the database containing three tables: the HabitAppUser, the Habit and the
    Completions table.

    :param database: the database connection in which the tables are to be created (type: sqlite3.connection)
    """
    cursor = database.cursor()

    # create HabitAppUser table
    user_table = """CREATE TABLE IF NOT EXISTS HabitAppUser
    (PKUserID INTEGER PRIMARY KEY, UserName TEXT)"""

    cursor.execute(user_table)

    # create Habit table
    habit_table = """CREATE TABLE IF NOT EXISTS Habit
    (PKHabitID INTEGER PRIMARY KEY, FKUserID INTEGER, Name TEXT, Periodicity TEXT, CreationTime TIMESTAMP,
    FOREIGN KEY(FKUserID) REFERENCES HabitAppUser(PKUserID) ON DELETE CASCADE ON UPDATE CASCADE)"""

    cursor.execute(habit_table)

    # create Completions table
    completions_table = """CREATE TABLE IF NOT EXISTS Completions
    (PKCompletionsID INTEGER PRIMARY KEY, FKHabitID INTEGER, CompletionDate DATE, CompletionTime TIME, 
    FOREIGN KEY(FKHabitID) REFERENCES Habit(PKHabitID) ON DELETE CASCADE ON UPDATE CASCADE)"""

    cursor.execute(completions_table)

    database.commit()


# insert data into tables
def add_user(user):
    """store a new user in the "HabitAppUser" table

    :param user: the user who is to be stored in the database (type: user.UserDB)
    """
    cursor = user.database.cursor()
    cursor.execute("INSERT INTO HabitAppUser(UserName) VALUES (?)", [user.username])
    user.database.commit()


def find_user_id(user):
    """find the user ID of the user

    :param user: the user, whose user ID is to be found (type: user.UserDB)
    :return: the user's user_id (type: int)
    """
    cursor = user.database.cursor()
    cursor.execute("SELECT PKUserID FROM HabitAppUser WHERE UserName = ?", [user.username])
    user_id = cursor.fetchone()
    return user_id[0]


def add_habit(habit, creation_datetime=None):
    """store a new habit in the Habit table

    :param habit: the habit to store (type: habit.HabitDB)
    :param creation_datetime: the datetime the habit was created (type: str)
    """
    cursor = habit.database.cursor()
    user_id = find_user_id(habit.user)
    if not creation_datetime:
        creation_datetime = str(datetime.now())
    cursor.execute("INSERT INTO Habit(FKUserID, Name, Periodicity, CreationTime) VALUES (?, ?, ?, ?)",
                   (user_id, habit.name, habit.periodicity, creation_datetime))
    habit.database.commit()


def find_habit_id(habit):
    """find the habit id of a habit

    :param habit: the habit for which the id is to be found (type: habit.HabitDB)
    :return: the habit's id (type: int)
    """
    cursor = habit.database.cursor()
    user_id = find_user_id(habit.user)
    cursor.execute("SELECT PKHabitID FROM Habit WHERE Name = ? AND FKUserID = ?",
                   (habit.name, user_id))
    habit_id = cursor.fetchone()
    return habit_id[0]


def add_completion(habit, check_datetime=None):
    """store a new completion to the Completion table

    :param habit: the habit for which a new completion is to be stored
    :param check_datetime: the datetime when the habit was checked off (type: str)
    """
    cursor = habit.database.cursor()
    if not check_datetime:
        check_datetime = str(datetime.now())
    check_date, check_time = check_datetime.split(" ")
    habit_id = find_habit_id(habit)
    cursor.execute("INSERT INTO Completions(FKHabitID, CompletionDate, CompletionTime) VALUES (?, ?, ?)",
                   (habit_id, check_date, check_time))
    habit.database.commit()


def delete_habit(habit):
    """delete a habit and its corresponding data from the database

    :param habit: the habit to be deleted (type: habit.HabitDB)
    """
    habit_id = find_habit_id(habit)
    cursor = habit.database.cursor()
    cursor.execute("DELETE FROM Habit WHERE PKHabitID == ?", [habit_id])
    habit.database.commit()


# modify the habit's name, periodicity oder both
def modify_habit(habit, name=None, periodicity=None):
    """modify the habit's name, the habit's periodicity or both in the database

    :param habit: the habit to be modified (type: habit.HabitDB)
    :param name: the new name of the habit (type: str), if the user wants to change the name
    :param periodicity: the new periodicity of the habit (type: str), if the user wants to change the periodicity
    """
    habit_id = find_habit_id(habit)
    cursor = habit.database.cursor()
    if name:
        cursor.execute("UPDATE Habit SET Name = ? WHERE PKHabitID == ?", (name, habit_id))
    if periodicity:
        cursor.execute("UPDATE Habit SET Periodicity = ? WHERE PKHabitID == ?", (periodicity, habit_id))
    habit.database.commit()


# check if data was already entered to the user table
def check_for_user_data(database):
    """check if data has already been entered into the HabitAppUser table.

    :param database: the database connection which stores the user data (type: sqlite3.connection)
    :return: True if data has already been entered and False if not (type: bool)
    """
    cursor = database.cursor()
    cursor.execute("SELECT * From HabitAppUser")
    user_data = cursor.fetchall()
    return True if len(user_data) > 0 else False
