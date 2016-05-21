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

import sys

from . import config

def print_message(*objects, sep=" ", end="\n", file=sys.stdout, flush=False, level=1, minlevel=1):
    """Writes a message if the level is high enough.
    
    Works just like the standard print function, if and only if `level`
    is at least `minlevel`. Otherwise it does nothing.
    
    Its primary purpose is as the underlying implementation for all the
    output functions in the debug module.
    
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
        Level of output.
    minlevel : int
        `level` must be at least `minlevel` for any output.
    """
    if level >= minlevel:
        print(*objects, sep=sep, end=end, file=file, flush=flush)

def message(*objects, sep=" ", end="\n", file=sys.stdout, flush=False):
    """Writes a message if `config.verbosity` is at least 1.
    
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
    print_message(*objects, sep=sep, end=end, file=file, flush=flush, level=config.verbosity, minlevel=1)

def info(*objects, sep=" ", end="\n", file=sys.stdout, flush=False):
    """Writes a message if `config.verbosity` is at least 2.
    
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
    print_message(*objects, sep=sep, end=end, file=file, flush=flush, level=config.verbosity, minlevel=2)

def trace(*objects, sep=" ", end="\n", file=sys.stdout, flush=False):
    """Writes a message if `config.verbosity` is at least 3.
    
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
    print_message(*objects, sep=sep, end=end, file=file, flush=flush, level=config.verbosity, minlevel=3)
