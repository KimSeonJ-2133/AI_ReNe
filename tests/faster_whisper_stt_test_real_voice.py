import time
import os
import wave
import struct
import math
import random
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from src.services.stt_service.faster_whisper_service import stt_service  # FasterWhisperService가 정의된 파일을 import 하세요

def run_real_audio_benchmark(file_path):
    if not os.path.exists(file_path):
        print(f"❌ 오류: '{file_path}' 파일을 찾을 수 없습니다.")
        print("  -> 프로젝트 폴더에 테스트용 녹음 파일(test_voice.wav)을 넣어주세요.")
        return

    print(f"=== 🎙️ 실제 오디오 벤치마크: {file_path} ===")
    
    # 1. 파일 읽기 (Bytes로 로드)
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    
    file_size_mb = len(audio_bytes) / (1024 * 1024)
    print(f"파일 크기: {file_size_mb:.2f} MB")

    # 2. Warm-up (첫 실행)
    print("\n[Warm-up] 첫 번째 실행 (모델 로딩 및 초기화)...")
    start_time = time.time()
    text = stt_service.transcribe(audio_bytes)
    end_time = time.time()
    
    print(f"⏱️ Warm-up 소요 시간: {end_time - start_time:.4f}초")
    print(f"📝 인식 결과: \"{text}\"")

    if not text:
        print("⚠️ 주의: 인식된 텍스트가 없습니다. 오디오 볼륨이 너무 작거나 VAD에 걸러졌을 수 있습니다.")

    # 3. 실제 성능 측정 (3회 반복)
    iteration_count = 3
    total_time = 0
    print(f"\n[Benchmark] {iteration_count}회 반복 측정 시작...")

    for i in range(iteration_count):
        start_time = time.time()
        result = stt_service.transcribe(audio_bytes)
        elapsed = end_time = time.time() - start_time
        total_time += elapsed
        print(f"#{i+1} 소요 시간: {elapsed:.4f}초")

    avg_time = total_time / iteration_count
    
    print("\n=== 📊 최종 결과 ===")
    print(f"평균 처리 시간: {avg_time:.4f}초")
    
    # RTF 계산을 위해 오디오 길이(초)를 알면 좋지만, 여기서는 파일 크기로 대략 짐작하거나
    # librosa 등으로 길이를 구해야 정확한 RTF가 나옵니다. 
    # 일단 처리 시간 자체가 짧은지가 중요합니다.

if __name__ == "__main__":
    # 테스트할 파일명을 여기에 입력하세요
    target_file = "./tests/test_data/test.m4a" 
    run_real_audio_benchmark(target_file)