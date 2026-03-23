class MockScanner():
    def __init__(self, file_list):
        self.file_list = file_list

    def scan(self):
        for file_info in self.file_list:
            yield file_info
