#!/usr/bin/env  python
###
# Copyright (c) 2006, Jim Richardson <weaselkeeper@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

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
# Setting some constants
good_symbols = string.digits + string.letters


def get_options():
    """ Parse for any options """
    log.debug('in get_options')
    import argparse
    parser = argparse.ArgumentParser(
        description='This is a data visualization aide.')
    parser.add_argument('-f', '--file', action='store', default=None,
        help='Input file', dest='inputfile')
    parser.add_argument('-o', '--output', action='store', default='output.ps',
        help='output file')
    parser.add_argument('-d', '--debug', action='store_true',
        help='enable debugging')
    _args = parser.parse_args()
    _args.usage = PROJECTNAME + ".py [options]"
    log.debug('leaving get_options')
    return _args


def get_biggest(_dict):
    """ calculate the largest offset, and divide all offsets by one tenth
     of it, in order to get a 0 to 10 spread so that all the files run
     through this will be in roughly the same scale. """
    log.debug('in get_biggest')
    _list = []
    for item in _dict.keys():
        _list.append(_dict[item])
    _list.sort()

    temp = [_list.pop(0) * -1, _list.pop()]
    temp.sort()
    log.debug('leaving get_biggest')
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
    log.debug('in build_list')
    symbol_count = {}

    for symbol in good_symbols:
        symbol_count[symbol] = 0

    for symbol in dataset:
        if good_symbols.count(symbol):
            symbol_count[symbol] = symbol_count.get(symbol, [0]) + 1
    log.debug('leaving build_list')
    return symbol_count


def build_coords(symbol_dict, char_sep):
    """ Create a list of the coords for the charmap"""
    log.debug('in build_coords')
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
            scale_factor = 100.0 / biggest
    log.debug("Final scale factor is %s and biggest is %s", scale_factor,
              biggest)
    for char in sorted_list:
        freq_scaled = symbol_dict[char[0]] * scale_factor
        P_coords[char[0]] = [angle, freq]
        R_coords[char[0]] = [radme(angle, 'cos') * freq_scaled,
                             radme(angle, 'sin') * freq_scaled]
        angle = angle + char_sep
    log.debug('leaving build_coords')
    return R_coords


def open_file(filename):
    """ Should really break this up, and not gulp entire file at once. But
    for now, will leave the read() alone.  """
    log.debug('in open_file')
    _input = open(filename)

    data = _input.read().strip()
    _input.close()
    #size = len(data)
    log.debug('leaving open_file')
    return data


def massage(data):
    """ Pass the data, one big string, to build_list, get a dict back."""
    log.debug('in massage')
    symbols_used = build_list(data)
    size = len(symbols_used.keys())
    char_sep = 360.0 / size  # Deg seperation between symbols on chart.

# The Postscript stuff. Hand off the data, and the xy coords to be
# written into the postscript file.

    rect_coords = build_coords(symbols_used, char_sep)
    build_postscript(rect_coords)

# Supporting functions.
    log.debug('leaving massage')


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
    log.debug('in build_postscript')
    output_file = args.output
    output = open(output_file, 'w')

#  Build the postscript file, which for now, appears on stdout.
    output.write(header())
    output.write(crosshair())
    for sym in rect_coords.keys():
        X, Y = rect_coords[sym]
        log.debug("X and Y are %3.8f and %3.8f", X, Y)
        if X and Y != 0.00000000:
            output.write('%3.8f cal  %3.8f cal moveto (%s) show ' % (X, Y, sym))
        else:
            log.debug("zero count for symbol %s", sym)
    output.write(' showpage \r')
    output.close()
    log.debug('leaving build_postscript')

def crosshair():
    """ Create the crosshair reticule for the display """
    log.debug('in crosshair')
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
    log.debug('leaving crosshair')
    return target


def header():
    """ Build the postscript header"""
    log.debug('in header')
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
    log.debug('leaving header')
    return ps_header


def run():
    """ The run() function, start here, note, there are no relevant args yet"""
    log.debug('in run')
    if args.inputfile:
        name = args.inputfile
    else:
        # No filename given, ask for one. Note buffer overrun
        # possibility. Also, this takes pathname as part of filename,
        # bigtime doubleplusungood
        name = str(raw_input(' need a filename please! : '))

    data = open_file(name)
    massage(data)
    log.debug('leaving run')


if __name__ == "__main__":
    # This is where we will begin when called from CLI. No need for argparse
    # unless being called interactively, so import it here, or at least, in
    # get_options
    args = get_options()

    if args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARN)

    sys.exit(run())
