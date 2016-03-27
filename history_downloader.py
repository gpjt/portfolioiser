#!/usr/bin/env python3.4

import csv
import datetime
import os
import pandas_datareader.data as datareader
import time

start = datetime.datetime(2011, 1, 1)
end = datetime.datetime(2015, 12, 31)
retries = 2

for filename in ("ishares.csv", "vanguard.csv"):
    print("Loading {}".format(filename))
    with open(filename, "r") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        for row in reader:
            ticker = row[0]

            print("About to read data for {}".format(ticker))
            for retry in range(retries):
                try:
                    frame = datareader.DataReader(ticker, "yahoo", start, end)
                    print("Done reading data for {}, storing".format(ticker))
                    frame.to_csv(os.path.join("data", ticker + ".csv"))
                    print("Done storing {}".format(ticker))
                    break
                except:
                    if retry < retries - 1:
                        print("Got an error loading {}, will pause and retry".format(ticker))
                        time.sleep(5)
                    else:
                        print("Giving up on {}".format(ticker))
