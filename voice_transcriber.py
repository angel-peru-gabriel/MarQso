# voice_transcriber.py
# Módulo OPCIONAL para transcribir voz con Whisper.
# Si las dependencias no están instaladas, VOICE_AVAILABLE=False
# y las funciones devuelven None o lanzan una excepción clara.

from typing import Optional

class VoiceFeatureDisabled(RuntimeError):
    """Señaliza que la función de voz no está disponible en este despliegue."""
    pass

VOICE_AVAILABLE = False
try:
    import io
    import ffmpeg
    import numpy as np
    from scipy.io import wavfile
    import whisper
    VOICE_AVAILABLE = True
except Exception:
    # Mantener VOICE_AVAILABLE = False sin romper las importaciones
    pass


def _ogg_to_float32_array(ogg_bytes: bytes, sr: int = 16000):
    """Convierte OGG/Opus → ndarray float32 16 kHz mono (Whisper-ready)."""
    if not VOICE_AVAILABLE:
        raise VoiceFeatureDisabled("Whisper no disponible en este despliegue.")
    wav_bytes, _ = (
        ffmpeg
        .input('pipe:0')
        .output('pipe:1', format='wav', ac=1, ar=str(sr))
        .overwrite_output()
        .run(capture_stdout=True, input=ogg_bytes, quiet=True)
    )
    sr_read, data = wavfile.read(io.BytesIO(wav_bytes))
    if sr_read != sr:
        raise ValueError(f"Sample-rate mismatch ({sr_read} vs {sr})")
    if data.dtype != np.float32:
        data = data.astype(np.float32) / np.iinfo(data.dtype).max
    return data


_whisper_model = None
def transcribe_ogg_bytes(ogg_bytes: bytes, language: str = 'es', model_name: str = 'small') -> Optional[str]:
    """
    Devuelve el texto transcrito o None si VOICE_AVAILABLE == False.
    No toca disco; trabaja todo en RAM.
    """
    if not VOICE_AVAILABLE:
        return None
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model(model_name)
    audio_np = _ogg_to_float32_array(ogg_bytes)
    result = _whisper_model.transcribe(audio_np, language=language) or {}
    return (result.get("text") or "").strip()
