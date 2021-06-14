from pathlib import Path
import json
from converter.subtitles import WordSequence, Word
import argparse
from urllib.parse import urlparse

parser = argparse.ArgumentParser(description='Convert Google transcript to .srt file')
parser.add_argument(
    '-i',
    '--input',
    type=str,
    help='JSON transcript, either gs uri or local file',
)
parser.add_argument(
    '-o',
    '--output',
    type=Path,
    help='Output file',
)
parser.add_argument(
    '-m',
    '--method',
    type=str,
    choices=['single', 'cps', 'raw'],
    default='single',
    help='Splitting method',
)

def read_document(uri):
    if uri.startswith('gs://'):
        from google.cloud import storage
        storage_client = storage.Client()
        url = urlparse(uri)
        bucket = storage_client.bucket(url.netloc)
        blob = bucket.blob(url.path)
        document = json.loads(blob.download_as_string())
    else:
        pth = Path(uri)
        if not pth.is_file():
            raise argparse.ArgumentError('Input is not a filepath')
        document = json.loads(pth.read_text())
    return document



if __name__ == "__main__":
    args = parser.parse_args()
    print('Reading transcript')
    document = read_document(args.input)

    print('Compiling Subtitles')
    if args.method == 'single':
        subgroups = [
            WordSequence([Word(**w)]) 
            for result in document['results'] 
            for w in result['alternatives'][0]['words']
        ]
    elif args.method == 'raw':
        subgroups = [
            WordSequence([Word(**w) for w in result['alternatives'][0]['words']])
            for result in document['results']
        ]
    else:
        raise NotImplemented(f'{args.method} mode not implemented')
    
    print('Writing subtitle file')
    with args.output.open('w') as f:
        for i, group in enumerate(subgroups, start=1):
            f.write(f'\n{i}\n')
            f.write(group.srt())
    print('done')
