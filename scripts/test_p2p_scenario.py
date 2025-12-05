
import requests
import time
import os
from pathlib import Path
from pydub import AudioSegment

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUDIO_DIR = Path("data/mock_interview_audio")
SAMPLE_RATE = 16000

def convert_mp3_to_pcm(file_path):
    """
    Convert MP3 file to raw PCM data (16kHz, Mono, 16-bit)
    """
    audio = AudioSegment.from_mp3(file_path)
    
    # Resample to 16kHz, Mono, 16-bit
    audio = audio.set_frame_rate(SAMPLE_RATE).set_channels(1).set_sample_width(2)
    
    return audio.raw_data

def send_audio_chunk(speaker_role, audio_data, filename):
    url = f"{BASE_URL}/p2p/audio"
    
    # Send the entire file as one chunk for simplicity in this test
    # In a real scenario, this might be split into smaller chunks
    files = {
        'file': (f'{filename}.pcm', audio_data, 'application/octet-stream')
    }
    data = {
        'speaker_role': speaker_role
    }
    
    print(f"Sending {filename} | Speaker: {speaker_role} | Size: {len(audio_data)} bytes")
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
    print(f"\nGenerating Report...")
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print(f" -> Report Generated Successfully!")
            # Print a summary of the report
            report = response.json()
            print(f"Session ID: {report.get('session_id')}")
            print(f"Human Report Preview:\n{report.get('human_report')[:200]}...")
        else:
            print(f" -> Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" -> Error: {e}")

def main():
    print(f"Starting P2P Scenario Test")
    
    if not AUDIO_DIR.exists():
        print(f"Error: Audio directory {AUDIO_DIR} does not exist.")
        return

    # Get all mp3 files sorted by name (01_..., 02_...)
    audio_files = sorted(list(AUDIO_DIR.glob("*.mp3")))
    
    if not audio_files:
        print("No audio files found.")
        return

    for file_path in audio_files:
        filename = file_path.name
        # Determine speaker from filename (e.g., "01_interviewer.mp3")
        if "interviewer" in filename:
            speaker_role = "interviewer"
        elif "candidate" in filename:
            speaker_role = "candidate"
        else:
            print(f"Skipping unknown file: {filename}")
            continue
            
        # Convert to PCM
        pcm_data = convert_mp3_to_pcm(file_path)
        
        # Send to API
        send_audio_chunk(speaker_role, pcm_data, filename)
        
        # Wait a bit to simulate real-time gap (optional, but good for log readability)
        time.sleep(0.5)

    # Generate Report
    generate_report()

if __name__ == "__main__":
    main()
