
import pymongo

from app.logging_handler import log
from app.stock_actions import Execution
from app.exit_handler import ExitHandler
from app.configurations import MongoConfig
from app.stock_actions import Recommendation
from app.metaclasses_definition import Singleton

# internal configurations
DATABASE_NAME = "evalsr"
METADATA_COLLECTION_NAME = "metadata"
EXECUTIONS_COLLECTION_NAME = "executions"
PROFITLOSS_COLLECTION_NAME = "profitloss"
RECOMMENDATIONS_COLLECTION_NAME = "recommendations"

class MongoDbms(metaclass=Singleton):

    __db = None
    __dbms = None

    def __init__(self):

        self.init()

    @staticmethod
    def init():

        dbms = None # short name
        log.info("Initializing database connection")
        if MongoDbms.__dbms is None:
            dbms = MongoDbms.__dbms = pymongo.MongoClient(MongoConfig.url)

        MongoDbms.__db = dbms[DATABASE_NAME]

    @staticmethod
    def collection(collectionName):

        return MongoDbms.__db[collectionName]

class MetadataCollection(metaclass=Singleton):

    reCount = 0
    exCount = 0
    pnlCount = 0

    @staticmethod
    def init():

        cn = METADATA_COLLECTION_NAME
        collection = MongoDbms.collection(cn)
        document = collection.find_one({})

        log.info("Initializing metadata collection")

        ExitHandler.register(MetadataCollection.update_changes)

        if document:

            reCount = document["recommendationCount"]
            pnlCount = document["profitLossCount"]
            exCount = document["executionCount"]

        else:

            reCount = 0
            exCount = 0
            pnlCount = 0

            collection.insert({
                "firstdocument": True,
                "recommendationCount": reCount,
                "profitLossCount": pnlCount,
                "executionCount": exCount,
            })

        MetadataCollection.pnlCount = pnlCount
        MetadataCollection.reCount = reCount
        MetadataCollection.exCount = exCount

    @staticmethod
    def inc_re_count():

        MetadataCollection.reCount += 1
        return MetadataCollection.reCount

    @staticmethod
    def get_re_count():

        return MetadataCollection.reCount

    @staticmethod
    def inc_ex_count():

        MetadataCollection.exCount += 1
        return MetadataCollection.exCount

    @staticmethod
    def get_ex_count():

        return MetadataCollection.exCount

    @staticmethod
    def inc_pnl_count():

        MetadataCollection.pnlCount += 1
        return MetadataCollection.pnlCount

    @staticmethod
    def get_pnl_count():

        return MetadataCollection.pnlCount

    @staticmethod
    def update_changes():

        cn = METADATA_COLLECTION_NAME
        collection = MongoDbms.collection(cn)
        collection.update({"firstdocument":True}, {"$set": {
                "profitLossCount": MetadataCollection.pnlCount,
                "recommendationCount": MetadataCollection.reCount,
                "executionCount": MetadataCollection.exCount,
            }}
        )

class RecommendationCollection(metaclass=Singleton):

    @staticmethod
    def add(recommendation: Recommendation):

        placeHolderProps = {
            "feoDatetime" : None,
            "pnlCalcDatetime" : None,
            "lastDataDatetime" : None
        }

        document = recommendation.dict()
        document["appGenId"] = MetadataCollection.inc_re_count()
        document.update(placeHolderProps)

        cn = RECOMMENDATIONS_COLLECTION_NAME
        MongoDbms.collection(cn).insert(document)

        # for every recommendation there should be a PnL table
        ProfitLossCollection.add(document["symbol"], document["appGenId"],
            placeHolderProps)

    @staticmethod
    def update(documentId, fieldName, fieldValue):

        cn = RECOMMENDATIONS_COLLECTION_NAME
        MongoDbms.collection(cn).update({"_id":documentId},
            {"$set":{fieldName:fieldValue}})

    @staticmethod
    def iterator():

        for document in MongoDbms.collection().find({}):
            yield document

    @staticmethod
    def find_one(query):

        # the internal find_one gets timed out
        # MongoDbms.collection().find_one(query)
        # print(query)
        cn = RECOMMENDATIONS_COLLECTION_NAME
        resp = MongoDbms.collection(cn).find_one(query)
        return resp

    @staticmethod
    def get_symbols_set(query={}):

        symbolSet = set()
        cn = RECOMMENDATIONS_COLLECTION_NAME
        cursor = MongoDbms.collection(cn).find(query,
            {"_id":False, "symbol":True})
        for each in cursor:
            symbolSet.add(each.get("symbol"))
        return symbolSet

class ExecutionCollection(metaclass=Singleton):

    @staticmethod
    def add(execution: Execution):

        document = execution.dict()
        document["appGenId"] = MetadataCollection.inc_re_count()
        cn = EXECUTIONS_COLLECTION_NAME
        MongoDbms.collection(cn).insert(document)

class ProfitLossCollection(metaclass=Singleton):

    @staticmethod
    def add(symbol, reId, document):

        document["symbol"] = symbol
        document["recommendationId"] = reId
        document["appGenId"] = MetadataCollection.inc_pnl_count()

        cn = PROFITLOSS_COLLECTION_NAME
        MongoDbms.collection(cn).insert(document)

    @staticmethod
    def add_field(reId, fieldName, fieldValue):

        ProfitLossCollection.update(reId, fieldName, fieldValue)

    @staticmethod
    def update(reId, fieldName, fieldValue):

        cn = PROFITLOSS_COLLECTION_NAME
        MongoDbms.collection(cn).update({"recommendationId":reId}, {
            "$set":{fieldName:fieldValue}
        })

MongoDbms.init()
MetadataCollection.init()
