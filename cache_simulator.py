#!/usr/bin/env python

import yaml, cache, argparse, logging

def main():
    
    logger = logging.getLogger()
    fh = logging.FileHandler('cache_simulator.log')
    sh = logging.StreamHandler()
    logger.addHandler(fh)
    logger.addHandler(sh)

    fh_format = logging.Formatter('%(asctime)s:\t%(message)s')
    fh.setFormatter(fh_format)
    sh.setFormatter(fh_format)
    logger.setLevel(logging.INFO)
    
    logger.info('Loading config...')
    config_file = open('cache_config')
    configs = yaml.load(config_file)
    l1 = build_hierarchy(configs)
    logger.info('Memory hierarchy built.')

    #print l1.name+': a', str(l1.associativity)+'-way set associative cache'

    logger.info('Loading tracefile...')
    trace_file = open('trace1.txt')
    trace = trace_file.read().split('\r\n')
    logger.info('Simulation!')
    simulate(l1, trace, logger)


def simulate(l1, trace, logger):
    for current_step in range(len(trace)):
        instruction = trace[current_step]
        logger.info(instruction)
        address, op = instruction.split()
        if op == 'R':
            r = l1.read(address, current_step)
            logger.info('hit_list: '+str(r.hit_list)+'\ttime: '+str(r.time))
            #Do something with response
        elif op == 'W':
            r = l1.write(address, True, current_step)
            logger.info('hit_list: '+str(r.hit_list)+'\ttime: '+str(r.time))
            #Do something with response
        else:
            raise InvalidOpError

def build_hierarchy(configs):
    main_memory = build_cache(configs, 'mem', None)
    prev_level = main_memory
    if 'cache_3' in configs.keys():
        cache_3 = build_cache(configs, 'cache_3', prev_level)
        prev_level = cache_3
    if 'cache_2' in configs.keys():
        cache_2 = build_cache(configs, 'cache_2', prev_level)
        prev_level = cache_2
    cache_1 = build_cache(configs, 'cache_1', prev_level)
    return cache_1

def build_cache(configs, name, next_level_cache):
    return cache.Cache(name,
                configs['architecture']['word_size'],
                configs['architecture']['block_size'],
                configs[name]['blocks'] if (name != 'mem') else -1,
                configs[name]['associativity'] if (name != 'mem') else -1,
                configs[name]['hit_time'],
                configs[name]['hit_time'],
                next_level_cache)


if __name__ == '__main__':
    main()
