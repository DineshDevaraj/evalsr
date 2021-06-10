
class Singleton(type) :
    
    def __init__(cls, name, bases, attrs, **kwargs) :
        cls._instance = None
    def __call__(cls, *vargs, **kwargs) :
        if cls._instance is None :
            cls._instance = super().__call__(*vargs, **kwargs)
        return cls._instance
