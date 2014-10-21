class Response:
    def __init__(self, was_hit, time, data=''):
        self.was_hit = was_hit
        self.depth = 1
        self.time = time
        self.data = data

    def add_time(self, time):
        self.time += time

    def deepen(self):
        self.depth += 1

    def missed(self):
        self.was_hit = False
