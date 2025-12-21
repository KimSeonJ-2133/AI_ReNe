import time
import os
import wave
import struct
import math
import random
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from src.services.stt_service.faster_whisper_service import stt_service  # FasterWhisperService가 정의된 파일을 import 하세요

def generate_dummy_audio_bytes(duration_sec=3):
    """테스트용 더미 오디오(삐- 소리) 바이트 생성"""
    sample_rate = 16000
    n_samples = int(sample_rate * duration_sec)
    
    # 메모리 버퍼에 WAV 파일 포맷으로 쓰기
    import io
    wav_buffer = io.BytesIO()
    
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(sample_rate)
        
        # 간단한 Sine 파형 생성 (데이터가 있어야 VAD에 걸러지지 않고 STT가 돔)
        data = bytearray()
        for i in range(n_samples):
            value = int(32767.0 * math.sin(2 * math.pi * 440.0 * i / sample_rate))
            data.extend(struct.pack('<h', value))
            
        wav_file.writeframes(data)
        
    return wav_buffer.getvalue()

def run_benchmark():
    print("=== STT 성능 벤치마크 시작 ===")
    
    # 1. 테스트 데이터 준비
    duration = 10 # 5초짜리 오디오
    audio_bytes = generate_dummy_audio_bytes(duration_sec=duration)
    print(f"테스트 오디오 길이: {duration}초 ({len(audio_bytes)} bytes)")

    # 2. Warm-up (첫 실행은 모델 로딩/CUDA 초기화로 인해 무조건 느림)
    print("\n[Warm-up] 첫 번째 실행 (Cold Start)...")
    start_time = time.time()
    result = stt_service.transcribe(audio_bytes)
    end_time = time.time()
    print(f"Warm-up 소요 시간: {end_time - start_time:.4f}초")
    print(f"결과: {result}")

    # 3. 실제 성능 측정 (여러 번 반복하여 평균 측정)
    iteration_count = 3
    total_time = 0
    
    print(f"\n[Benchmark] {iteration_count}회 반복 측정 시작...")
    
    for i in range(iteration_count):
        start_time = time.time()
        _ = stt_service.transcribe(audio_bytes) # 결과는 무시
        end_time = time.time()
        
        elapsed = end_time - start_time
        total_time += elapsed
        print(f"#{i+1} 소요 시간: {elapsed:.4f}초")

    avg_time = total_time / iteration_count
    rtf = avg_time / duration # Real-Time Factor (낮을수록 좋음)

    print("\n=== 최종 결과 ===")
    print(f"평균 처리 시간: {avg_time:.4f}초")
    print(f"RTF (Real-Time Factor): {rtf:.4f}")
    if rtf < 1.0:
        print("✅ 실시간 처리 가능 (오디오 길이보다 처리 시간이 짧음)")
    else:
        print("⚠️ 실시간 처리 어려움 (오디오 길이보다 처리 시간이 김)")

if __name__ == "__main__":
    run_benchmark()