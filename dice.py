#!/usr/bin/env python3
import argparse
import binascii
import curses
import hashlib
import os
import sys


D6 = '123456'
D8 = '12345678'
SEED_WORDS = []
with open('english.txt') as f:
    SEED_WORDS = f.read().splitlines()


def dice2n(n_str, digits):
    basem = 1
    n = 0
    for c in n_str:
        n += (digits.index(c)) * basem
        basem = basem*len(digits)
    return n


def n2dice(n, digits):
    chars = []
    while n > 0:
        n, d = divmod(n, len(digits))
        chars.append(digits[d])
    return ''.join(chars)


def _seed_checksum(s):
    """return checksum bin from binary input string"""
    _bytes = int(s, 2).to_bytes(len(s) // 8)
    _sha = hashlib.sha256(_bytes).hexdigest()
    return format(int(_sha[0:2], 16), '08b')


def dice_to_seed_phrase(n_str, digits, seed_words):
    """ generate seed phrase from dice rolls
    """
    entropy_number = dice2n(n_str, digits)
    entropy_bin = format(entropy_number, '0256b')[:256]
    seed_bin = entropy_bin + _seed_checksum(entropy_bin)
    return [seed_words[int(seed_bin[x:x+11],2)] for x in range(0,264,11)]


def _prompt(seed_words=SEED_WORDS, digits=D6):
    if len(set(digits)) != len(digits):
        return "digits need to be unique"
    stdscr = curses.initscr()
    rolls_needed = len(n2dice(2**256-1, digits))
    rolls = []
    _seeds = ['abandon'] * 24
    _ent = 1
    while len(rolls) < rolls_needed:
        stdscr.erase()
        stdscr.addstr(0, 0, f"Entering {len(rolls)+1}/{rolls_needed} dice roll: ")
        _y, _x = stdscr.getyx()
        stdscr.addstr(1, 0, f"-> {''.join(rolls)}")
        _seeds = dice_to_seed_phrase(''.join(rolls), digits, seed_words)
        _ent = len(bin( dice2n(digits[-1]*len(rolls), digits) )[2:])
        stdscr.addstr(3, 0, f"estimated entropy <{_ent}-bits")
        _seed_phrase = '\n'.join(_seeds)
        stdscr.addstr(5, 0, _seed_phrase)
        stdscr.move(_y, _x)
        stdscr.refresh()
        _raw = stdscr.getch()
        if chr(_raw) in digits:
            rolls.append(chr(_raw))
    curses.endwin()
    final_seeds = dice_to_seed_phrase(''.join(rolls), digits, seed_words)
    return ''.join(rolls) + '\n' + ' '.join(final_seeds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--digits", type=int, default=6, help="increase output verbosity")
    parser.add_argument("-L", "--language-file", default='english.txt', help="increase output verbosity")
    args = parser.parse_args()
    _d = D6
    if args.digits == 8:
        _d = D8
    _sw = []
    if  os.path.isfile(args.language_file):
        with open(args.language_file) as f:
            _sw = f.read().splitlines()
    else:
        print('Please specify a valid language file', file=sys.stderr)
        sys.exit(-1)
    print(_prompt(seed_words=_sw, digits=_d))



