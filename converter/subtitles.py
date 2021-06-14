import time
from decimal import Decimal
from functools import total_ordering
from typing import List, Tuple

@total_ordering
class Offset:
    def __init__(self, seconds, nanos=0):
        self.seconds: int = seconds
        self.nanos: int = nanos
        self.time: Decimal = Decimal(seconds) + (Decimal(nanos) / Decimal(1e9)).normalize()

    def __str__(self) -> str:
        hhmmss = time.strftime('%H:%M:%S', time.gmtime(self.seconds))
        milis = self.nanos // 1000000
        return f'{hhmmss},{milis:03d}'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        return self.time == other.time
    
    def __lt__(self, other) -> bool:
        return self.time < other.time

class Word:
    def __init__(self, word: str, start_offset, end_offset):
        self.word = word
        self.start = Offset(**start_offset)
        self.end = Offset(**end_offset)

    def __str__(self) -> str:
        return self.word

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return len(self.word)

class WordSequence(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def cps(self) -> float:
        chars = self.char_len
        start, end = self.interval
        return chars / (end.time - start.time)

    @property
    def char_len(self) -> int:
        return sum([len(x) for x in self])
    
    @property
    def interval(self) -> Tuple[Offset, Offset]:
        if not len(self):
            raise IndexError('Empty sequence')
        return self[0].start, self[-1].end

    @property
    def tanscript(self) -> str:
        return ' '.join(str(x) for x in self)

    def srt(self) -> str:
        start, end = self.interval
        return f'{start} --> {end}\n{self.tanscript}\n'
