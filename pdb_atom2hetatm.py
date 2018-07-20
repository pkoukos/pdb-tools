#!/usr/bin/env python

"""
Transform all the non-standard aminoacid residue records into HETATM.

HADDOCK formatted PDB files have allthe HETATM renamed to ATOM which sometimes
causes problem with downstream analysis programs (eg PROFIT). This  script will
only print the ATOM lines whose resname is one of the standard aminoacids. The
non-ATOM/HETATM lines will not be affected.

usage: python pdb_atom2hetatm.py <pdb file>

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

RESNAMES = (
    'ALA',
    'ARG',
    'ASN',
    'ASP',
    'CYS',
    'GLN',
    'GLU',
    'GLY',
    'HIS',
    'ILE',
    'LEU',
    'LYS',
    'MET',
    'PHE',
    'PRO',
    'SER',
    'THR',
    'TRP',
    'TYR',
    'VAL'
)

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if not len(args):
        # No chain, from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        # File
        if not os.path.isfile(args[0]):
            sys.stderr.write('File not found: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        pdbfh = open(args[0], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return pdbfh

def _slice_pdb(fhandle):
    """Enclosing logic in a function to speed up a bit"""

    for line in fhandle:
        if line.startswith(('ATOM', 'HETATM')):
            if line[17:20] in RESNAMES:
                yield line
            else:
                yield "HETATM" + line[6:]
        else:
            yield line

if __name__ == '__main__':

    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _slice_pdb(pdbfh)

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
