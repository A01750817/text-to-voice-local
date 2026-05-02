# Text Narrador

Text Narrador is a lightweight clipboard-to-speech app for Windows that reads copied text aloud using Kokoro ONNX.

It monitors your clipboard, opens a small floating UI near your cursor, detects language (`es` / `en-us`), and narrates the text with the selected voice.

## Features

- Clipboard monitoring in real time
- Floating mini UI to confirm language before reading
- Automatic language detection with manual override
- System tray icon for background usage
- Fast local TTS with Kokoro ONNX

## How It Works

1. Start the app with `python main.py`
2. Copy text from any app
3. Text Narrador detects the clipboard change
4. A compact UI appears near the mouse position
5. Press `Narrar` (or `Enter`) to play audio

## Requirements

- Python 3.10+
- Windows (tested in Windows/WSL development setup)
- Kokoro model files:
  - `kokoro-v1.0.onnx`
  - `voices-v1.0.bin`

Install dependencies:

```bash
pip install kokoro-onnx sounddevice pyperclip langid pynput pystray pillow numpy
```

Download model assets from:
- https://github.com/thewh1teagle/kokoro-onnx/releases

> [!IMPORTANT]
> Place `kokoro-v1.0.onnx` and `voices-v1.0.bin` in the project root (same folder as `main.py`).

## Quick Start

```bash
python main.py
```

Console output should show:
- `Kokoro cargado correctamente`
- `Narrador activo...`

To exit:
- Use the tray menu `Salir`, or
- Stop from terminal with `Ctrl+C`

## Voice Configuration

| Language | Voice |
| --- | --- |
| Spanish (`es`) | `ef_dora` |
| English (`en-us`) | `af_bella` |

## Project Structure

- `main.py`: app entrypoint (clipboard monitor, UI, TTS, tray)
- `test.py`: small Windows mouse-state test script
- `README.md`: documentation

## Notes

- First run can be slower due to model warmup
- Clipboard text shorter than 4 chars is ignored
- The UI auto-closes after a few seconds if no action is taken

> [!TIP]
> If audio does not play, verify your output device and check `sounddevice` installation/drivers.
