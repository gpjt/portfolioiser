#!/usr/bin/env python3.4

import csv
from datetime import datetime, timedelta
import numpy as np
import os
import pandas as pd
import random
import sys
import time

from fitness_function import judge_fitness
from portfolio import Portfolio

if len(sys.argv) != 2:
    print("Usage: evolve.py run_number")
    sys.exit(-1)

try:
    run_number = int(sys.argv[1])
except:
    print("Can't parse {} as a run number".format(sys.argv[1]))
    sys.exit(-2)

run_dir = "runs/{}".format(run_number)
if not os.path.isdir(run_dir):
    os.makedirs(run_dir)




POPULATION_SIZE = 20000
PORTFOLIO_SIZE = 8
GLOBAL_START_DATE = datetime(2012, 7, 17)
GLOBAL_END_DATE = datetime(2016, 3, 15)
GENERATIONS = 477


def generate_random_portfolio():
    raw_ratios = [random.random() for _ in range(PORTFOLIO_SIZE)]
    total = sum(raw_ratios)
    normalised_ratios = [(100 * ratio) / total for ratio in raw_ratios]
    stocks = random.sample(universe, PORTFOLIO_SIZE)
    return Portfolio(list(zip(stocks, normalised_ratios)))


def mutate(portfolio):
    holdings = list(portfolio.holdings)
    change_holding_index = random.randint(0, len(portfolio.holdings) - 1)
    if random.random() < 0.5:
        # Change the stock
        holdings[change_holding_index] = (random.choice(list(universe)), holdings[change_holding_index][1])
    else:
        # Adjust size
        new_ratios = [weight for holding, weight in holdings]
        new_ratios[change_holding_index] = new_ratios[change_holding_index] + (new_ratios[change_holding_index] * (random.random() - 0.5))
        if new_ratios[change_holding_index] < 0:
            raise Exception()
        total = sum(new_ratios)
        normalised_ratios = [(100 * ratio) / total for ratio in new_ratios]
        holdings = list(zip([holding for (holding, _) in holdings], normalised_ratios))
    return Portfolio(holdings)


universe = set()

print("Reading universe of tickers")
with open("data/share_universe.csv", "r") as f:
    for line in f:
        universe.add(line.strip())
print("Read {} tickers".format(len(universe)))

print("Loading market data")
market_data = {}
for ticker in universe:
    frame = pd.read_csv("data/{}.csv".format(ticker), parse_dates=[0], index_col=0)
    frame = frame.reindex(pd.date_range(GLOBAL_START_DATE, GLOBAL_END_DATE, freq="D"), method="ffill")
    frame.fillna(method="ffill", inplace=True)
    market_data[ticker] = frame
print("Done loading, got market data for {} tickers".format(len(market_data)))


generations_file_path = "{}/generations.csv".format(run_dir)
generation_number = 0
population = set()
if not os.path.isfile(generations_file_path):
    print("Generating {} initial portfolios with {} stocks in each".format(POPULATION_SIZE, PORTFOLIO_SIZE))
    for ii in range(POPULATION_SIZE):
        population.add(generate_random_portfolio())
    print("Done generating, got {} portfolios".format(len(population)))
else:
    print("Reading generations file")
    with open(generations_file_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            generation_number = int(row[0])
    print("Generation number is {}".format(generation_number))
    current_population_file = "{}/population_after_{}.csv".format(run_dir, generation_number)
    print("Reading in population from {}".format(current_population_file))
    with open(current_population_file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            holdings = [holding.split(":") for holding in row]
            holdings = [(ticker, float(quantity)) for (ticker, quantity) in holdings]
            population.add(Portfolio(holdings))
    print("Read {} portfolios".format(len(population)))
    generation_number += 1
    print("Restarting at generation {}".format(generation_number))


start_dates = [
    datetime(2012, 7, 17),
    datetime(2013, 1, 1),
    datetime(2013, 6, 1),
    datetime(2014, 1, 1),
    datetime(2014, 6, 1),
    datetime(2015, 1, 1),
    datetime(2015, 3, 2),
]

for generation in range(generation_number, GENERATIONS):
    if generation == GENERATIONS - 1:
        start_date = GLOBAL_START_DATE
        end_date = GLOBAL_END_DATE
    else:
        if generation > 32:
            if generation % 5 == 0:
                start_date = start_dates[-1]
            else:
                start_date = random.choice(start_dates)
        else:
            start_date = start_dates[-1]
        end_date = start_date + timedelta(days=365)


    print()
    print("*" * 80)
    print("Generation {}".format(generation))
    print("*" * 80)
    print()
    print("Judging fitness over {} to {}".format(start_date, end_date))
    start_time = time.time()
    metrics_portfolios = []
    for portfolio in population:
        trace = portfolio.trace(market_data, start_date, end_date)
        fitness, calmness, return_over_period = judge_fitness(trace.frame)
        metrics_portfolios.append((fitness, calmness, return_over_period, portfolio))
    metrics_portfolios = sorted(metrics_portfolios, key=lambda element: element[0])
    print("Done collating fitness, took {}s".format(time.time() - start_time))

    print("Finished generation {}. Stats (min / max / average)".format(generation))
    fitnesses = [fitness for (fitness, _, _, _) in metrics_portfolios]
    print("Fitness: {} / {} / {}".format(min(fitnesses), max(fitnesses), np.mean(fitnesses)))
    calmnesses  = [calmness for (_, calmness, _, _) in metrics_portfolios]
    print("Calmness: {} / {} / {}".format(min(calmnesses), max(calmnesses), np.mean(calmnesses)))
    returns_over_period  = [return_over_period for (_, _, return_over_period, _) in metrics_portfolios]
    print("Returns: {} / {} / {}".format(min(returns_over_period), max(returns_over_period), np.mean(returns_over_period)))
    winner_fitness, winner_calmness, winner_returns_over_period, winner_porfolio = metrics_portfolios[-1]
    print("Winner fitness {}".format(winner_fitness))
    print("Winner calmness {}".format(winner_calmness))
    print("Winner return {}".format(winner_returns_over_period))
    print("Winner holdings:")
    for ticker, holding in winner_porfolio.holdings:
        print("{}, {}".format(ticker, holding))

    print("Culling...")
    new_population = set()
    # Kill weakest half plus any with zero rating
    survivors_after_file = "{}/survivors_after_{}.csv".format(run_dir, generation)
    with open(survivors_after_file, "w") as f:
        writer = csv.writer(f)
        for rating, _, _, portfolio in metrics_portfolios[int(len(metrics_portfolios) / 2):]:
            if rating != 0:
                new_population.add(portfolio)
                writer.writerow(
                    [rating] + [
                        "{}:{}".format(ticker, quantity)
                        for (ticker, quantity) in portfolio.holdings
                    ]
                )
    print("{} survivors ({}%)".format(len(new_population), len(new_population) * 100 / len(population)))
    if len(new_population) < 100:
        print("BAILOUT extinction-level event")
        raise Exception()

    if generation < GENERATIONS - 1:

        new_portfolio_count = len(population) - len(new_population)
        print("Need {} new portfolios".format(new_portfolio_count))

        print("Creating 90% mutated portfolios weighting reproduction chances to highest-ranked")
        start_time = time.time()
        reproducing_population = [portfolio for (_, _, _, portfolio) in metrics_portfolios]
        reproduction_chance_unnormalised = range(len(reproducing_population))
        normalisation_factor = sum(reproduction_chance_unnormalised)
        reproduction_chance = [v / normalisation_factor for v in reproduction_chance_unnormalised]
        for jj in range(int(new_portfolio_count * 0.9)):
            new_population.add(mutate(np.random.choice(reproducing_population, None, p=reproduction_chance)))
        print(
            "Done mutating, took {}s.  New population is now {}".format(
                time.time() - start_time, len(new_population)
            )
        )

        to_fill = POPULATION_SIZE - len(new_population)
        print("Generating {} new random portfolios".format(to_fill))
        for jj in range(to_fill):
            new_population.add(generate_random_portfolio())
        print("Done generating new random portfolios")

        population = new_population

    current_population_file = "{}/population_after_{}.csv".format(run_dir, generation)
    with open(current_population_file, "w") as f:
        writer = csv.writer(f)
        for portfolio in population:
            writer.writerow([
                "{}:{}".format(ticker, quantity)
                for (ticker, quantity) in portfolio.holdings
            ])
    with open(generations_file_path, "a") as f:
        writer = csv.writer(f)
        writer.writerow([
            str(generation),
            str(min(fitnesses)), str(max(fitnesses)), str(np.mean(fitnesses)),

        ])


