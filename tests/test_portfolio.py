from datetime import datetime
import pandas as pd
import unittest

from portfolio import Portfolio


class TestPortfolio(unittest.TestCase):

    def test_can_create_with_ticker_and_percentages(self):
        portfolio = Portfolio([
            ("BACK.L", 10),
            ("BACS.L", 10),
            ("BBSB.L", 10),
            ("BRIC.L", 10),
            ("CBE0.L", 10),
            ("CBE7.L", 10),
            ("CBIU.L", 40),
        ])
        self.assertEqual(
            portfolio.holdings,
            [
                ("BACK.L", 10),
                ("BACS.L", 10),
                ("BBSB.L", 10),
                ("BRIC.L", 10),
                ("CBE0.L", 10),
                ("CBE7.L", 10),
                ("CBIU.L", 40),
            ]
        )


    def test_generate_trace_calculates_holdings_as_of_start_to_sum_to_a_million(self):
        portfolio = Portfolio([
            ("BACK.L", 40),
            ("BACS.L", 60),
        ])

        start_date = datetime(2016, 1, 1)
        end_date = datetime(2016, 1, 4)

        ticker1_price = 1
        ticker1_frame = pd.DataFrame({
            "Close": pd.Series(
                [
                    ticker1_price,
                    1.01,
                ],
                index=[
                    datetime(2016, 1, 1),
                    datetime(2016, 1, 2),
                ]
            )
        })

        ticker2_price = 2
        ticker2_frame = pd.DataFrame({
            "Close": pd.Series(
                [
                    2.1,
                    ticker2_price,
                ],
                index=[
                    datetime(2015, 12, 31),
                    datetime(2016, 1, 1),
                ]
            )
        })

        market_data = {
            "BACK.L": ticker1_frame,
            "BACS.L": ticker2_frame,
        }

        trace = portfolio.trace(market_data, start_date, end_date)

        expected_ticker1_holding = (10000 / ticker1_price) * 40
        expected_ticker2_holding = (10000 / ticker2_price) * 60
        self.assertEqual(
            trace.holdings,
            [
                ("BACK.L", expected_ticker1_holding),
                ("BACS.L", expected_ticker2_holding),
            ]
        )
        ticker1_value = expected_ticker1_holding * ticker1_price
        ticker2_value = expected_ticker2_holding * ticker2_price
        total_value = ticker1_value + ticker2_value
        self.assertEqual(total_value, 1000000)
        self.assertEqual(ticker1_value / total_value, 0.4)
        self.assertEqual(ticker2_value / total_value, 0.6)


    def test_generate_trace_generates_frame(self):
        portfolio = Portfolio([
            ("BACK.L", 40),
            ("BACS.L", 60),
        ])

        start_date = datetime(2016, 1, 1)
        end_date = datetime(2016, 1, 4)

        ticker1_frame = pd.DataFrame({
            "Close": pd.Series(
                [
                    1,
                    1.01,
                    1.02,
                    1.03,
                    1.04,
                ],
                index=[
                    datetime(2016, 1, 1),
                    datetime(2016, 1, 2),
                    datetime(2016, 1, 3),
                    datetime(2016, 1, 4),
                    datetime(2016, 1, 5),
                ]
            )
        })

        ticker2_frame = pd.DataFrame({
            "Close": pd.Series(
                [
                    2.1,
                    2,
                    1.9,
                    1.8,
                    1.7,
                ],
                index=[
                    datetime(2015, 12, 31),
                    datetime(2016, 1, 1),
                    datetime(2016, 1, 2),
                    datetime(2016, 1, 3),
                    datetime(2016, 1, 4),
                ]
            )
        })

        market_data = {
            "BACK.L": ticker1_frame,
            "BACS.L": ticker2_frame,
        }

        trace = portfolio.trace(market_data, start_date, end_date)

        expected_ticker1_holding = (10000 / 1) * 40
        expected_ticker2_holding = (10000 / 2) * 60
        print(ticker1_frame)
        print(ticker2_frame)
        print(trace.frame)
        self.assertEqual(
            trace.frame,
            pd.DataFrame({
                "Close": pd.Series(
                    [
                        expected_ticker1_holding * 1 + expected_ticker2_holding * 2,
                        expected_ticker1_holding * 1.01 + expected_ticker2_holding * 1.9,
                        expected_ticker1_holding * 1.02 + expected_ticker2_holding * 1.8,
                        expected_ticker1_holding * 1.03 + expected_ticker2_holding * 1.7,
                    ],
                    index=[
                        datetime(2016, 1, 1),
                        datetime(2016, 1, 2),
                        datetime(2016, 1, 3),
                        datetime(2016, 1, 4),
                    ]
                )
            })
        )
