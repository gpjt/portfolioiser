from datetime import datetime
import numpy as np
import pandas as pd
import unittest

from fitness_function import judge_fitness


class TestFitnessFunction(unittest.TestCase):

    def test_returns_metrics_as_well_as_fitness(self):
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
        fitness, calmness, return_over_period = judge_fitness(performance_frame)
        self.assertEqual(calmness, 100 / np.std([100, 94, 96, 105], ddof=1))
        self.assertEqual(return_over_period, 1.05)


    def test_returns_zero_fitness_if_drops_below_5_percent_of_start(self):
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
        fitness, calmness, return_over_period = judge_fitness(performance_frame)
        self.assertEqual(fitness, 0)


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
        non_vol_fitness, non_vol_calmness, non_vol_return_over_period = judge_fitness(non_volatile_frame)
        vol_fitness, vol_calmness, vol_return_over_period = judge_fitness(volatile_frame)
        self.assertGreater(non_vol_fitness, vol_fitness)


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
        high_return_fitness, high_return_calmness, high_return_return_over_period = judge_fitness(high_return_frame)
        low_return_fitness, low_return_calmness, low_return_return_over_period = judge_fitness(low_return_frame)
        self.assertGreater(high_return_fitness, low_return_fitness)

