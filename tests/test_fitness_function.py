from datetime import datetime
import pandas as pd
import unittest

from fitness_function import judge_fitness


class TestFitnessFunction(unittest.TestCase):

    def test_returns_zero_if_drops_below_5_percent_of_start(self):
        performance_frame = pd.DataFrame({
            "Close": pd.Series(
                [
                    100,
                    94,
                    96,
                    105,
                ],
                index=[
                    datetime(2016, 1, 1),
                    datetime(2016, 1, 2),
                    datetime(2016, 1, 3),
                    datetime(2016, 1, 4),
                ]
            )
        })
        self.assertEqual(judge_fitness(performance_frame), 0)


    def test_returns_better_numbers_for_less_volatile_returns(self):
        volatile_frame = pd.DataFrame({
            "Close": pd.Series(
                [
                    100,
                    95,
                    110,
                    95,
                ],
                index=[
                    datetime(2016, 1, 1),
                    datetime(2016, 1, 2),
                    datetime(2016, 1, 3),
                    datetime(2016, 1, 4),
                ]
            )
        })
        non_volatile_frame = pd.DataFrame({
            "Close": pd.Series(
                [
                    100,
                    95,
                    105,
                    95,
                ],
                index=[
                    datetime(2016, 1, 1),
                    datetime(2016, 1, 2),
                    datetime(2016, 1, 3),
                    datetime(2016, 1, 4),
                ]
            )
        })
        self.assertGreater(judge_fitness(non_volatile_frame), judge_fitness(volatile_frame))


    def test_returns_better_numbers_for_better_returns_if_volatility_equal(self):
        high_return_frame = pd.DataFrame({
            "Close": pd.Series(
                [
                    100,
                    200,
                    300,
                    400,
                ],
                index=[
                    datetime(2016, 1, 1),
                    datetime(2016, 1, 2),
                    datetime(2016, 1, 3),
                    datetime(2016, 1, 4),
                ]
            )
        })
        low_return_frame = pd.DataFrame({
            "Close": pd.Series(
                [
                    100,
                    200,
                    400,
                    300,
                ],
                index=[
                    datetime(2016, 1, 1),
                    datetime(2016, 1, 2),
                    datetime(2016, 1, 3),
                    datetime(2016, 1, 4),
                ]
            )
        })
        self.assertGreater(judge_fitness(high_return_frame), judge_fitness(low_return_frame))

