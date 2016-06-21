# This file is part of snowboard.
# 
# snowboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# snowboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with snowboard.  If not, see <http://www.gnu.org/licenses/>.

'''
Sends debugging messages to the console.

See https://github.com/dwhagar/snowboard/wiki/Class-Docs for documentation.
'''

verbosity = 0

import sys

def print_message(*objects, sep=" ", end="\n", file=sys.stdout, flush=False, level=1):
    """Writes a message if the level is high enough.
    
    Works just like the standard print function, if and only if `level`
    is at least `verbosity`. Otherwise it does nothing.
    
    Its primary purpose is as the underlying implementation for all the
    normal output functions in the debug module.
    
    Parameters
    ----------
    objects : positional parameter pack of objects
        Each object in `*objects` is converted to `str` and printed in turn.
    sep : str
        Value output between each item in `objects`.
    end : str
        Value output at the end.
    file : file-like
        File-like object to write output to.
    flush : bool
        If `True`, flush `file` after output.
    level : int
        `verbosity` must be at least `level` for any output.
    """
    global verbosity
    if level <= verbosity:
        print(*objects, sep=sep, end=end, file=file, flush=flush)

def debug_message(*objects, sep=" ", end="\n", type="DEBUG", level=3):
    """Writes an error message if the level is high enough.
    
    If `level` is at least `verbosity`, basically equivalent to:
        print("[" + type + "]: ", *objects, sep=sep, end=end, 
            file=sys.stderr, flush=True)
    Otherwise it does nothing.
    
    Its primary purpose is as the underlying implementation for all the
    error output functions in the debug module.
    
    Parameters
    ----------
    objects : positional parameter pack of objects
        Each object in `*objects` is converted to `str` and printed in turn.
    sep : str
        Value output between each item in `objects`.
    end : str
        Value output at the end.
    type : str
        What to tag output as.
    level : int
        `verbosity` must be at least `level` for any output.
    """
    if level <= verbosity:
        print("[", type, "]: ", sep="", end="", file=sys.stderr, flush=False)
        print(*objects, sep=sep, end=end, file=sys.stderr, flush=True)

def message(*objects, sep=" ", end="\n", file=sys.stdout, flush=False):
    """Writes a message if `verbosity` is at least 1.
    
    Parameters
    ----------
    objects : positional parameter pack of objects
        Each object in `*objects` is converted to `str` and printed in turn.
    sep : str
        Value output between each item in `objects`.
    end : str
        Value output at the end.
    file : file-like
        File-like object to write output to.
    flush : bool
        If `True`, flush `file` after output.
    """
    print_message(*objects, sep=sep, end=end, file=file, flush=flush, level=1)

def info(*objects, sep=" ", end="\n", file=sys.stdout, flush=False):
    """Writes a message if `verbosity` is at least 2.
    
    Parameters
    ----------
    objects : positional parameter pack of objects
        Each object in `*objects` is converted to `str` and printed in turn.
    sep : str
        Value output between each item in `objects`.
    end : str
        Value output at the end.
    file : file-like
        File-like object to write output to.
    flush : bool
        If `True`, flush `file` after output.
    """
    print_message(*objects, sep=sep, end=end, file=file, flush=flush, level=2)

def trace(*objects, sep=" ", end="\n", file=sys.stdout, flush=False):
    """Writes a message if `verbosity` is at least 3.
    
    Parameters
    ----------
    objects : positional parameter pack of objects
        Each object in `*objects` is converted to `str` and printed in turn.
    sep : str
        Value output between each item in `objects`.
    end : str
        Value output at the end.
    file : file-like
        File-like object to write output to.
    flush : bool
        If `True`, flush `file` after output.
    """
    print_message(*objects, sep=sep, end=end, file=file, flush=flush, level=3)

def error(*objects, sep=" ", end="\n"):
    """Writes an error message.
    
    The message is written to `sys.stderr`.
    
    Parameters
    ----------
    objects : positional parameter pack of objects
        Each object in `*objects` is converted to `str` and printed in turn.
    sep : str
        Value output between each item in `objects`.
    end : str
        Value output at the end.
    """
    debug_message(*objects, sep=sep, end=end, type="ERROR", level=0)

def warn(*objects, sep=" ", end="\n"):
    """Writes a warning message.
    
    The message is written to `sys.stderr`.
    
    `verbosity` must be at least 1 to show any output.
    
    Parameters
    ----------
    objects : positional parameter pack of objects
        Each object in `*objects` is converted to `str` and printed in turn.
    sep : str
        Value output between each item in `objects`.
    end : str
        Value output at the end.
    """
    debug_message(*objects, sep=sep, end=end, type="WARNING", level=1)

def debug(*objects, sep=" ", end="\n"):
    """Writes a debug message.
    
    The message is written to `sys.stderr`.
    
    `verbosity` must be at least 3 to show any output.
    
    Parameters
    ----------
    objects : positional parameter pack of objects
        Each object in `*objects` is converted to `str` and printed in turn.
    sep : str
        Value output between each item in `objects`.
    end : str
        Value output at the end.
    """
    debug_message(*objects, sep=sep, end=end, type="DEBUG", level=3)
