#!/usr/bin/env python

import yaml, cache, argparse, logging, pprint
from terminaltables import UnixTable

def main():
    parser = argparse.ArgumentParser(description='Simulate a cache')
    parser.add_argument('-c','--config-file', help='Configuration file for the memory heirarchy', required=True)
    parser.add_argument('-t', '--trace-file', help='Tracefile containing instructions', required=True)
    parser.add_argument('-l', '--log-file', help='Log file name', required=False)
    arguments = vars(parser.parse_args())

    log_filename = 'cache_simulator.log'
    if arguments['log_file']:
        log_filename = arguments['log_file']

    #Clear the log file if it exists
    with open(log_filename, 'w'):
        pass

    logger = logging.getLogger()
    fh = logging.FileHandler(log_filename)
    sh = logging.StreamHandler()
    logger.addHandler(fh)
    logger.addHandler(sh)

    fh_format = logging.Formatter('%(message)s')
    fh.setFormatter(fh_format)
    sh.setFormatter(fh_format)
    logger.setLevel(logging.INFO)
    
    logger.info('Loading config...')
    config_file = open(arguments['config_file'])
    configs = yaml.load(config_file)
    hierarchy = build_hierarchy(configs, logger)
    logger.info('Memory hierarchy built.')

    #print l1.name+': a', str(l1.associativity)+'-way set associative cache'

    logger.info('Loading tracefile...')
    trace_file = open(arguments['trace_file'])
    trace = trace_file.read().splitlines()
    logger.info('Simulation!')
    simulate(hierarchy, trace, logger)
    for cache in hierarchy:
        if hierarchy[cache].next_level:
            print_cache(hierarchy[cache])

def print_cache(cache):
    table_size = 5
    ways = [""]
    sets = []
    set_indexes = sorted(cache.data.keys())
    if len(cache.data.keys()) > 0:
        first_key = cache.data.keys()[0]
        way_no = 0
        for way in range(cache.associativity):
            ways.append("Way " + str(way_no))
            way_no += 1

        sets.append(ways)
        if len(set_indexes) > table_size + 4 - 1:
            for s in range(min(table_size, len(set_indexes) - 4)):
                set_ways = cache.data[set_indexes[s]].keys()
                temp_way = ["Set " + str(s)]
                for w in set_ways:
                    temp_way.append(cache.data[set_indexes[s]][w].address)
                sets.append(temp_way)
            
            for i in range(3):
                temp_way = ['.']
                for w in range(cache.associativity):
                    temp_way.append('')
                sets.append(temp_way)
            
            set_ways = cache.data[set_indexes[len(set_indexes) - 1]].keys()
            temp_way = ['Set ' + str(len(set_indexes) - 1)]
            for w in set_ways:
                temp_way.append(cache.data[set_indexes[len(set_indexes) - 1]][w].address)
            sets.append(temp_way)
        else: 
            for s in range(len(set_indexes)):
                set_ways = cache.data[set_indexes[s]].keys()
                temp_way = ["Set " + str(s)]
                for w in set_ways:
                    temp_way.append(cache.data[set_indexes[s]][w].address)
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
        address, op = instruction.split()
        if op == 'R':
            logger.info(str(current_step) + ':\tReading ' + address)
            r = l1.read(address, current_step)
            logger.info('\thit_list: ' + pprint.pformat(r.hit_list) + '\ttime: ' + str(r.time) + '\n')
            responses.append(r)
            #Do something with response
        elif op == 'W':
            logger.info(str(current_step) + ':\tWriting ' + address)
            r = l1.write(address, True, current_step)
            logger.info('\thit_list: ' + pprint.pformat(r.hit_list) + '\ttime: ' + str(r.time) + '\n')
            responses.append(r)
            #Do something with response
        else:
            raise InvalidOpError
    analyze_results(hierarchy, responses, logger)

def analyze_results(hierarchy, responses, logger):
    n_instructions = len(responses)

    amat = compute_amat(hierarchy['cache_1'], responses, logger)
    logger.info('\nAMATs:\n'+pprint.pformat(amat))

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


def build_hierarchy(configs, logger):
    hierarchy = {}
    main_memory = build_cache(configs, 'mem', None, logger)
    prev_level = main_memory
    hierarchy['mem'] = main_memory
    if 'cache_3' in configs.keys():
        cache_3 = build_cache(configs, 'cache_3', prev_level, logger)
        prev_level = cache_3
        hierarchy['cache_3'] = cache_3
    if 'cache_2' in configs.keys():
        cache_2 = build_cache(configs, 'cache_2', prev_level, logger)
        prev_level = cache_2
        hierarchy['cache_2'] = cache_2
    cache_1 = build_cache(configs, 'cache_1', prev_level, logger)
    hierarchy['cache_1'] = cache_1
    return hierarchy

def build_cache(configs, name, next_level_cache, logger):
    return cache.Cache(name,
                configs['architecture']['word_size'],
                configs['architecture']['block_size'],
                configs[name]['blocks'] if (name != 'mem') else -1,
                configs[name]['associativity'] if (name != 'mem') else -1,
                configs[name]['hit_time'],
                configs[name]['hit_time'],
                configs['architecture']['write_back'],
                logger,
                next_level_cache)


if __name__ == '__main__':
    main()
