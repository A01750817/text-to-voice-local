# Text Narrador

Clipboard listener that auto-reads copied text aloud using Kokoro TTS. Detects Spanish/English per sentence and switches voices accordingly.

## How it works

1. Copy any text
2. App detects clipboard change
3. Narrates it phrase by phrase, streaming audio as it generates

## Requirements

```
pip install kokoro-onnx sounddevice pyperclip langid pywin32
```

Also needs:
- `kokoro-v1.0.onnx` — model file
- `voices-v1.0.bin` — voices file

Both available at [kokoro-onnx releases](https://github.com/thewh1teagle/kokoro-onnx/releases).

## Usage

```
python main.py
```

Runs in background. Copy text anywhere → it narrates. `Ctrl+C` to stop.

## Voices

| Language | Voice |
|----------|-------|
| Spanish  | `ef_dora` |
| English  | `af_bella` |

## Notes

- First run is slower (model warmup)
- Large `.onnx` and `.bin` files are git-ignored — download separately
