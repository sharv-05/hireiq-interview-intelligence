from io import BytesIO

def normalize_audio(raw: bytes, filename: str = "response.webm") -> bytes:
    """Normalize an uploaded browser recording when PyDub/ffmpeg are available.

    The API can still run in demo mode without codecs; production workers should call
    this before chunking and passing audio to a Whisper-compatible transcriber.
    """
    try:
        from pydub import AudioSegment
        audio=AudioSegment.from_file(BytesIO(raw), format=filename.rsplit('.',1)[-1])
        audio=audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        out=BytesIO(); audio.export(out,format='wav'); return out.getvalue()
    except Exception:
        return raw
