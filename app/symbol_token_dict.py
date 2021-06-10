
import csv

from app.metaclasses_definition import Singleton
from app.exceptions_definition import ArgumentError

SCRIPTS_DETAIL_FILEPATH = "app/static/script-data.csv"

class SymbolTokenDict(metaclass=Singleton):

    __symbolTokenDict = {}

    def __init__(self):

        SymbolTokenDict.init()

    @staticmethod
    def init():

        csvFile = open(SCRIPTS_DETAIL_FILEPATH)
        csvReader = csv.DictReader(csvFile)

        for line in csvReader:

            # we use only NSE for now
            if line["exch_seg"] != "NSE":
                continue

            # we consider only equity for now
            if not line["symbol"].endswith("-EQ"):
                continue

            symbol, *_ = line["symbol"].split('-')

            SymbolTokenDict.__symbolTokenDict[symbol] = line["token"]

        # print("Total number of NSE equity symbols : ",
        #     len(SymbolTokenDict.__symbolTokenDict))

    @staticmethod
    def token(symbol):

        token = SymbolTokenDict.__symbolTokenDict.get(symbol, None)
        if token is None:
            raise ArgumentError(f"Stock symbol {symbol} is invalid")
        return token

SymbolTokenDict.init()
