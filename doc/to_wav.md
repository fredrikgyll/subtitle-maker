# Transcription workflow
This is a proposed workflow for automated captioning using Google Cloud Speach-to-Text


## Preprocessing audio for Speech-to-Text

[This guide from Google](https://cloud.google.com/speech-to-text/docs/encoding) explains what format to use to get the best results.

Use `ffmpeg` to extraxt the audio from a videofile with [these arguments](https://superuser.com/questions/609740/extracting-wav-from-mp4-while-preserving-the-highest-possible-quality):

- `-vn` -- Remove video stream.
- `-acodec pcm_s16le` -- linear 16bit pcm encoding to use with gcloud in `LINEAR16` mode.
- `-ar 16000` -- Sample rate of 16kHz, set this to the sample rate of the source, and adjust `sample_rate_hertz`.
- `-ac 1` -- single channel (mono) output.

```zsh
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audiofile01.wav
```

Stroage required is `sample_rate * 2 * 3600 * hours_of_video` bytes, e.g:

- 1 hour at 44.1 kHz = 302 MB
- 1 hour at 16 kHz = 110 MB

## Uploading audio to Google Storage
push the audio WAV file to the google storage bucket

```zsh
gsutil cp audiofile01.wav gs://nkul-subtitles
```

## Run transcribtion task async
This will order a transcription to be done. When completed, the result is uploaded to the bucket automatically

Create the following request payload:

```json
# request.json
{
  "config": {
      "encoding":"LINEAR16",
      "sampleRateHertz": 44100,
      "languageCode": "en-US",
      "enableWordTimeOffsets": true,
      "enableAutomaticPunctuation": true
  },
  "output_config": {
     "gcs_uri":"gs://nkul-subtitles/caption01.json"
  },
  "audio": {
      "uri":"gs://nkul-subtitles/audiofile01.wav"
  }
}
```

Run the task:
```zsh
curl -s -H "Content-Type: application/json" \
    -H "Authorization: Bearer "$(gcloud auth application-default print-access-token) \
 	"https://speech.googleapis.com/v1p1beta1/speech:longrunningrecognize" \
	-d @request.json
```

if succesfull the task ID will be returned:

```json
{
  "name": "9121852626090255257"
}
```

check on the task with,

```zsh
gcloud ml speech operations describe 9121852626090255257
```

