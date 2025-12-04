import requests
import time
import os
import math
import struct
import random

BASE_URL = "http://localhost:8000/api/v1"
SESSION_ID = "test_session_realtime_01"

def generate_sine_wave_pcm(duration_sec=1.0, sample_rate=16000, frequency=440.0):
    """
    Generate a simple sine wave PCM audio (16-bit, Mono, 16kHz)
    """
    num_samples = int(duration_sec * sample_rate)
    audio_data = bytearray()
    for i in range(num_samples):
        sample = 32767 * math.sin(2 * math.pi * frequency * i / sample_rate)
        audio_data.extend(struct.pack('<h', int(sample)))
    return bytes(audio_data)

def send_audio_chunk(speaker_role, audio_data, chunk_index):
    url = f"{BASE_URL}/p2p/audio"
    files = {
        'file': (f'chunk_{chunk_index}.pcm', audio_data, 'application/octet-stream')
    }
    data = {
        'speaker_role': speaker_role
    }
    
    print(f"Sending Chunk {chunk_index} | Speaker: {speaker_role} | Size: {len(audio_data)} bytes")
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print(f" -> Success: {response.json()}")
        else:
            print(f" -> Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" -> Error: {e}")

def generate_report():
    url = f"{BASE_URL}/p2p/report"
    print(f"\nGenerating Report")
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print(f" -> Report Generated Successfully!")
            print(response.json())
        else:
            print(f" -> Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" -> Error: {e}")

def main():
    print(f"Starting P2P Realtime Test (Single Session)")
    
    # 1. Interviewer speaks (Chunks 1, 2)
    # Using 440Hz (A4) for Interviewer
    chunk1 = generate_sine_wave_pcm(duration_sec=2.0, frequency=440.0)
    send_audio_chunk("interviewer", chunk1, 1)
    time.sleep(0.5)
    
    chunk2 = generate_sine_wave_pcm(duration_sec=2.0, frequency=440.0)
    send_audio_chunk("interviewer", chunk2, 2)
    time.sleep(0.5)
    
    # 2. Candidate speaks (Chunk 3) -> Should trigger STT for Interviewer
    # Using 880Hz (A5) for Candidate
    chunk3 = generate_sine_wave_pcm(duration_sec=3.0, frequency=880.0)
    send_audio_chunk("candidate", chunk3, 3)
    time.sleep(0.5)
    
    # 3. Interviewer speaks again (Chunk 4) -> Should trigger STT for Candidate
    chunk4 = generate_sine_wave_pcm(duration_sec=2.0, frequency=440.0)
    send_audio_chunk("interviewer", chunk4, 4)
    time.sleep(0.5)
    
    # 4. End Session & Report
    generate_report()

if __name__ == "__main__":
    main()
