#!/usr/bin/env python

import yaml, cache, argparse, logging, pprint
from terminaltables import UnixTable

def main():
    parser = argparse.ArgumentParser(description='Simulate a cache')
    parser.add_argument('-c','--config-file', help='Configuration file for the memory heirarchy', required=True)
    parser.add_argument('-t', '--trace-file', help='Tracefile containing instructions', required=True)
    arguments = vars(parser.parse_args())

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
    config_file = open(arguments['config_file'])
    configs = yaml.load(config_file)
    hierarchy = build_hierarchy(configs)
    logger.info('Memory hierarchy built.')

    #print l1.name+': a', str(l1.associativity)+'-way set associative cache'

    logger.info('Loading tracefile...')
    trace_file = open(arguments['trace_file'])
    trace = trace_file.read().splitlines()
    logger.info('Simulation!')
    simulate(hierarchy, trace, logger)
    for cache in hierarchy:
        print_cache(hierarchy[cache])

def print_cache(cache):
    ways = [""]
    sets = []
    if len(cache.data.keys()) > 0:
        first_key = cache.data.keys()[0]
        way_no = 0
        for way in range(cache.associativity):
            ways.append("Way " + str(way_no))
            way_no += 1

        sets.append(ways)
        for s in range(min(5, len(cache.data.keys()))):
            temp_way = []
            temp_way.append("Set " + str(s))
            for w in range(len(ways) - 1):
                temp_way.append(str(w))
            sets.append(temp_way)

        table = UnixTable(sets)
        table.title = cache.name
        table.inner_row_border = True
        print "\n"
        print table.table

def simulate(hierarchy, trace, logger):
    responses = []
    l1 = hierarchy['cache_1']
    for current_step in range(len(trace)):
        instruction = trace[current_step]
        logger.info(instruction)
        address, op = instruction.split()
        if op == 'R':
            r = l1.read(address, current_step)
            logger.info('hit_list: '+str(r.hit_list)+'\ttime: '+str(r.time))
            responses.append(r)
            #Do something with response
        elif op == 'W':
            r = l1.write(address, True, current_step)
            logger.info('hit_list: '+str(r.hit_list)+'\ttime: '+str(r.time))
            responses.append(r)
            #Do something with response
        else:
            raise InvalidOpError
    analyze_results(hierarchy, responses, logger)

def analyze_results(hierarchy, responses, logger):
    n_instructions = len(responses)

    amat = compute_amat(hierarchy['cache_1'], responses, logger)
    logger.info('AMATs:\n'+pprint.pformat(amat))

def compute_amat(level, responses, logger, results={}):
    #Check if this is main memory
    if not level.next_level:
        results[level.name] = level.hit_time
    else:
        n_miss = 0
        n_access = 0
        for r in responses:
            if level.name in r.hit_list.keys():
                n_access += 1
                if r.hit_list[level.name] == False:
                    n_miss += 1

        if n_access > 0:
            miss_rate = float(n_miss)/n_access
            results[level.name] = level.hit_time + miss_rate * compute_amat(level.next_level, responses, logger)[level.next_level.name] #wat
        else:
            results[level.name] = 0 * compute_amat(level.next_level, responses, logger)[level.next_level.name] #trust me, this is good
    return results


def build_hierarchy(configs):
    hierarchy = {}
    main_memory = build_cache(configs, 'mem', None)
    prev_level = main_memory
    hierarchy['mem'] = main_memory
    if 'cache_3' in configs.keys():
        cache_3 = build_cache(configs, 'cache_3', prev_level)
        prev_level = cache_3
        hierarchy['cache_3'] = cache_3
    if 'cache_2' in configs.keys():
        cache_2 = build_cache(configs, 'cache_2', prev_level)
        prev_level = cache_2
        hierarchy['cache_2'] = cache_2
    cache_1 = build_cache(configs, 'cache_1', prev_level)
    hierarchy['cache_1'] = cache_1
    return hierarchy

def build_cache(configs, name, next_level_cache):
    return cache.Cache(name,
                configs['architecture']['word_size'],
                configs['architecture']['block_size'],
                configs[name]['blocks'] if (name != 'mem') else -1,
                configs[name]['associativity'] if (name != 'mem') else -1,
                configs[name]['hit_time'],
                configs[name]['hit_time'],
                configs['architecture']['write_back'],
                next_level_cache)


if __name__ == '__main__':
    main()
