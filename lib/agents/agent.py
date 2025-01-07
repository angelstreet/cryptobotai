class Agent:
    def __init__(self, config):
        self.config = config
        self.debug = False
        self.mock = False

    def set_debug(self, debug: bool):
        self.debug = debug

    def set_mock(self, mock: bool):
        self.mock = mock

    def run(self):
        """Base run method to be implemented by child classes"""
        raise NotImplementedError
        
    def log(self, message):
        """Common logging method for all agents"""
        print(f"[{self.name}] {message}") 