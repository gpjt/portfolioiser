#!/usr/bin/env python3.4

from datetime import datetime
import os
import pandas

cutoff = datetime(2012, 7, 17)

success = set()
fail = set()
for filename in os.listdir("data"):
    frame = pandas.read_csv("data/{}".format(filename), parse_dates=[0])
    ticker = filename[:-4]
    min_date = frame.min(index="Date")["Date"]
    if min_date > cutoff:
        print("Failed {} with {}".format(ticker, min_date))
        fail.add(ticker)
        continue

    print("Start date OK {} with {}".format(ticker, min_date))
    success.add(ticker)


print("Success: {}".format(success))
print("Fail: {}".format(fail))

print("Success count: {}".format(len(success)))
print("Fail count: {}".format(len(fail)))

with open("data/share_universe.csv", "w") as f:
    for ticker in success:
        f.write(ticker + "\n")
