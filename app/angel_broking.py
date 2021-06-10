
from app.configurations import AngelBrokingConfig
from datetime import datetime
from smartapi import SmartConnect
from app.metaclasses_definition import Singleton
from app.logging_handler import log

class AngelBroking(metaclass=Singleton):

    __connection = None

    def __init__(self):

        AngelBroking.init()

    @staticmethod
    def init():

        log.info("Initializing Angel Broking connection")
        
        connection=SmartConnect(
            api_key=AngelBrokingConfig.apiKey
        )

        data = connection.generateSession(
            AngelBrokingConfig.username, 
            AngelBrokingConfig.password
        )

        refreshToken= data['data']['refreshToken']
        userProfile= connection.getProfile(refreshToken)
        feedToken=connection.getfeedToken()

        AngelBroking.__connection = connection

    @staticmethod
    def get_candle_data(param):

        return AngelBroking.__connection.getCandleData(param)

    @staticmethod
    def get_today_data(token):

        return AngelBroking.get_day_data(datetime.now())

    @staticmethod
    def get_day_data(datetimeInst, token):

        todayDate = datetimeInst.strftime("%Y-%m-%d")
        fromDate = f"{todayDate} 09:00"
        toDate = f"{todayDate} 16:00"

        param ={
            "exchange": "NSE",
            "symboltoken": token,
            "interval": "ONE_MINUTE",
            "fromdate": fromDate,
            "todate": toDate
        }

        return AngelBroking.get_candle_data(param)

AngelBroking.init()
