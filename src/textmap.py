#!/usr/bin/env  python
"""

 This is a data visualization aide. It takes a filename  (Contents
 of file should be 8 bit ascii only please), and calculates the relative
 frequency of each symbol, then graphically represents how often the
 symbol appears in the text, by placing each symbol from the text, in
 a circle, the distance from the center, being related to how frequent
 the symbol occurs. So if you have text, which consists of only the
 letter e (100 times) and the letter m (once) m will appear in the center,
 and e, on the edge of the scale. If there is a letter l, which appears
 50 times, it will appear halfway between e and m, but displaced radially.
 Compare the differences between plaintext, random symbols, and ciphertext.
 Scale is adjusted automatically, to fit all symbols on a letter size page in
 the postscript output.
"""

# Copyright: Jim Richardson, <weaselkeeper@gmail.com> 2012

Changelog = """

Dec 1  2003, Rev 0.1: initial version.
Dec 12 2003, Rev 0.2: Changes to catch errors in input.
Dec 29 2005, Rev 0.3: Rewrite a lot, including the rect-polar
                       conversion
Dec 30 2005, Rev 0.4: Fix div/0 error for datasets that don't use all
symbols available in good_symbols.

"""
PROJECTNAME = 'textmap'

import sys
import math
import string
from operator import itemgetter
import logging
# Setup logging
logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S')

# Setup logging to console.
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger(PROJECTNAME).addHandler(console)
log = logging.getLogger(PROJECTNAME)


def get_options():
    """ Parse for any options """
    import argparse
    parser = argparse.ArgumentParser(
        description='This is a data visualization aide.')
    parser.add_argument('-f', '--file', action='store', default = None,
        help='Input file', dest='inputfile')
    parser.add_argument('-o', '--output', action='store', default = 'output.ps',
        help = 'output file' )

    _args = parser.parse_args()
    _args.usage = PROJECTNAME + ".py [options]"
    return _args


# Setting some constants
good_symbols = string.digits + string.letters


def get_biggest(_dict):
    """ calculate the largest offset, and divide all offsets by one tenth
     of it, in order to get a 0 to 10 spread so that all the files run
     through this will be in roughly the same scale. """
    _list = []
    for item in _dict.keys():
        _list.append(_dict[item])
    _list.sort()

    temp = [_list.pop(0) * -1, _list.pop()]
    temp.sort()
    return temp.pop()


def build_list(dataset):
    """ Pass this a string or tuple of characters, get back a dict, of
    char:number where number is the number of times that char occurs in
    the dataset

    We chop off cr/lf, and
    whitespace. In fact, anything other than numerical, alphabetical are
    pulled. All we care about are the actual symbols.  See good_symbols
    for details on what we want to play with. Adjust accordingly.

    First, we strip out bad_symbols, which are anything not in
    good_symbols. Then we fill a dict with everything from plaintext that
    is also present in good symbols, and set the value to 0 to start the
    ball rolling. If you change good_symbols, be wary of stuff like \
    which are postscript operators and must be dealt with or your output
    will not be correct."""

    symbol_count = {}

    for symbol in good_symbols:
        symbol_count[symbol] = 0

    for symbol in dataset:
        if good_symbols.count(symbol):
            symbol_count[symbol] = symbol_count.get(symbol, [0]) + 1

    return symbol_count


def build_coords(symbol_dict, char_sep):
    """ Create a list of the coords for the charmap"""
    sorted_list = sorted(symbol_dict.items(), key=itemgetter(0))
    angle = 0
    R_coords = {}
    P_coords = {}
    biggest = 0
    for char in symbol_dict.keys():
        freq = symbol_dict[char]
        if biggest < freq:
            biggest = freq
        if biggest:
            scale_factor = 1.0 / biggest

    for char in sorted_list:
        freq_scaled = symbol_dict[char[0]] * scale_factor
        P_coords[char[0]] = [angle, freq]
        R_coords[char[0]] = [radme(angle, 'cos') * freq_scaled,
                             radme(angle, 'sin') * freq_scaled]
        angle = angle + char_sep
    return R_coords


def open_file(filename):
    """ Should really break this up, and not gulp entire file at once. But
    for now, will leave the read() alone.
    :FIXME: Optimization,  Security:""" 
    _input = open(filename)

    data = _input.read()
    data = string.strip(data)
    _input.close()
    #size = len(data)
    return data


def massage(data):
    """ Pass the data, one big string, to build_list, get a dict back.""" 
    symbols_used = build_list(data)
    size = len(symbols_used.keys())
    char_sep = 360.0 / size  # Deg seperation between symbols on chart.

# The Postscript stuff. Hand off the data, and the xy coords to be
# written into the postscript file.

    rect_coords = build_coords(symbols_used, char_sep)
    build_postscript(rect_coords)

# Supporting functions.


def radme(deg, func):
    """need degrees for the postscript stuff, python mathlib deals with
    radians of course. """
    if func == 'cos':
        deg_real = math.cos(deg * math.pi / 180)
    if func == 'sin':
        deg_real = math.sin(deg * math.pi / 180)
    return deg_real

def build_postscript(rect_coords):
    """ We have to take the frequency of symbol use value in symbol_dict, and
 convert that first to a polar radius value, (using char_sep, and
 incrementing it for the angle) then convert that polar coord pair,
 into rect coords for postscript. """
    output_file = args.output
    output = open(output_file,'w')

#  Build the postscript file, which for now, appears on stdout.
    output.write(header())
    output.write(crosshair())
    for symbol in rect_coords.keys():
        X, Y = rect_coords[symbol]
        output.write('%3.8f cal  %3.8f cal moveto (%s) show ' % (X, Y, symbol))
    output.write(' showpage \r')
    output.close()

def crosshair():
    """ Create the crosshair reticule for the display """
    target = """
        /crosshair {
                gsave
                newpath
                /Radius 2 def
                % Draw circle around 0 0
                0 0 Radius 72 mul 0 360 arc stroke

                0 cal   1 cal  moveto
                0 cal -1 cal lineto
                1  cal 0 cal moveto
                -1 cal  0 cal  lineto
                stroke
                grestore
                } def
        crosshair """
    return target


def header():
    """ Build the postscript header"""
    ps_header = """%!PS-Adobe-3.0
%%DocumentData: Clean7Bit
%%Orientation: Portrait
%%Pages: 1
%%PageOrder: Ascend
%%Title: PackingList
%%EndComments
/cm {25.4 mul} def
/cal {250 mul} def
/Times-Roman findfont 12 scalefont setfont
10 cm 15 cm translate
"""
    return ps_header


def run():
    """ The run() function, start here, note, there are no relevant args yet"""
    if args.inputfile:
        name = args.inputfile
    else:
        # No filename given, ask for one. Note buffer overrun
        # possibility. Also, this takes pathname as part of filename,
        # bigtime doubleplusungood   :FIXME:
        name = str(raw_input(' need a filename please! : '))

    data = open_file(name)
    massage(data)


if __name__ == "__main__":
    # This is where we will begin when called from CLI. No need for argparse
    # unless being called interactively, so import it here, or at least, in
    # get_options
    args = get_options()
    run()
