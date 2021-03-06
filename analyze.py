"""This module contains the habit tracker's functionalities necessary to handle and analyze habit data,
as well as user data.

The most important functionalities include functions to
    - show a user's habit data
    - retrieve a habit's completion dates (i.e., the dates on which habits were checked off)
    - calculate a habit's longest streak (i.e., the maximum number of consecutive periods, in which the habit
      was completed)
    - calculate a habit's completion rate (i.e., the percentage of time periods in the last four weeks, in
      which the habit was completed)
    - calculate a habit's number of streak breaks
    - calculate a user's longest streak (i.e., the longest streak of all habits)
    - calculate a user's lowest completion rate (i.e., the lowest completion rate of all habits)
    - calculate a user's best habit(s) (i.e., the habit(s) with the longest streak of all habits)
    - calculate a user's worst habit(s) (i.e., the habit(s) with the longest streak of all habits)
"""

from datetime import date, timedelta

import pandas as pd

import db
import habit as hb


def create_data_frame(database, table: str):
    """create a pandas dataframe from one of the database tables

    :param database: the database which contains the desired tables and data ('sqlite3.connection')
    :param table: the table to be created - either "Habit", "HabitAppUser" or "Completions" ('str')
    :return: a data frame containing the table's data ('pandas.core.frame.DataFrame')
    """
    habit_columns = ["PKHabitID", "FKUserID", "Name", "Periodicity", "CreationTime"]
    user_columns = ["PKUserID", "UserName"]
    completions_columns = ["PKCompletionsID", "FKHabitID", "CompletionDate", "CompletionTime"]
    column_names = {"Habit": habit_columns, "HabitAppUser": user_columns, "Completions": completions_columns}
    sql_query = pd.read_sql_query(f'''SELECT * FROM {table}''', database)
    return pd.DataFrame(sql_query, columns=column_names[table])


def check_for_username(user):
    """check if the entered username is already used in the database where the user data is stored

    :param user: the user ('user.UserDB')
    :return: True if the user name already exists, false if not ('bool')
    """
    user_df = create_data_frame(user.database, "HabitAppUser")
    users = list(user_df["UserName"])
    return True if user.username in users else False


def show_habit_data(user):
    """filter the 'Habit' table for habit data of a user

    :param user: the user for whom habit data is to be shown ('user.UserDB')
    :return: a data frame containing only the user's habits and their data ('pandas.core.frame.DataFrame')
    """
    user_id = db.find_user_id(user)
    habit_df = create_data_frame(user.database, "Habit")
    return habit_df.loc[habit_df["FKUserID"] == user_id]


def return_completions(habit):
    """return a list of a habit's completion dates

    :param habit: the habit for which the completion dates are to be returned ('habit.HabitDB')
    :return: a list (list) containing all completion dates ('str') of the habit
    """
    habit_id = db.find_habit_id(habit)
    completions_df = create_data_frame(habit.database, "Completions")
    habit_data = completions_df.loc[completions_df["FKHabitID"] == habit_id]
    return habit_data["CompletionDate"].to_list()


def return_ordered_periodicities(user):
    """return a user's periodicities (i.e., the periodicities for which the user has defined habits)
    in the correct order (daily < weekly < monthly < yearly)

    :param user: the user for whom periodicities are to be returned ('user.UserDB')
    :return: a list (list) of the correctly ordered periodicities ('str')
    """
    user_periodicities = (set([habit.periodicity for habit in user.defined_habits]))
    possible_periodicities = ["daily", "weekly", "monthly", "yearly"]  # to determine the order in the next step
    return [x for x in possible_periodicities if x in user_periodicities]


def return_habit_info(user, periodicity: str = None):
    """return the name, periodicity and creation time of either all of the user's habits (periodicity = None) or
    only the habits with a certain periodicity (e.g., periodicity = 'daily').

    :param user: the user for whom habit information is to be returned ('user.UserDB')
    :param periodicity: the periodicity for which information is to be returned ('str')
    :return: a data frame containing the name, periodicity and creation time of the desired habits
    ('pandas.core.frame.DataFrame')
    """
    habit_info = show_habit_data(user)
    if periodicity:
        habit_info = habit_info.loc[habit_info["Periodicity"] == periodicity].reset_index()
    return habit_info[["Name", "Periodicity", "CreationTime"]]


def str_to_date(str_dates: list):
    """convert a list of string dates into a list of datetime dates

    :param str_dates: list ('list') of strings dates ('str')
    :return: a list ('list') of datetime dates ('date')
    """
    return list(map(lambda x: date.fromisoformat(x), str_dates))


def weekly_start(check_date):
    """for the given date, determine the date of the preceding Monday (to determine the period start for weekly
    habits). The period start is defined as the date of the beginning of the period (i.e., every day
    for daily habits and every Monday for weekly habits etc.).

    :param check_date: the completion date for which the period start is to be determined ('date')
    :return: the date of the Monday before the passed in date ('date')
    """
    diff_to_monday = timedelta(days=check_date.weekday())
    return check_date - diff_to_monday


def monthly_start(check_date):
    """determine the first day of the month of the specified date

    :param check_date: the completion date for which the period start is to be determined ('date')
    :return: the first day of the passed in month ('date')
    """
    diff_to_first = timedelta(days=check_date.day - 1)
    return check_date - diff_to_first


def yearly_start(check_date):
    """determine the first day of the year of the specified date

    :param check_date: the completion date for which the period start is to be determined ('date')
    :return: the first day of the passed in year ('date')
    """
    return date.fromisoformat(f"{check_date.year}-01-01")


def calculate_period_starts(periodicity: str, check_dates):
    """for each completion date of a habit, calculate the period start. The period start is defined as the
    date of the beginning of the period (i.e., every day for daily habits and every Monday for weekly habits etc.)

    :param periodicity: the habit's periodicity ('str')
    :param check_dates: a list ('list') of the habit's completion dates (dates: 'date' or 'str')
    :return: a list ('list') of period starts ('date') - can contain duplicates
    """
    if isinstance(check_dates[0], str):  # are dates already in date format?
        check_dates = str_to_date(check_dates)
    period_start_funcs = {
        "daily": (lambda x: x),
        "weekly": weekly_start,
        "monthly": monthly_start,
        "yearly": yearly_start
    }
    period_start_func = period_start_funcs[periodicity]  # determine the correct function to calculate period starts
    return list(map(period_start_func, check_dates))  # calculate for each completion date the period start


def calculate_one_period_start(periodicity: str, check_date):
    """calculate the beginning of the period in which a habit with the specified periodicity was completed

    :param periodicity: the habit's periodicty ('str')
    :param check_date: the date the habit was checked off ('date')
    :return: the start of the period ('date')
    """
    period_start = calculate_period_starts(periodicity, [check_date])
    return period_start[0]


def tidy_starts(period_starts: list):
    """remove duplicates in the inserted list and sort its elements

    :param period_starts: a list ('list') of period starts ('date')
    :return: a sorted list ('list') of period starts ('date') without duplicates
    """
    return sorted(list(set(period_starts)))


def return_allowed_time(periodicity: str):
    """check what time difference is allowed between two habit completions according to the habit's periodicity
    so that the streak is not broken

    :param periodicity: the habit's periodicity ('str')
    :return: the allowed time difference ('timedelta')
    """
    timeliness = {"daily": timedelta(days=1),
                  "weekly": timedelta(days=7),
                  "monthly": timedelta(days=32),  # if a habit has not been completed in a month, the timedelta is at
                  # least 58 days
                  "yearly": timedelta(days=366)
                  }
    return timeliness[periodicity]


def add_future_period(tidy_period_starts: list, periodicity: str):
    """add a future period to calculate streaks and breaks correctly

    :param tidy_period_starts: the sorted list ('list') of period starts ('dates') without duplicates
    :param periodicity: the habit's periodicity ('str')
    :return: a list ('list') of period starts ('date') including the calculated future period
    """
    period_starts = tidy_period_starts  # to not change the actual list
    duration = return_allowed_time(periodicity)  # approximate duration of a period
    future_period = calculate_one_period_start(periodicity, date.today() + 2 * duration)  # calculate a future period
    # with at least one period distance to the current period
    period_starts.append(future_period)
    return period_starts


# prepare for streak and break analysis
def return_final_period_starts(habit):
    """prepare for streak and break analysis by performing all functions necessary to return a clean list of periods,
    in which the habit was performed at least once, including the future period to correctly calculate streaks and
    break indices.

    :param habit: the habit which is to be analyzed ('habit.HabitDB')
    :return: a clean list ('list') of period starts ('date'), denoting the start of periods,
    in which the habit was performed at least once
    """
    check_dates = return_completions(habit)
    period_starts = calculate_period_starts(habit.periodicity, check_dates)
    tidy_periods = tidy_starts(period_starts)
    return add_future_period(tidy_periods, habit.periodicity)


def calculate_element_diffs(final_periods: list):
    """calculate the differences between two consecutive elements in a list

    :param final_periods: clean list ('list') of dates ('date') that correspond to the start
     of the periods, in which the habit was checked off at least once, including one future period
    :return: a list ('list') of differences ('timedelta') between two consecutive period starts
    """
    return [t - s for s, t in zip(final_periods, final_periods[1:])]


def calculate_break_indices(final_periods: list, periodicity: str):
    """for the final periods, return the indices of the periods, after which a habit streak was broken
    (i.e., the indices after which a consecutive period is missing)

    :param final_periods: clean list ('list') of dates ('date') that correspond to the start
     of the periods, in which the habit was checked off at least once, including one future period
    :param periodicity: the habit's periodicity ('str')
    :return: a list ('list') of the indices ('int') which indicate the break of a streak
    """
    diffs = calculate_element_diffs(final_periods)
    allowed_time = return_allowed_time(periodicity)
    return [index for index, value in enumerate(diffs) if value > allowed_time]


def calculate_streak_lengths(habit):
    """for a habit, calculate the length of each streak (i.e., the number of consecutive periods in a row,
    in which the habit was completed at least once)

    :param habit: the habit for which the streak lengths are to be calculated ('habit.HabitDB')
    :return: a list ('list') of the habit's streak lengths ('int')
    """
    final_periods = return_final_period_starts(habit)
    break_indices = calculate_break_indices(final_periods, habit.periodicity)  # due to the added future period,
    # there is always at least one break index, even if no streak has been broken yet
    streak_lengths = [-1]  # because otherwise the following calculation does not consider the first streak
    streak_lengths[1:] = break_indices  # append the remaining break indices
    return calculate_element_diffs(streak_lengths)


def calculate_longest_streak(habit):
    """calculate the longest streak of a habit

    :param habit: the habit for which the longest streak is to be calculated ('habit.HabitDB')
    :return: the habit's longest streak ('int')
    """
    streak_lengths = calculate_streak_lengths(habit)
    return max(streak_lengths)


def habit_creator(user):
    """create a list of the user's habits

    :param user: the user for whom the habit list is to be created ('user.UserDB')
    :return: a list ('list') of the user's habits ('habit.HabitDB')
    """
    habit_data = show_habit_data(user)
    names_and_periodicity = habit_data[["Name", "Periodicity"]].values.tolist()
    return list(map(lambda x: hb.HabitDB(x[0], x[1], user), names_and_periodicity))


def calculate_longest_streak_per_habit(completed_habits: list):
    """calculate the longest streak for each habit in the specified list of habits

    :param completed_habits: a list ('list') of habits which have been completed at least once ('habit.HabitDB')
    :return: a dictionary ('dict') with the habit names ('str') as keys and their longest streaks ('int')
    as values
    """
    if len(completed_habits) == 0:
        return None
    else:
        habit_names = [habit.name for habit in completed_habits]
        longest_streaks = map(calculate_longest_streak, completed_habits)
        return dict(zip(habit_names, longest_streaks))


def calculate_longest_streak_of_all(completed_habits: list):
    """calculate the longest streak of all habits of a user that have been completed at least once.
    The habit with the longest streak is defined as the habit completed the most consecutive periods in a row
    (i.e., a daily habit has a better chance of becoming the best habit than a yearly habit)

    :param completed_habits: a list ('list') of habits ('habit.HabitDB') that have been completed at least once
    :return: a tuple ('tuple') containing the value of the longest streak of all habits ('int') as well as the
    corresponding habit name (or habit names ('str'), since it is possible that several habits have the
    same longest streak)
    """
    longest_streaks = calculate_longest_streak_per_habit(completed_habits)
    if not longest_streaks:  # if none of the user's habits have been completed
        return None, None
    else:
        longest_streak_of_all = longest_streaks[max(longest_streaks, key=longest_streaks.get)]
        best_habits = [key for (key, value) in longest_streaks.items() if value == longest_streak_of_all]  # it is
        # possible that two habits have the same longest streak. In this way, both habits are returned.
        return longest_streak_of_all, best_habits


def completed_in_period(final_periods: list, periodicity: str, period: str):
    """check if the habit was completed in the specified period.

    :param period: the period to check for, either "current" or "previous" ('str')
    :param final_periods: clean list ('list') of dates ('date') that correspond to the start
     of the periods, in which the habit was checked off at least once, including one future period
    :param periodicity: the habit's periodicity ('str')
    :return: true if the list of final periods contains the previous period, false otherwise ('bool')
    """
    cur_period_start = calculate_one_period_start(periodicity, date.today())
    if period == "current":
        return True if cur_period_start in final_periods else False
    else:
        prev_period_start = calculate_one_period_start(periodicity, cur_period_start - timedelta(days=1))
        return True if prev_period_start in final_periods else False


def calculate_curr_streak(habit):
    """calculate the specified habit's current streak, i.e., the current number of consecutive periods in a row,
    in which the habit was completed at least once.

    :param habit: the habit ('habit.HabitDB'), for which the current streak is to be calculated
    :return: the current streak (i.e., the current number of consecutive periods in a row, in which the user has
    completed the habit at least once) ('int')
    """
    final_periods = return_final_period_starts(habit)
    # if a habit was not completed in the previous period, the current streak is either 0 (not completed in
    # the current period) or 1 (completed in the current period)
    if not completed_in_period(final_periods, habit.periodicity, "previous"):
        return 0 if not completed_in_period(final_periods, habit.periodicity, "current") else 1
    else:
        streak_lengths = calculate_streak_lengths(habit)
        return streak_lengths[-1]


def calculate_break_no(habit):
    """calculate how often a habit's streaks were broken since the first completion

    :param habit: the habit which is to be analyzed ('habit.HabitDB')
    :return: the number of breaks ('int')
    """
    final_periods = return_final_period_starts(habit)
    break_indices = calculate_break_indices(final_periods, habit.periodicity)
    # if the habit was executed in the current or the previous period (since the user can then still complete
    # the habit in the current period), there is one break less than elements in break indices due to the
    # consideration of the future period
    curr_period = completed_in_period(final_periods, habit.periodicity, "current")
    prev_period = completed_in_period(final_periods, habit.periodicity, "previous")
    if curr_period or prev_period:  # for this reason, the break calculation only works for completion dates
        # in the past or at the current date
        return len(break_indices) - 1
    else:
        return len(break_indices)


def calculate_completion_rate(habit):
    """calculate a habit's completion rate during the last 28 days (daily habits)/4 full weeks (weekly habits).
    Completions in the current period are not counted. The completion rate is defined as the number of periods
    in which the habit was completed divided by the number of periods in which the habit was not
    completed during the last four weeks. It can only be calculated for daily or weekly habits.

    :param habit: the habit whose completion rate is to be calculated ('habit.HabitDB')
    :return: the habit's completion rate during the last four weeks ('float')
    """
    final_periods = return_final_period_starts(habit)
    no_possible_periods = 28 if habit.periodicity == "daily" else 4
    cur_period = calculate_one_period_start(habit.periodicity, date.today())
    period_4_weeks_ago = calculate_one_period_start(habit.periodicity, (cur_period - timedelta(weeks=4)))
    completed_periods_4_weeks = list(filter(lambda x: period_4_weeks_ago <= x < cur_period, final_periods))
    return len(completed_periods_4_weeks) / no_possible_periods


def calculate_completion_rate_per_habit(completed_habits: list):
    """for each daily or weekly habit that has been completed at least once, calculate its completion rate of
    the last four weeks

    :param completed_habits: a list ('list') of completed habits ('habit.HabitDB')
    :return: a dictionary ('dict') with the name of each daily or weekly habit ('str') as key and their
     completions rates ('float') as values
    """
    frequent_habits = [habit for habit in completed_habits if habit.periodicity in ("daily", "weekly")]
    habit_names = [habit.name for habit in frequent_habits]
    completion_rates = list(map(calculate_completion_rate, frequent_habits))
    return dict(zip(habit_names, completion_rates))


def calculate_worst_completion_rate_of_all(completed_habits: list):
    """calculate the lowest completion rate of all daily and weekly habits that have been completed at least once

    :param completed_habits: a list ('list') of completed habits ('habit.HabitDB')
    :return: a tuple ('tuple') containing the lowest completion rate ('float') and the name(s) of the
    habit(s) ('str') that have the lowest completion rate(s)
    """
    completion_rates = calculate_completion_rate_per_habit(completed_habits)
    lowest_completion_rate = completion_rates[min(completion_rates, key=completion_rates.get)]
    worst_habits = [key for (key, value) in completion_rates.items() if value == lowest_completion_rate]  # it is
    # possible that two habits have the same completion rates. In this way, both are returned
    return lowest_completion_rate, worst_habits


def find_completed_habits(habit_list: list):
    """from a list of habits, identify the habits that have been completed at least once.

    :param habit_list: a list ('list') of habits ('habit.HabitDB')
    :return: a list ('list') of habits ('habit.HabitDB') that have been completed at least once
    """
    check_dates = list(map(return_completions, habit_list))
    habit_indices = [index for index, value in enumerate(check_dates) if len(value) > 0]
    return [habit for index, habit in enumerate(habit_list) if index in habit_indices]


def analysis_index():
    """return the index names for the analysis of habits"""
    return ["periodicity: ", "last completion: ", "longest streak: ", "current streak: ",
            "total breaks: ", "completion rate (last 4 weeks): "]


def analyze_all_habits(habit_list: list):
    """provide a detailed analysis of a user's habits that have been completed at least once.

    :param habit_list: a list ('list') of all defined habits ('habit.HabitDB') of a user
    :return: a dataframe ('pandas.core.frame.DataFrame') containing a detailed analysis for each habit
    """
    completed_habits = find_completed_habits(habit_list)
    habit_names = [habit.name for habit in completed_habits]
    analysis_data = [habit.analyze_habit() for habit in completed_habits]
    analysis_dict = dict(zip(habit_names, analysis_data))
    pd.set_option("display.max_columns", None)  # to show all columns
    return pd.DataFrame(analysis_dict, index=analysis_index())


def present_habit_analysis(data: list, habit_name: str):
    """present the analysis of a habit as a data frame.

    :param data: a list ('list') of the habit's statistics such as the longest streak, the current streak etc.
    :param habit_name: the name of the habit whose analysis is to be presented ('str')
    :return: a dataframe presenting the habit's statistics ('pandas.core.frame.DataFrame')
    """
    return pd.DataFrame(data, index=analysis_index(), columns=[habit_name])


def list_to_df(analysis: list, data: list):
    """turn two lists into a dataframe.

    :param analysis: a list ('list') containg the names ('str') of statistics that were calculated
    :param data: a list ('list') containing the data that is to be displayed
    :return: a dataframe ('pandas.core.frame.DataFrame') with the two lists as columns
    """
    return pd.DataFrame({'Analysis': analysis, 'Data': data})
