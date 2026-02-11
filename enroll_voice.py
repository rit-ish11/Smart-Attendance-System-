import sounddevice as sd
import librosa
import numpy as np
import os

PROFILE_PATH = "voice_profile.npy"

def record_sample(seconds=3, fs=16000):
    print("🎤 Speak 'present' now...")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    return np.squeeze(audio)

def extract_mfcc(audio, fs=16000):
    mfcc = librosa.feature.mfcc(y=audio, sr=fs, n_mfcc=13)
    return np.mean(mfcc, axis=1)

if __name__ == "__main__":
    profiles = []
    for i in range(3):  # record 3 samples
        audio = record_sample()
        features = extract_mfcc(audio)
        profiles.append(features)
        print(f"✅ Sample {i+1} recorded")

    # Average profile
    voice_profile = np.mean(profiles, axis=0)
    np.save(PROFILE_PATH, voice_profile)
    print(f"🎉 Voice profile saved to {PROFILE_PATH}")
