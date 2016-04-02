def judge_fitness(frame):
    close_data = frame["Close"]
    start_point = close_data.iloc[0]

    minimum_value = close_data.min()
    calmness = 100 / close_data.std()
    return_over_period = close_data.iloc[-1] / start_point

    if minimum_value < start_point * 0.95:
        fitness = 0
    else:
        fitness = return_over_period

    return fitness, calmness, return_over_period