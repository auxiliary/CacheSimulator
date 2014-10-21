import math, block, response

class Cache:
    def __init__(self, name, word_size, block_size, n_blocks, associativity, hit_time, write_time, next_level=None):
        self.name = name
        self.word_size = word_size
        self.block_size = block_size
        self.n_blocks = n_blocks
        self.associativity = associativity
        self.hit_time = hit_time
        self.write_time = write_time
        
        self.n_sets = n_blocks / associativity

        self.data = {}
        for i in range(self.n_sets):
            self.data[i] = {}   #Create a dictionary of blocks for each set
        
        self.next_level = next_level
        self.block_offset_size = math.log(self.block_size)
        self.index_size = math.log(self.n_sets)

    def read(self, address):
        #Calculate our address length and convert the address to binary string
        address_size = len(address) * 4
        binary_address = bin(address)[2:].zfill(address_size)
        
        #Get the three pieces of the address
        #Sorry for the negative indexing
        block_offset = binary_address[-self.block_offset_size:]
        index = binary_address[-(self.block_offset_size+self.index_size):-self.block_offset_size]
        tag = binary_address[:-(self.block_offset_size+self.index_size)]

        try:
            #CHECK IF MAIN MEMORY
            #MAIN MEMORY IS ALWAYS A HIT
            if self.next_level:
                #Try to read this block in cache
                data[index][tag].read()
            #Create a response object
            r = response.Response(True, self.hit_time)

        except CacheMissException:
            #Call the next level of cache
            r = self.next_level.read(address)

        return r            

    def write(self, address, data=''):
        pass

class CacheMissException(Exception):
    pass
