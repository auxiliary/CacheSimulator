import math, block, response
import pprint

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
                
        self.next_level = next_level
        self.block_offset_size = int(math.log(self.block_size, 2))
        self.index_size = int(math.log(self.n_sets, 2))
        if next_level:
            for i in range(self.n_sets):
                index = str(bin(i))[2:].zfill(self.index_size)
                self.data[index] = {}   #Create a dictionary of blocks for each set


    def read(self, address, current_step):
        r = None
        if not self.next_level:
            r = response.Response([True], self.hit_time)
        else:
            block_offset, index, tag = self.parse_address(address)
            in_cache = self.data[index].keys()

            if tag in in_cache:
                r = response.Response([True], self.hit_time)
            else:
                r = self.next_level.read(address, current_step)
                r.deepen(self.write_time)
                if len(in_cache) < self.associativity:
                    self.data[index][tag] = block.Block(self.block_size, current_step, False, address)
                else:
                    oldest_tag = in_cache[0] 
                    for b in in_cache:
                        if self.data[index][b].last_accessed < self.data[index][oldest_tag].last_accessed:
                            oldest_tag = b
                    if self.data[index][oldest_tag].is_dirty():
                        temp = self.next_level.write(self.data[index][oldest_tag].address, True, current_step)
                        r.time += temp.time
                    del self.data[index][oldest_tag]
                    self.data[index][tag] = block.Block(self.block_size, current_step, False, address)

        return r
   
        

    def write(self, address, from_cpu, current_step):
        #wat is cache pls
        r = None
        if not self.next_level:
            r = response.Response([True], self.write_time)
        else:
            block_offset, index, tag = self.parse_address(address)
            in_cache = self.data[index].keys()

            if tag in in_cache:
                #Set dirty bit to true if this block was in cache
                self.data[index][tag].write()
                r = response.Response([True], self.write_time)
            
            elif len(in_cache) < self.associativity:
                #If there is space in this set, create a new block and set its dirty bit to true if this write is coming from the CPU
                self.data[index][tag] = block.Block(self.block_size, current_step, from_cpu, address)
                r = response.Response([False], self.write_time)
            
            elif len(in_cache) == self.associativity:
                #If this set is full, find the oldest block, write it back if it's dirty, and replace it
                oldest_tag = in_cache[0]
                for b in in_cache:
                    if self.data[index][b].last_accessed < self.data[index][oldest_tag].last_accessed:
                        oldest_tag = b
                if self.data[index][oldest_tag].is_dirty():
                    r = self.next_level.write(self.data[index][oldest_tag].address, from_cpu, current_step)
                    r.deepen(self.write_time)
                del self.data[index][oldest_tag]
                self.data[index][tag] = block.Block(self.block_size, current_step, from_cpu, address)
                if not r:
                    r = response.Response([False], self.write_time)
            else:
                pprint.pprint(len(in_cache))
                pprint.pprint(self.data)

        return r


    def parse_address(self, address):
        #Calculate our address length and convert the address to binary string
        address_size = len(address) * 4
        binary_address = bin(int(address, 16))[2:].zfill(address_size)

        block_offset = binary_address[-self.block_offset_size:]
        index = binary_address[-(self.block_offset_size+self.index_size):-self.block_offset_size]
        tag = binary_address[:-(self.block_offset_size+self.index_size)]
        return (block_offset, index, tag)

class InvalidOpError(Exception):
    pass
