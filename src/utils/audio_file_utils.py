import wave, io

def pcm_to_wav_bytes(pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, bit_depth: int = 16) -> bytes:
    """
    Raw PCM 데이터를 WAV 포맷(헤더 포함)의 바이트로 변환
    :param pcm_data: PCM 바이너리 데이터
    :param sample_rate: 샘플링 레이트 (예: 16000Hz, 44100Hz) - *중요: 녹음 설정과 일치해야 함*
    :param channels: 채널 수 (1: Mono, 2: Stereo)
    :param bit_depth: 비트 깊이 (보통 16비트)
    """
    # 메모리 내에서 파일처럼 동작하는 버퍼 생성
    wav_io = io.BytesIO()
    
    # wave 모듈을 사용해 헤더 작성 및 데이터 쓰기
    with wave.open(wav_io, "wb") as wav_file:
        wav_file.setnchannels(channels)        # 채널 수 설정
        wav_file.setsampwidth(bit_depth // 8)  # 샘플 사이즈 설정 (16bit -> 2bytes)
        wav_file.setframerate(sample_rate)     # 프레임 레이트 설정
        wav_file.writeframes(pcm_data)         # PCM 데이터 쓰기
    
    # 버퍼의 포인터를 처음으로 되돌리고 바이트 값 반환
    wav_io.seek(0)
    return wav_io.read()