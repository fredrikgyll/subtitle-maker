import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from converter.subtitles import Subtitle, Word, WordSequence

parser = argparse.ArgumentParser(description='Convert Google transcript to .srt file')
parser.add_argument(
    '-i',
    '--input',
    type=str,
    help='JSON transcript, either gs uri or local file',
)
parser.add_argument(
    '-m',
    '--method',
    type=str,
    choices=['single', 'pause', 'cps', 'raw'],
    default='single',
    help='Splitting method',
)
parser.add_argument(
    '-c',
    '--cps',
    type=float,
    help='Target characters per sec to split on',
)
parser.add_argument(
    '-f',
    type=float,
    help='Force break when pause exceeds this value',
    default=2.0,
)
parser.add_argument(
    'output',
    type=Path,
    help='Output file',
)


def read_document(uri: str):
    if uri.startswith('gs://'):
        from google.cloud import storage

        storage_client = storage.Client()
        url = urlparse(uri)
        bucket = storage_client.bucket(url.netloc)
        blob = bucket.blob(url.path[1:])
        document = json.loads(blob.download_as_string())
    else:
        pth = Path(uri)
        if not pth.is_file():
            raise argparse.ArgumentError('Input is not a filepath')
        document = json.loads(pth.read_text())
    return document


def write_srt(subgroups: list[WordSequence], file: Path):
    with file.open('w') as f:
        for i, group in enumerate(subgroups, start=1):
            f.write(f'{i}\n')
            f.write(group.srt())


if __name__ == "__main__":
    args = parser.parse_args()
    print('Reading transcript')
    document = read_document(args.input)

    print('Compiling Subtitles')
    subgroups: list[Subtitle] = []
    if args.method in ['single', 'pause']:
        groups = [
            Word(**w)
            for result in document['results']
            for w in result['alternatives'][0]['words']
        ]
        if args.method == 'pause':
            thresh = args.f
            temp_group = []
            for word in groups:
                if word.duration > thresh:
                    if temp_group:
                        subgroups.append(WordSequence(temp_group))
                    word.start.shift(word.duration - 1)
                    temp_group = [word]
                temp_group.append(word)
            if temp_group:
                subgroups.append(WordSequence(temp_group))
        else:
            subgroups = groups
    elif args.method == 'raw':
        subgroups = [
            WordSequence([Word(**w) for w in result['alternatives'][0]['words']])
            for result in document['results']
        ]
    else:
        raise NotImplementedError(f'{args.method} mode not implemented')

    print('Writing subtitle file')
    write_srt(subgroups, args.output)
    print('done')
