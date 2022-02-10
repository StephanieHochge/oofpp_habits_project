from datetime import date, timedelta, datetime
from unittest.mock import patch

import analyze as ana
from habit import HabitDB
import test_data
from user import UserDB


class TestHabitAnalysis(test_data.DataForTestingPytest):

    def test_create_data_frame(self):
        """
        tests whether data_frames can be created from database tables
        """
        habit_df = ana.create_data_frame(self.database, "Habit")
        user_df = ana.create_data_frame(self.database, "HabitAppUser")
        completions_df = ana.create_data_frame(self.database, "Completions")

    def test_check_for_user(self):
        """
        tests whether the function to identify whether a user name already exists works or not
        :return:
        """
        user_existing = ana.check_for_username(self.user_sh)
        assert user_existing is True
        user_sh_2 = UserDB("StephanieH", self.database)
        user_existing_2 = ana.check_for_username(user_sh_2)
        assert user_existing_2 is False

    def test_return_habits(self):
        """
        tests whether user_habits are correctly returned
        """
        defined_habits = ana.show_habit_data(self.user_sh)
        assert len(defined_habits) == 6

    def test_return_habit_periodicity(self):
        """
        tests whether the periodicity of the habit is correctly returned
        """
        periodicity = ana.return_periodicity(self.user_sh, "Brush teeth")
        assert periodicity == "daily"
        periodicity = ana.return_periodicity(self.user_sh, "Dance")
        assert periodicity == "weekly"

    def test_return_ordered_periodicities(self):
        """
        tests whether the periodicities of a user's habits are returned in the correct order
        :return:
        """
        assert ana.return_ordered_periodicites(self.user_sh) == ["daily", "weekly", "monthly", "yearly"]
        assert ana.return_ordered_periodicites(self.user_rb) == ["daily", "weekly"]
        assert ana.return_ordered_periodicites(self.user_le) == []
        assert ana.return_ordered_periodicites(self.user_hp) == ["daily"]

    def test_return_habits_of_type(self):
        """
        tests whether user_habits of a specific type are correctly returned
        """
        weekly_habits = ana.return_habit_info(self.user_sh, "weekly")
        assert len(weekly_habits) == 2
        quaterly_habits = ana.return_habit_info(self.user_sh, "quarterly")
        assert len(quaterly_habits) == 0

    def test_return_habit_completions(self):
        # test if return_habit_completions returns the correct table
        habit_completions = ana.return_completions(self.dance_sh)
        assert len(habit_completions) == 20

    def test_check_for_habit_data(self):
        completions_sh = ana.return_all_completions(self.user_sh)
        completions_le = ana.return_all_completions(self.user_le)
        assert len(completions_sh) == 6
        assert len(completions_le) == 0
        assert ana.check_any_completions(self.user_sh) is True
        assert ana.check_any_completions(self.user_le) is False

    def test_calculate_period_starts(self):
        """
        tests if the period starts are correctly calculated
        """
        # test weekly_start, monthly_start and yearly_start functions
        assert ana.weekly_start(date(2022, 1, 26)) == date(2022, 1, 24)
        assert ana.monthly_start(date(2022, 2, 26)) == date(2022, 2, 1)
        assert ana.yearly_start(date(2022, 3, 24)) == date(2022, 1, 1)

        # test calculate_one_period_start function
        assert ana.calculate_one_period_start("weekly", date(2022, 1, 26)) == date(2022, 1, 24)
        assert ana.calculate_one_period_start("daily", date(2022, 2, 23)) == date(2022, 2, 23)
        assert ana.calculate_one_period_start("monthly", date(2021, 12, 24)) == date(2021, 12, 1)
        assert ana.calculate_one_period_start("yearly", date(2021, 8, 2)) == date(2021, 1, 1)

        # test calculate_period_starts function
        check_dates_daily = ["2022-01-25", "2022-01-27"]
        periods_daily = ana.calculate_period_starts("daily", check_dates_daily)
        assert periods_daily == [date(2022, 1, 25), date(2022, 1, 27)]

        check_dates_weekly = [date(2022, 1, 25), date(2022, 1, 20), date(2022, 1, 26)]
        periods_weekly = ana.calculate_period_starts("weekly", check_dates_weekly)
        assert periods_weekly == [date(2022, 1, 24), date(2022, 1, 17), date(2022, 1, 24)]

        check_dates_monthly = ["2022-01-15", "2021-12-14"]
        periods_monthly = ana.calculate_period_starts("monthly", check_dates_monthly)
        assert periods_monthly == [date(2022, 1, 1), date(2021, 12, 1)]

        check_dates_yearly = [date(2021, 6, 1), date(2020, 5, 30)]
        periods_yearly = ana.calculate_period_starts("yearly", check_dates_yearly)
        assert periods_yearly == [date(2021, 1, 1), date(2020, 1, 1)]

        # test tidy_starts function
        tidy_starts_weekly = ana.tidy_starts(periods_weekly)
        assert tidy_starts_weekly == [date(2022, 1, 17), date(2022, 1, 24)]

        # test add_future_period function
        # wird nur einmal getestet, weil calculate_one_period_start schon getestet wurde
        future_period = ana.calculate_one_period_start("weekly", date.today() + timedelta(weeks=2))  # damit Tests
        # trotz der Verwendung des aktuellen Datums in der Berechnung noch funktionieren
        assert ana.add_future_period(tidy_starts_weekly, "weekly") == [date(2022, 1, 17), date(2022, 1, 24),
                                                                       future_period]
        # hier muss man auch irgendwie mit aktuellen Daten arbeiten

        # test return_final_period_starts function
        final_periods_teeth = ana.return_final_period_starts(self.teeth_sh)
        final_periods_dance = ana.return_final_period_starts(self.dance_sh)
        final_periods_windows = ana.return_final_period_starts(self.windows_sh)
        final_periods_dentist = ana.return_final_period_starts(self.dentist_sh)
        assert len(final_periods_teeth) == 36
        assert len(final_periods_dance) == 12
        assert len(final_periods_windows) == 9
        assert len(final_periods_dentist) == 3

    def test_calculate_break_indices(self):
        # test diffs_list_elements function
        dates = [date(2021, 7, 3), date(2021, 7, 9), date(2021, 7, 10), date(2021, 8, 10)]
        assert ana.calculate_element_diffs(dates) == [timedelta(days=6), timedelta(days=1), timedelta(days=31)]

        # test calculate_break_indices function
        final_periods_teeth = ana.return_final_period_starts(self.teeth_sh)
        final_periods_dance = ana.return_final_period_starts(self.dance_sh)
        final_periods_windows = ana.return_final_period_starts(self.windows_sh)
        final_periods_dentist = ana.return_final_period_starts(self.dentist_sh)
        assert ana.calculate_break_indices(final_periods_teeth, "daily") == [4, 25, 28, 29, 32, 34]
        assert ana.calculate_break_indices(final_periods_dance, "weekly") == [4, 7, 10]
        assert ana.calculate_break_indices(final_periods_windows, "monthly") == [1, 7]
        assert ana.calculate_break_indices(final_periods_dentist, "yearly") == [1]

    def test_calculate_longest_streak(self):
        # test calculate_streak_lengths function
        assert ana.calculate_streak_lengths(self.teeth_sh) == [5, 21, 3, 1, 3, 2]
        assert ana.calculate_streak_lengths(self.dance_sh) == [5, 3, 3]
        assert ana.calculate_streak_lengths(self.windows_sh) == [2, 6]
        assert ana.calculate_streak_lengths(self.dentist_sh) == [2]

        # test calculate_longest_streak function
        assert ana.calculate_longest_streak(self.teeth_sh) == 21
        assert ana.calculate_longest_streak(self.dentist_sh) == 2

    def test_calculate_longest_streak_of_all(self):
        # test habit creator function
        habits_sh = ana.habit_creator(self.user_sh)
        assert len(habits_sh) == 6
        habits_rb = ana.habit_creator(self.user_rb)
        assert len(habits_rb) == 2
        habits_le = ana.habit_creator(self.user_le)
        assert len(habits_le) == 0

        # test find habits with data function
        habits_sh_data = ana.find_completed_habits(habits_sh)
        assert len(habits_sh_data) == 5
        habits_rb_data = ana.find_completed_habits(habits_rb)
        assert len(habits_rb_data) == 2
        habits_le_data = ana.find_completed_habits(habits_le)
        assert len(habits_le_data) == 0

        # test calculate_longest_streak_per_habit function
        longest_streaks_sh = ana.calculate_longest_streak_per_habit(habits_sh_data)
        assert longest_streaks_sh["Dance"] == 5
        longest_streak_rb = ana.calculate_longest_streak_per_habit(habits_rb_data)
        assert longest_streak_rb["Brush teeth"] == 1
        longest_streak_le = ana.calculate_longest_streak_per_habit(habits_le_data)
        assert longest_streak_le is None

        # test calculate_longest_streak_of_all function
        longest_streak_all_sh = ana.calculate_longest_streak_of_all(habits_sh_data)
        assert longest_streak_all_sh == (21, ["Brush teeth"])
        longest_streak_all_rb = ana.calculate_longest_streak_of_all(habits_rb_data)
        assert longest_streak_all_rb == (1, ["Brush teeth", "Dance"])
        longest_streak_all_le = ana.calculate_longest_streak_of_all(habits_le_data)
        assert longest_streak_all_le == (None, None)

    def test_check_previous_period(self):
        final_periods_teeth_sh = ana.return_final_period_starts(self.teeth_sh)
        assert ana.check_previous_period(final_periods_teeth_sh, self.teeth_sh.periodicity) is False
        final_periods_dance_sh = ana.return_final_period_starts(self.dance_sh)
        assert ana.check_previous_period(final_periods_dance_sh, self.dance_sh.periodicity) is True

    def test_calculate_curr_streak(self):
        assert ana.calculate_curr_streak(self.teeth_sh) == 0
        assert ana.calculate_curr_streak(self.dance_sh) == 3
        self.dance_rb.check_off_habit(check_date=str(datetime.now()))
        assert ana.calculate_curr_streak(self.dance_rb) == 1
        assert ana.calculate_curr_streak(self.windows_sh) == 6

    def test_calculate_completion_rate(self):
        assert ana.calculate_completion_rate(self.teeth_sh) == 6 / 28
        assert ana.calculate_completion_rate(self.dance_sh) == 2 / 4

    @patch('analyze.return_last_month', return_value=(12, 2021))  # damit Tests trotz der Verwendung des
    # aktuellen Datums weiterhin funktionieren
    def test_calculate_breaks(self, mock_last_month):
        # test check_curr_period function
        period_starts_curr_teeth = ana.return_final_period_starts(self.teeth_sh)
        assert ana.check_current_period(period_starts_curr_teeth, "daily") is False
        period_starts_curr_dance = ana.return_final_period_starts(self.dance_sh)
        assert ana.check_current_period(period_starts_curr_dance, "weekly") is True

        # test calulate_breaks function
        assert ana.calculate_breaks(self.teeth_sh) == 6
        assert ana.calculate_breaks(self.dance_sh) == 2
        assert ana.calculate_breaks(self.windows_sh) == 1
        assert ana.calculate_breaks(self.dentist_sh) == 0

    def test_find_habits_with_data(self):
        habit_list = ana.habit_creator(self.user_sh)
        assert len(habit_list) == 6
        habits_with_data = ana.find_completed_habits(habit_list)
        assert len(habits_with_data) == 5

    def test_calculate_worst_of_all(self):
        habit_list = self.user_sh.return_habit_list()
        habits_with_data = ana.find_completed_habits(habit_list)
        completion_rates = ana.calculate_completion_rate_per_habit(habits_with_data)
        assert list(completion_rates.values()) == [6 / 28, 2 / 4, 0 / 4]
        lowest_completion_rate, worst_habit = ana.calculate_worst_completion_rate_of_all(habits_with_data)
        assert round(lowest_completion_rate) == 0
        assert worst_habit == ["Clean bathroom"]

    def test_detailed_analysis_of_all_habits(self):
        habit_list_sh = ana.habit_creator(self.user_sh)
        habits_with_data_sh = ana.find_completed_habits(habit_list_sh)
        comparison_data_sh = ana.detailed_analysis_of_all_habits(habits_with_data_sh)
        assert list(comparison_data_sh.columns) == ["Brush teeth", "Dance", "Clean windows", "Clean bathroom",
                                                    "Go to dentist"]
        habit_list_rb = ana.habit_creator(self.user_rb)
        habits_with_data_rb = ana.find_completed_habits(habit_list_rb)
        comparison_data_rb = ana.detailed_analysis_of_all_habits(habits_with_data_rb)
        assert list(comparison_data_rb) == ["Brush teeth", "Dance"]

        # TODO: bei allen zukünftigen Funktionen darauf achten, ob sie das aktuelle Datum verwenden, das in den Tests
        #  berücksichtigen

        # test if this works for habits, for which only one completion was added

# TODO: bei jeder Funktion überprüfen, ob die auch geht, wenn das Habit noch keine Daten hat
# TODO: überprüfen, ob die Streakberechnung auch funktioniert, wenn man das Habit mehrmals pro Tag abgeschlossen hat
