class MockScanner():
    def __init__(self, registry, file_list):
        self.registry = registry
        self.file_list = file_list

    def scan(self, source):
        for file_info in self.file_list:
            yield file_info


class MockSource():
    def __init__(self, file_list):
        self.file_list = file_list

    def walk(self):
        for file_info in self.file_list:
            yield file_info
