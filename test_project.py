import pytest
from habit import Habit, HabitDB
import db
import os  # to be able to remove the test data base
from user import User, UserDB
import analyze as an


class TestHabit:

    def setup_method(self):
        self.data_base = db.get_db("test.db")
        db.add_user(self.data_base, "StephanieHochge")
        db.add_user(self.data_base, "RajaBe")
        db.add_user(self.data_base, "LibertyEvans")
        db.add_habit(self.data_base, "StephanieHochge", "Brush teeth", "daily")
        db.add_habit(self.data_base, "RajaBe", "Brush teeth", "daily")
        db.add_habit(self.data_base, "StephanieHochge", "Dance", "weekly", "2021-12-31 07:54:24.999098")
        db.add_habit(self.data_base, "StephanieHochge", "Clean kitchen", "monthly", "2022-01-01 07:54:24.999098")
        db.add_habit(self.data_base, "StephanieHochge", "Clean bathroom", "monthly", "2022-01-01 07:56:24.999098")
        db.add_habit(self.data_base, "StephanieHochge", "Go to dentist", "half yearly", "2022-01-01 07:56:24.999098")
        db.complete_habit(self.data_base, "Brush teeth", "StephanieHochge", "2021-12-24")
        db.complete_habit(self.data_base, "Brush teeth", "StephanieHochge", "2021-12-25")
        db.complete_habit(self.data_base, "Brush teeth", "StephanieHochge", "2021-12-26")
        db.complete_habit(self.data_base, "Brush teeth", "StephanieHochge", "2021-12-27")
        db.complete_habit(self.data_base, "Brush teeth", "StephanieHochge")
        # TODO: Insert further test data into test database

    def test_habit(self):
        """
        tests whether a habit object is correctly created
        """
        habit = Habit("Brush teeth", "weekly", "StephanieHochge")
        assert habit.name == "Brush teeth"
        assert habit.periodicity == "weekly"
        assert habit.user == "StephanieHochge"
        # TODO: Entscheidung: muss ich das überhaupt testen?

    def test_user(self):
        """
        tests whether a user object is correctly created
        """
        user = UserDB("StephanieHochge")
        assert user.user_name == "StephanieHochge"

    def test_user_table_db(self):
        """
        tests whether data can be added to the user table
        """
        cursor = self.data_base.cursor()  # TODO: zum Testen der Tables kann noch eine Funktion geschrieben werden (
        # Syntax wiederholt sich)
        cursor.execute("SELECT * FROM HabitAppUser")
        results = cursor.fetchall()
        assert len(results) == 3

    def test_habit_table_db(self):
        """
        tests whether data can be added to the habit table
        """
        cursor = self.data_base.cursor()
        cursor.execute("SELECT * FROM Habit")
        results = cursor.fetchall()
        assert len(results) == 6

    def test_completion_table_db(self):
        """
        tests whether data can be added to the completion table
        """
        cursor = self.data_base.cursor()
        cursor.execute("SELECT * FROM Completion")
        results = cursor.fetchall()
        assert len(results) == 5

    def test_habitDB(self):
        """
        tests whether habits can be stored and checked off
        """
        habit = HabitDB("Brush teeth", "weekly", "StephanieHochge")
        habit.store_habit(self.data_base)
        habit.check_off_habit(self.data_base)

    def test_userDB(self):
        """
        tests whether users can be stored
        """
        user = UserDB("HansJ")
        user.store_user(self.data_base)

    def test_create_data_frame(self):
        """
        tests whether data_frames can be created from data base tables
        """
        habit_df = an.create_data_frame(self.data_base, "Habit")
        user_df = an.create_data_frame(self.data_base, "HabitAppUser")
        completion_df = an.create_data_frame(self.data_base, "Completion")

    def teardown_method(self):
        os.remove("test.db")  # löscht die Testdatenbank, die beim setup erstellt wurde
