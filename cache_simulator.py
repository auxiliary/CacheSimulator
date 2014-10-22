#!/usr/bin/env python

import yaml, cache, argparse

def main():
    config_file = open('cache_config')
    configs = yaml.load(config_file)
    l1 = build_hierarchy(configs)

    print l1.name+': a', str(l1.associativity)+'-way set associative cache'


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
