# -*- coding: utf-8 -*-
from dataclasses import dataclass
from pathlib import Path
import argparse
import sys
import re

from tqdm import tqdm
import colorama
import pdb

VERSION = '1.0'     # версия
SYMBOL  = 'X'       # любой символ в маске
LENGTH  = 59        # длина маски и ключа


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
@dataclass(frozen=True)
class Constans(object):
    RESET:          str = colorama.Style.RESET_ALL
    WHITE:          str = colorama.Style.BRIGHT + colorama.Fore.WHITE
    RED:            str = colorama.Style.BRIGHT + colorama.Fore.RED

    NOT_FOUND:      str = 'Файл %s не найден.'
    ALREADY_EXISTS: str = 'Файл %s уже существует. Перезаписать? (y/n): '
    LENGTH_MASK:    str = 'Длина маски не равна %d символам' % LENGTH
    ERROR:          str = RED + 'ОШИБКА:' + RESET


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class ProgressBar(tqdm):
    def __init__(self, total, it='b'):
        kwargs = {'total': total, 'unit': it, 'unit_scale': True, 'ascii': ' ░░░░▒▒▓▓██'}
        tqdm.__init__(self, **kwargs)


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class Sieve(Constans):
    def __init__(self, namespace):
        self.ifile = Path(namespace.ifile)
        self.mfile = Path(namespace.mfile)
        self.ofile = Path(namespace.ofile)
        self.mask  = f'{namespace.mask}\n'
        self.count = 0

        if (problem := self.error_checking()):
            self.error(problem)
            raise SystemExit

        # +2 - '/r/n'
        self.lines = self.ifile.stat().st_size // (LENGTH + 2)


    #---------------------------------------------------------------------------
    def paint(self, color, text):
        return f'{color}{text}{self.RESET}'


    #---------------------------------------------------------------------------
    def error(self, problem):
        print(f'{self.ERROR} {problem}')
        raise SystemExit


    #---------------------------------------------------------------------------
    def error_checking(self, problem=''):
        if not self.ifile.exists():
            problem = self.NOT_FOUND % self.paint(self.WHITE, str(self.ifile))

        if len(self.mask) != (LENGTH + 1):
            problem = self.LENGTH_MASK

        return problem


    #---------------------------------------------------------------------------
    def run(self):
        pattern = re.compile(self.mask.replace(SYMBOL, '.'))
        ifile = open(self.ifile, 'rt')
        mfile = open(self.mfile, 'wt')
        ofile = open(self.ofile, 'wt')

        progressbar = ProgressBar(total=self.lines)

        while (line := ifile.readline()):
            progressbar.update(1)

            if pattern.fullmatch(line):
                mfile.write(line)
                self.count += 1
            else:
                ofile.write(line)

        progressbar.close()

        ifile.close()
        mfile.close()
        ofile.close()

        print(f'\nМаска:      {self.paint(self.WHITE, self.mask)}', end='')
        print(f'Всего:      {self.paint(self.WHITE, str(self.lines))}')
        print(f'Совпадений: {self.paint(self.WHITE, str(self.count))}')


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='sievekeys')
    parser.add_argument('ifile', help='input file')
    parser.add_argument('mfile', help='file with matching keys')
    parser.add_argument('ofile', help='file with other keys')
    parser.add_argument('mask', help='key mask')

    colorama.init(autoreset=True)
    namespace = parser.parse_args()

    Sieve(namespace).run()
