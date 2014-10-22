class Block:
    def __init__(self, block_size):
        self.size = block_size
        self.dirty_bit = False

    def is_dirty(self):
        return self.dirty_bit

    def write(self):
        self.dirty_bit = True

    def clean(self):
        self.dirty_bit = False

    def read(self):
        print "You read me!"

