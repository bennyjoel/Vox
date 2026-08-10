import wave
import struct
import math
import os

def generate_tone(filename, frequency, duration, volume=0.5, sample_rate=44100):
    num_samples = int(duration * sample_rate)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            # Calculate sine wave value
            t = float(i) / sample_rate
            value = int(volume * 32767.0 * math.sin(2.0 * math.pi * frequency * t))
            
            # Pack value into binary data
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

if __name__ == "__main__":
    # Generate start sound (Higher pitch short tone)
    generate_tone("sound_start.wav", frequency=880.0, duration=0.1)
    
    # Generate stop sound (Lower pitch short tone)
    generate_tone("sound_stop.wav", frequency=440.0, duration=0.1)
    
    print("Generated sound_start.wav and sound_stop.wav")
