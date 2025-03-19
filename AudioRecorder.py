import msvcrt
import numpy as np
import sounddevice as sd
import soundfile as sf
import threading

class AudioRecorder:
    def __init__(self, volumeThreshold=0.01, silentTimeThreshold=1.0, sampleRate=44100, blockDuration=0.1):
        self.buffer = []
        self.silentTime = 0
        self.recording = False

        self.volumeThreshold = volumeThreshold
        self.silentTimeThreshold = silentTimeThreshold
        self.sampleRate = sampleRate
        self.blockDuration = blockDuration

    def __record__(self):
        self.recording = True
        print("Recording started, press 's' to stop recording.")

        with sd.InputStream(samplerate=self.sampleRate, channels=1) as stream:
            while True:
                data, _ = stream.read(int(self.sampleRate * self.blockDuration))
                self.buffer.append(data)
                volume = np.abs(data).mean()

                if volume < self.volumeThreshold:
                    self.silentTime += self.blockDuration
                    if self.silentTime >= self.silentTimeThreshold:
                        break
                else:
                    self.silentTime = 0

                if not self.recording:
                    break

        print("Recording finished, saving to file...")
        sf.write("output.wav", np.concatenate(self.buffer), 44100)
        print("File saved as output.wav.")

        self.buffer = []
        self.silentTime = 0
        self.recording = False

    def startRecording(self):
        if self.recording:
            return

        self.thread = threading.Thread(target=self.__record__)
        self.thread.start()

    def stopRecording(self):
        if not self.recording:
            return
        
        self.recording = False
        self.thread.join()

    def isRecording(self):
        return self.recording

if __name__ == "__main__":
    recorder = AudioRecorder(silentTimeThreshold=3.0)
    recording = recorder.startRecording()

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b's':
                recorder.stopRecording()
            elif key == b'r':
                recorder.startRecording()
            elif key == b'q':
                if recorder.isRecording():
                    recorder.stopRecording()

                break