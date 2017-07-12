#!/usr/bin/env python

"""
Extracts a portion of the PDB file, from atom i (to atom j). Slices are inclusive.

usage: python pdb_aslice.py <i>:<j> <pdb file>
examples: python pdb_aslice.py 1:10 1CTF.pdb # Extracts atoms 1 to 10
          python pdb_aslice.py 1: 1CTF.pdb # Extracts atoms 1 to END
          python pdb_aslice.py :10 1CTF.pdb # Extracts atoms from START to 10.

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

import os
import re
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if not len(args):
        sys.stderr.write(USAGE)
        sys.exit(1)
    elif len(args) == 1:
        # Resi & Pipe _or_ file & no aslice
        if re.match('[\-0-9]*:[\-0-9]*', args[0]):
            aslice = args[0]
            if not sys.stdin.isatty():
                pdbfh = sys.stdin
            else:
                sys.stderr.write(USAGE)
                sys.exit(1)
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 2:
        # Option & File
        if not re.match('[\-0-9]*:[\-0-9]*', args[0]):
            sys.stderr.write('Invalid slice: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        if not os.path.isfile(args[1]):
            sys.stderr.write('File not found: ' + args[1] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        aslice = args[0]
        pdbfh = open(args[1], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    # Parse st and end of slice
    bits = [b for b in aslice.split(':') if b.strip()]
    if len(bits) == 2:
        st_slice, en_slice = map(int, bits)
    elif len(bits) == 1 and aslice[0] == ':':
        st_slice = -9999
        en_slice = int(bits[0])
    elif len(bits) == 1 and aslice[-1] == ':':
        st_slice = int(bits[0])
        en_slice = 999999
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return ((st_slice, en_slice), pdbfh)

def _slice_pdb(fhandle, aslice):
    """Enclosing logic in a function to speed up a bit"""

    st_slice, en_slice = aslice

    prev_resi = None
    for line in fhandle:
        if line.startswith(('ATOM', 'HETATM')):
            if st_slice <= int(line[6:11]) <= en_slice:
                yield line
        elif line.startswith('TER'):
            if len(line) >= 26:
                if st_slice <= int(line[6:11]) <= en_slice:
                    yield line
            elif prev_resi and st_slice <= prev_resi <= en_slice:
                yield line

        if line.startswith(('ATOM', 'HETATM', 'TER')) and len(line) >= 26:
            prev_resi = int(line[6:11])

if __name__ == '__main__':

    # Check Input
    aslice, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _slice_pdb(pdbfh, aslice)

    try:
        sys.stdout.write(''.join(new_pdb))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)
