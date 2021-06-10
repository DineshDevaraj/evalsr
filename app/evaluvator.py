
from datetime import datetime

from app.logging_handler import log
from app.angel_broking import AngelBroking
from app.date_and_time import date_time_range
from app.database_handler import ProfitLossCollection
from app.database_handler import RecommendationCollection

def calc_day_pnl(datetimeInst, document):

    minuteCount = 1
    dayProfitLoss = []
    lastDataDatetime = None
    dayProfitLossPercent = []
    feoArrived = True if document.get("feoDatetime") else False
    resp = AngelBroking.get_day_data(datetimeInst, document["token"])

    for minutePrice in resp["data"]:

        # minutePrice format: [timestamp, open, high, low, close, volume]

        # timestamp example: '2021-05-26T09:15:00+05:30'
        datetimeString = minutePrice[0]
        datetimeFormat = "%Y-%m-%dT%X%z"
        datetimeObject = datetime.strptime(datetimeString, datetimeFormat)

        highPrice = float(minutePrice[2])
        lowPrice = float(minutePrice[3])

        if feoArrived == True:

            if document["side"] == "Buy":
                profitLoss = lowPrice - document["buyPrice"]
                profitLossPercent = profitLoss / document["buyPrice"] * 100
            else: # document["side"] == "Sell"
                profitLoss = document["sellPrice"] - highPrice
                profitLossPercent = profitLoss / document["sellPrice"] * 100

            dayProfitLossPercent.append(profitLossPercent)
            dayProfitLoss.append(profitLoss)

        else:

            priceInRange = False

            if document["side"] == "Buy":
                if lowPrice <= document["buyPrice"] <= highPrice:
                    priceInRange = True
            else: # document["side"] == "Sell"
                if lowPrice <= document["sellPrice"] <= highPrice:
                    priceInRange = True

            if priceInRange:

                ProfitLossCollection.update(document["appGenId"],
                    "feoDatetime", datetimeObject)
                RecommendationCollection.update(document["_id"],
                    "feoDatetime", datetimeObject)
                document["feoDatetime"] = datetimeObject

                feoArrived = True

        lastDataDatetime = datetimeObject
        minuteCount += 1

    return dayProfitLoss, dayProfitLossPercent, lastDataDatetime

def get_startend_datetime(document):

    reDatetime = document.get("datetime")
    pnlcDatetime = document.get("pnlCalcDatetime")

    if pnlcDatetime is None:

        pnlcDatetime = datetime.now()
        document["pnlCalcDatetime"] = pnlcDatetime
        startDatetime = reDatetime

    else: startDatetime = pnlcDatetime

    endDatetime = datetime.now()

    return startDatetime, endDatetime

def calculate_profitloss(symbolSet):

    result = {}
    symbolCount = 1

    if not symbolSet:
        symbolSet = RecommendationCollection.get_symbols_set()

    log.debug("Total %d symbol(s) will be processed", len(symbolSet))
    log.debug("Symbol list %s", " ".join(symbolSet))

    for symbol in symbolSet:

        dayCount = 1

        log.debug("Start processing symbol %s", symbol)
        document = RecommendationCollection.find_one({"symbol":symbol})
        (startDatetime, endDatetime) = get_startend_datetime(document)

        feoArrived = None
        lastDataDatetimeBackup = None        
        documentId = document.get("_id")
        appGenId = document.get("appGenId")

        for datetimeInst in date_time_range(startDatetime, endDatetime):

            dateString = datetime.strftime(datetimeInst, "%Y-%m-%d")
            dayProfitLoss, dayProfitLossPercent, lastDataDatetime = \
                calc_day_pnl(datetimeInst, document)

            if dayProfitLoss:

                ProfitLossCollection.add_field(appGenId, dateString, dayProfitLoss)
                ProfitLossCollection.add_field(appGenId, f"{dateString}-Percent",
                    dayProfitLossPercent)
                if feoArrived == None: feoArrived = dateString

            if lastDataDatetime is not None:
                lastDataDatetimeBackup = lastDataDatetime

            dayCount += 1

        RecommendationCollection.update(documentId, "pnlCalcDatetime", endDatetime)
        ProfitLossCollection.update(appGenId, "pnlCalcDatetime", endDatetime)

        if lastDataDatetimeBackup is not None:

            RecommendationCollection.update(documentId, "lastDataDatetime",
                lastDataDatetimeBackup)
            ProfitLossCollection.update(appGenId, "lastDataDatetime",
                lastDataDatetimeBackup)

        if feoArrived is not None:
            result[symbol] = f"opportunity on {feoArrived}"
        else:
            result[symbol] = "no opportunity to execute"

        log.debug("Finish processing symbol %s", symbol)
        symbolCount += 1

    return result
