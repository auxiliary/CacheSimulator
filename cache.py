import math, block, response
import pprint

class Cache:
    def __init__(self, name, word_size, block_size, n_blocks, associativity, hit_time, write_time, write_back, logger, next_level=None):
        #Parameters configured by the user
        self.name = name
        self.word_size = word_size
        self.block_size = block_size
        self.n_blocks = n_blocks
        self.associativity = associativity
        self.hit_time = hit_time
        self.write_time = write_time
        self.write_back = write_back
        self.logger = logger
        
        #Total number of sets in the cache
        self.n_sets = n_blocks / associativity
        
        #Dictionary that holds the actual cache data
        self.data = {}
        
        #Pointer to the next lowest level of memory
        #Main memory gets the default None value
        self.next_level = next_level

        #Figure out spans to cut the binary addresses into block_offset, index, and tag
        self.block_offset_size = int(math.log(self.block_size, 2))
        self.index_size = int(math.log(self.n_sets, 2))

        #Initialize the data dictionary
        if next_level:
            for i in range(self.n_sets):
                index = str(bin(i))[2:].zfill(self.index_size)
                if index == '':
                    index = '0'
                self.data[index] = {}   #Create a dictionary of blocks for each set


    def read(self, address, current_step):
        r = None
        #Check if this is main memory
        #Main memory is always a hit
        if not self.next_level:
            r = response.Response({self.name:True}, self.hit_time)
        else:
            #Parse our address to look through this cache
            block_offset, index, tag = self.parse_address(address)

            #Get the tags in this set
            in_cache = self.data[index].keys()
            
            #If this tag exists in the set, this is a hit
            if tag in in_cache:
                r = response.Response({self.name:True}, self.hit_time)
            else:
                #Read from the next level of memory
                r = self.next_level.read(address, current_step)
                r.deepen(self.write_time, self.name)

                #If there's space in this set, add this block to it
                if len(in_cache) < self.associativity:
                    self.data[index][tag] = block.Block(self.block_size, current_step, False, address)
                else:
                    #Find the oldest block and replace it
                    oldest_tag = in_cache[0] 
                    for b in in_cache:
                        if self.data[index][b].last_accessed < self.data[index][oldest_tag].last_accessed:
                            oldest_tag = b
                    #Write the block back down if it's dirty and we're using write back
                    if self.write_back:
                        if self.data[index][oldest_tag].is_dirty():
                            self.logger.info('\tWriting back block ' + address + ' to ' + self.next_level.name)
                            temp = self.next_level.write(self.data[index][oldest_tag].address, True, current_step)
                            r.time += temp.time
                    #Delete the old block and write the new one
                    del self.data[index][oldest_tag]
                    self.data[index][tag] = block.Block(self.block_size, current_step, False, address)

        return r
   
        

    def write(self, address, from_cpu, current_step):
        #wat is cache pls
        r = None
        if not self.next_level:
            r = response.Response({self.name:True}, self.write_time)
        else:
            block_offset, index, tag = self.parse_address(address)
            in_cache = self.data[index].keys()

            if tag in in_cache:
                #Set dirty bit to true if this block was in cache
                self.data[index][tag].write(current_step)

                if self.write_back:
                    r = response.Response({self.name:True}, self.write_time)
                else:
                    #Send to next level cache and deepen results if we have write through
                    self.logger.info('\tWriting through block ' + address + ' to ' + self.next_level.name)
                    r = self.next_level.write(address, from_cpu, current_step)
                    r.deepen(self.write_time, self.name)
            
            elif len(in_cache) < self.associativity:
                #If there is space in this set, create a new block and set its dirty bit to true if this write is coming from the CPU
                self.data[index][tag] = block.Block(self.block_size, current_step, from_cpu, address)
                if self.write_back:
                    r = response.Response({self.name:False}, self.write_time)
                else:
                    self.logger.info('\tWriting through block ' + address + ' to ' + self.next_level.name)
                    r = self.next_level.write(address, from_cpu, current_step)
                    r.deepen(self.write_time, self.name)
            
            elif len(in_cache) == self.associativity:
                #If this set is full, find the oldest block, write it back if it's dirty, and replace it
                oldest_tag = in_cache[0]
                for b in in_cache:
                    if self.data[index][b].last_accessed < self.data[index][oldest_tag].last_accessed:
                        oldest_tag = b
                if self.write_back:
                    if self.data[index][oldest_tag].is_dirty():
                        self.logger.info('\tWriting back block ' + address + ' to ' + self.next_level.name)
                        r = self.next_level.write(self.data[index][oldest_tag].address, from_cpu, current_step)
                        r.deepen(self.write_time, self.name)
                else:
                    self.logger.info('\tWriting through block ' + address + ' to ' + self.next_level.name)
                    r = self.next_level.write(address, from_cpu, current_step)
                    r.deepen(self.write_time, self.name)
                del self.data[index][oldest_tag]

                self.data[index][tag] = block.Block(self.block_size, current_step, from_cpu, address)
                if not r:
                    r = response.Response({self.name:False}, self.write_time)

        return r


    def parse_address(self, address):
        #Calculate our address length and convert the address to binary string
        address_size = len(address) * 4
        binary_address = bin(int(address, 16))[2:].zfill(address_size)

        block_offset = binary_address[-self.block_offset_size:]
        index = binary_address[-(self.block_offset_size+self.index_size):-self.block_offset_size]
        if index == '':
            index = '0'
        tag = binary_address[:-(self.block_offset_size+self.index_size)]
        return (block_offset, index, tag)

class InvalidOpError(Exception):
    pass
