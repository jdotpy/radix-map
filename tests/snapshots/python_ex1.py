class DataProcessor:
    def __init__(self, source: str):
        self.source = source
    
    def process(self):
        self._validate()
        return "done"

    def _validate(self):
        pass

def global_helper():
    pass
