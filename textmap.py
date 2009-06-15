#!/usr/bin/env  python

# Copyright Jim Richardson, <warlock@eskimo.com> 2000

# This is a data visualization aide. It takes a filename  ( 8 bit ascii only
# please), and calculates the relative frequency of each symbol, then
# graphically represents how often the symbol appears in the text, by
# placing each symbol from the text, in a circle, the distance from the
# center, being related to how frequent the symbol occurs. So if you
# have text, which consists of only the letter e (100 times) and the
# letter m (once) m will appear in the center, and e, on the edge of the
# scale. If there is a letter l, which appears 50 times, it will appear
# halfway between e and m, but displaced radially. Compare the
# differences between plaintext, random symbols, and ciphertext. Scale
# is adjusted automatically, to fit all symbols on a letter size page in
# the postscript output.


Changelog="""

Dec 1  2003, Rev 0.01: initial version.
Dec 12 2003, Rev 0.02: Changes to catch errors in input.
Dec 29 2005, Rev 0.03: Rewrite a lot, including the rect-polar
                       conversion
Dec 30 2005, Rev 0.04: Fix div/0 error for datasets that don't use all
symbols available in good_symbols. 

"""

import os,sys,math,string
def get_biggest(dict):
    list=[]
    for item in dict.keys():
        list.append(dict[item])
    list.sort()
    # calculate the largest offset, and divide all offsets by one tenth
    # of it, in order to get a 0 to 10 spread so that all the files run
    # through this will be in roughly the same scale. 

    temp=[list.pop(0)*-1,list.pop()]
    temp.sort()
    return temp.pop()
    
    
def build_list(dataset):
# Pass this a string or tuple of characters, get back a dict, of
# char:number where number is the number of times that char occurs in
# the dataset 

# We chop off cr/lf, and
# whitespace. In fact, anything other than numerical, alphabetical are
# pulled. All we care about are the actual symbols.  See good_symbols
# for details on what we want to play with. Adjust accordingly.

# First, we strip out bad_symbols, which are anything not in 
# good_symbols. Then we fill a dict with everything from plaintext that
# is also present in good symbols, and set the value to 0 to start the
# ball rolling. If you change good_symbols, be wary of stuff like \
# which are postscript operators and must be dealt with or your output
# will not be correct. 

    good_symbols=string.digits+string.letters
    symbol_count={}
    
    for symbol in good_symbols:
        symbol_count[symbol]=0
    
    for symbol in dataset:
        if good_symbols.count(symbol):
            symbol_count[symbol]=symbol_count.get(symbol,[0])+1
    
    return symbol_count

def build_coords(symbol_dict,char_sep):
    angle=0
    R_coords={}
    P_coords={}
    biggest=0
    for char in symbol_dict.keys():
        freq=symbol_dict[char]
        if biggest<freq:
            biggest=freq
        if biggest:
            scale_factor=1.0/biggest
        
    for char in symbol_dict.keys():
        freq_scaled=symbol_dict[char]*scale_factor
        P_coords[char]=[angle,freq]
        R_coords[char]=[cos_rad(angle)*freq_scaled,sin_rad(angle)*freq_scaled]
        angle=angle+char_sep
    return R_coords
    
 
def open_file(filename):
    input = open(filename)
# Should really break this up, and not gulp entire file at once. But
# for now, will leave the read() alone.  
# :FIXME: Optimization,  Security:

    data=input.read() 
    data=string.strip(data)
    input.close()
    size=len(data)
    return data
 
def massage(data):
# Pass the data, one big string, to build_list, get a dict back. 
    symbols_used=build_list(data)
    size=len(symbols_used.keys()) 
    
    char_sep=360.0/size # Deg seperation between symbols on chart.

# The Postscript stuff. Hand off the data, and the xy coords to be
# written into the postscript file. 
  
    rect_coords=build_coords(symbols_used,char_sep)
    build_postscript(rect_coords)



# Supporting functions. 

def sin_rad(deg):
    # need degrees for the postscript stuff, python mathlib deals with
    # radians of course.  
    deg_real = math.sin(deg * math.pi/180)
    return deg_real

def cos_rad(deg):
    deg_real = math.cos(deg*math.pi/180)
    return deg_real


def build_postscript(rect_coords):
# We have to take the frequency of symbol use value in symbol_dict, and
# convert that first to a polar radius value, (using char_sep, and
# incrementing it for the angle) then convert that polar coord pair,
# into rect coords for postscript.

#  Build the postscript file, which for now, appears on stdout. 
    print header()   
    print crosshair()
    for symbol in rect_coords.keys():
        X,Y=rect_coords[symbol]
        print '%3.8f cal  %3.8f cal moveto (%s) show'% (X,Y,symbol)
    print 'showpage'

def crosshair():
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
    header = """
    %!PS-Adobe-3.0
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
    return header


def main():
    try:
        if sys.argv[1]:
            name = sys.argv[1]
    except:
        IOError
        # No filename given, ask for one. Note buffer overrun
        # possibility. Also, this takes pathname as part of filename,
        # bigtime doubleplusungood   :FIXME:
        name = str(raw_input(' need a filename please! : '))

    data=open_file(name)
    massage(data)

main()

