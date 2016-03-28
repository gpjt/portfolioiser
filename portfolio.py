class Portfolio:

    def __init__(self, holdings):
        self.holdings = holdings


    def trace(self, market_data, start_date, end_date):
        class Trace:
            pass
        trace = Trace()
        trace.holdings = []
        trace.frame = None
        for security, percentage in self.holdings:
            quantity = 10000 / market_data[security].loc[start_date]["Close"] * percentage
            trace.holdings.append((security, quantity))
            if trace.frame is None:
                trace.frame = market_data[security][start_date:end_date] * quantity
            else:
                trace.frame += market_data[security][start_date:end_date] * quantity
        return trace
