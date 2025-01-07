class Agent:
    def __init__(self, config):
        self.config = config
        self.name = self.__class__.__name__
        
    def run(self):
        """Base run method to be implemented by child classes"""
        raise NotImplementedError
        
    def log(self, message):
        """Common logging method for all agents"""
        print(f"[{self.name}] {message}") 