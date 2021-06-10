
import atexit
import signal

from app.metaclasses_definition import Singleton

class ExitHandler(metaclass=Singleton):

    cbList = []

    @staticmethod
    def init():
    
        atexit.register(ExitHandler.exit_handler)
        signal.signal(signal.SIGINT, ExitHandler.exit_handler)

    @staticmethod
    def register(callback):
    
        ExitHandler.cbList.append(callback)
        
    @staticmethod
    def exit_handler(*vargs, **kwargs):
    
        for callback in ExitHandler.cbList:
            callback()
            
        exit(-1)

ExitHandler.init()
