
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod

from app.exceptions_definition import ArgumentError
from app.symbol_token_dict import SymbolTokenDict

class StockActionSides(Enum):

    Buy = "Buy"
    Sell = "Sell"

class AnalysisMethod(Enum):

    Technical = "Technical"
    Fundamental = "Fundamental"
    Hybrid = "Hybrid"

class ActionPointProperties(ABC):

    def __init__(self, args):

        self.date = args.get("date", None)
        self.time = args.get("time", None)

        # 2021-05-23 10:16
        datetimeFormat = "%Y-%m-%d %H:%M"
        datetimeString = f"{self.date} {self.time}"
        try:
            self.datetime = datetime.strptime(datetimeString, datetimeFormat)
        except ValueError as ex:
            raise ArgumentError("Wrong date or time format")

        self.symbol = args.get("symbol", None)
        if self.symbol is None or self.symbol == "":
            raise ArgumentError('Mandatory field "stock-symbol" is missing')
        else:
            self.symbol = self.symbol.upper()
            self.token = SymbolTokenDict.token(self.symbol)

        self.method: AnalysisMethod = args.get("method", None)
        if self.method is not None:
           self.method = self.method.title()

        self.name = args.get("name", None)

        self.side: StockActionSides = args.get("side", None)
        if self.side is None or self.side == "":
            raise ArgumentError('Mandatory field "side (buy/sell)" is missing')
        else:
            self.side = self.side.title()

        self.buyPrice = args.get("buyPrice", None)
        if self.buyPrice == "":
            self.buyPrice = None
        if self.buyPrice is not None:
            self.buyPrice = float(self.buyPrice)
        elif self.side == "Buy":
                raise ArgumentError('Mandatory field "buyPrice" is missing')

        self.sellPrice = args.get("sellPrice", None)
        if self.sellPrice == "":
            self.sellPrice = None
        if self.sellPrice is not None:
            self.sellPrice = float(self.sellPrice)
        elif self.side == "Sell":
                raise ArgumentError('Mandatory field "sellPrice" is missing')

        self.minDuration = args.get("minDuration", None)
        self.maxDuration = args.get("maxDuration", None)
        self.minReturn = args.get("minReturn", None)
        self.maxReturn = args.get("maxReturn", None)

class Recommendation(ActionPointProperties):

    def __init__(self, args):

        super().__init__(args)

        self.wait = args.get("wait", None)

    def dict(self):

        return self.__dict__

class Execution(ActionPointProperties):

    def __init__(self, recommendation, args):

        # this will point to the actual recommendation object which was executed
        self.recommendation = recommendation
        super().__init__(args)

    def dict(self):

        return self.__dict__
