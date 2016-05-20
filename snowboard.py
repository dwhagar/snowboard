#!/bin/env python3

# Snowboard - IRC Bot Written in Python 3
# See:  https://github.com/dwhagar/snowboard for more information.

import argparse
import sys

# Program arguments
args = None

def main(argv):
	argparser = argparse.ArgumentParser(
		prog="snowboard",
		description="IRC Bot Written in Python 3.",
		fromfile_prefix_chars="@")
	
	global args
	args = argparser.parse_args(argv)
	
	result = 0	# Define a result value, so we can pass it back to the shell
	
	# Start here
	
	return result

if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
