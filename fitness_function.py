def judge_fitness(frame):
    close_data = frame["Close"]
    start_point = close_data.iloc[0]
    minimum_value = close_data.min()
    if minimum_value < start_point * 0.95:
        return 0

    calmness = 100 / close_data.std()

    return_over_period = close_data.iloc[-1] / start_point

    return calmness * return_over_period