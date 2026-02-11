import os
import time
import pickle
import numpy as np

# Audio + features
import sounddevice as sd
from scipy.io.wavfile import write as wav_write
import librosa

# ------------ Config ------------
SAMPLE_RATE = 16000   # 16 kHz mono
DURATION_SEC = 4      # record ~4 seconds
N_MFCC = 20           # number of MFCCs to use
VOICEPRINT_DIRNAME = "voiceprints"  # folder to store .pkl and .wav
# --------------------------------


def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def record_audio(duration=DURATION_SEC, sr=SAMPLE_RATE) -> np.ndarray:
    """
    Records mono audio from the default microphone.
    Returns float32 numpy array in range [-1, 1].
    """
    print(f"\nRecording for {duration} seconds at {sr} Hz...")
    recording = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype="float32")
    sd.wait()
    # shape (samples, 1) -> (samples,)
    return recording[:, 0]


def extract_mfcc_features(y: np.ndarray, sr: int, n_mfcc: int = N_MFCC):
    """
    Compute MFCC-based fixed-length embedding: mean + std over time.
    """
    # simple pre-emphasis
    y = np.append(y[0], y[1:] - 0.97 * y[:-1])
    # safety: trim leading/trailing silence (optional)
    y, _ = librosa.effects.trim(y, top_db=30)

    # MFCCs over frames
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    # Also add deltas for a bit more robustness
    d_mfcc = librosa.feature.delta(mfcc)
    dd_mfcc = librosa.feature.delta(mfcc, order=2)

    # Stack [mfcc; delta; delta-delta] -> (3*n_mfcc, frames)
    feat = np.vstack([mfcc, d_mfcc, dd_mfcc])

    # Aggregate over time: mean and std -> (2 * 3*n_mfcc,)
    mean = np.mean(feat, axis=1)
    std = np.std(feat, axis=1)
    embedding = np.concatenate([mean, std], axis=0).astype("float32")
    return embedding


def main():
    print("=== Voice Enrollment ===")
    print("This will capture your voice saying the word 'Present' (or any short phrase),")
    print("and save a voiceprint linked to your roll number.\n")

    roll_no = input("Enter Roll No (e.g., 202301): ").strip()
    name = input("Enter Name (exactly as in students.csv): ").strip()

    if not roll_no:
        print("Roll No is required.")
        return
    if not name:
        print("Name is required.")
        return

    base_dir = os.path.dirname(__file__)
    voice_dir = os.path.join(base_dir, VOICEPRINT_DIRNAME)
    ensure_dir(voice_dir)

    # Countdown to avoid capturing keyboard noise
    print("\nGet ready. Please be in a quiet environment.")
    for i in [3, 2, 1]:
        print(f"... {i}")
        time.sleep(1)

    print("Please say clearly: 'Present'")
    y = record_audio(duration=DURATION_SEC, sr=SAMPLE_RATE)

    # Save raw WAV for reference (optional but handy)
    wav_path = os.path.join(voice_dir, f"{roll_no}.wav")
    # Convert float32 [-1,1] -> int16
    y_int16 = np.clip(y * 32767, -32768, 32767).astype(np.int16)
    wav_write(wav_path, SAMPLE_RATE, y_int16)

    # Extract features
    embedding = extract_mfcc_features(y=y, sr=SAMPLE_RATE, n_mfcc=N_MFCC)

    # Package voiceprint data
    voiceprint = {
        "roll_no": roll_no,
        "name": name,
        "sr": SAMPLE_RATE,
        "n_mfcc": N_MFCC,
        "embedding": embedding,   # (2*3*N_MFCC,) float32
        "wav_path": wav_path
    }

    pkl_path = os.path.join(voice_dir, f"{roll_no}.pkl")
    with open(pkl_path, "wb") as f:
        pickle.dump(voiceprint, f)

    print(f"\n✅ Saved voiceprint for {name} ({roll_no})")
    print(f" - WAV: {wav_path}")
    print(f" - PKL: {pkl_path}")
    print("\nYou can now run the attendance script that checks face + voice.")


if __name__ == "__main__":
    main()
