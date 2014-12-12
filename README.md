Old code that takes an 8bit ascii file, and presents a graphical
visualization of symbol frequency in the supplied text.

Output is via postscript file, default name ./output.ps



optional arguments:
  -h, --help            show this help message and exit
  -f INPUTFILE, --file INPUTFILE
                        Input file
  -o OUTPUT, --output OUTPUT
                        output file
  -d, --debug           enable debugging



e.g.
./textmap.py  -f <input file>

It's pretty crude, but kindof fun to see how patterns emerge from text, either
raw, or encrypted.

