class Response:
    def __init__(self, hit_list, time, data=''):
        self.hit_list = hit_list
        self.time = time
        self.data = data

    def deepen(self, time):
        self.hit_list.append(False)
        self.time += time
