CacheSimulator
==============

A cache simulator in Python for CS 530

# Goals

This simulator will create a memory heirarchy from a YAML configuration file
and calculate the AMAT for a given tracefile.

The memory heirarchy is configurable with the following features:
- Word size, block size
  - Address size does not need to be defined
- L1 cache with user-defined parameters
  - Associativity
  - Hit time
  - Write time
- Optional L2 and L3 caches
- Simulate write back and write through
- Pretty print the cache layouts

Still a work in progress!

