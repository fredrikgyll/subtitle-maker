import time
from decimal import Decimal
from functools import total_ordering


@total_ordering
class Offset:
    def __init__(self, seconds=0, nanos=0):
        self.time: Decimal = (
            Decimal(seconds) + (Decimal(nanos) / Decimal(1e9)).normalize()
        )

    @property
    def seconds(self) -> int:
        return int(self.time)

    @property
    def milis(self) -> int:
        return round((self.time - self.seconds) * 1000)

    def shift(self, value):
        self.time += value

    def __str__(self) -> str:
        hhmmss = time.strftime('%H:%M:%S', time.gmtime(self.seconds))
        return f'{hhmmss},{self.milis:03d}'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        return self.time == other.time

    def __lt__(self, other) -> bool:
        return self.time < other.time


class Subtitle:
    @property
    def duration(self) -> Decimal:
        """Return duration of subtitle"""
        start, end = self.interval
        return end.time - start.time

    @property
    def interval(self) -> tuple[Offset, Offset]:
        """Return tuple of start and end times"""
        raise NotImplementedError('Not implemeted by Subclass')

    @property
    def tanscript(self) -> str:
        """Return transcript of subtitle"""
        raise NotImplementedError('Not implemeted by Subclass')

    def srt(self) -> str:
        """Return SRT blob of subtitle"""
        start, end = self.interval
        return f'{start} --> {end}\n{self.tanscript}\n\n'


class Word(Subtitle):
    def __init__(self, word: str, start_offset, end_offset):
        self.word = word
        self.start = Offset(**start_offset)
        self.end = Offset(**end_offset)

    @property
    def interval(self) -> tuple[Offset, Offset]:
        return self.start, self.end

    @property
    def tanscript(self) -> str:
        return self.word

    def __str__(self) -> str:
        return self.word

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return len(self.word)


class WordSequence(list, Subtitle):
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
    def interval(self) -> tuple[Offset, Offset]:
        if not len(self):
            raise IndexError('Empty sequence')
        return self[0].start, self[-1].end

    @property
    def tanscript(self) -> str:
        return ' '.join(str(x) for x in self)
