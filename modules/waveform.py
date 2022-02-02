import numpy as np
import matplotlib.pyplot as mpl
import scipy.io.wavfile as wav
import tinytag
import pedalboard as fx
from datetime import timedelta, datetime
import os


class SoundData:
    def __init__(self):
        self.fs = 0
        self.data = []
        self.meta = None
        self.samples = None

    def clear(self):
        self.fs = 0
        self.data = []
        self.meta = None
        self.samples = None

    def get_time_ticks(self):
        ticks = [(datetime(2022, 1, 1, 0, 0, 0) + timedelta(seconds=i // self.fs)).strftime("%M:%S") for i in np.linspace(0, len(self.data), 5)]
        return ticks

    def from_numpy(self, data, fs):
        self.data = data
        self.fs = fs
        return self

    def load(self, filename):
        if not isinstance(filename, str):
            raise TypeError("SoundData creation failed! Filename is of wrong type!")
        if not filename.endswith(".wav"):
            raise ValueError("SoundData creation failed! Wrong filename!")
        self.fs, self.data = wav.read(filename)

        try:
            if self.data.shape[1] > 1:
                self.data = self.stereo2mono(self.data)
        except Exception as e:
            self.data = self.data * 2 ** 15
        self.samples = len(self.data)
        self.meta = tinytag.TinyTag.get(filename)
        if self.meta.artist is None:
            self.meta.artist = "Unknown"
        if self.meta.title is None:
            self.meta.title = "Unknown"

    def stereo2mono(self, stereo):
        mono = stereo.sum(axis=1) / 2
        return mono

    def normalize(self, data):
        if sum(data) == 0 or (max(data) <= 1 and min(data) >= -1):
            return data
        else:
            data32 = np.array(data, dtype="int32")
            chmax = max(data32)
            chmin = min(data32)
            return ((2 * data32) / (chmax - chmin)).T

    def float_wav_to_int16(self):
        self.data = self.data * 65335

    def decimate(self, data):
        dl = len(data)
        if dl > 10000:
            return data[[val for val in range(dl) if val % (dl // 10000) == 0]]
        return data

    def sample2duration(self, sid):
        return round(sid / self.fs, 2)

    def time2plotx(self, time, pdatalen):
        return round(pdatalen / time, 2)

    def plot(self, tstart=0, tend=None, marker_pos=0):

        if tend is None:
            tend = self.samples

        fig = mpl.figure(figsize=(6, 1.8))

        ax = fig.add_subplot(111)

        dn = self.decimate(self.normalize(self.data[tstart:tend]))

        #ax.plot(dn)
        marker, = ax.plot([marker_pos, marker_pos], [-1.4, 1.4], color="red")

        #ax.set_xticks([])
        #ax.set_yticks([-1, 0, 1])
        #ax.set_ylim([-1.2, 1.2])

        #mpl.title(f"Waveform {self.meta.title} by {self.meta.artist}")

        return dn, len(dn)

    def save(self, name):
        if isinstance(self.data[0], np.float64):
            # cheater move, the only workaround to deal with wav format mismatch
            board = fx.Pedalboard([fx.Reverb(room_size=0, damping=0, wet_level=0, dry_level=1 - 0)],
                                  sample_rate=self.fs)
            self.data = board(self.data)
        if max(self.data) > 1: # determine if operating on float wav or 16bit int wav
            wav.write(name, self.fs, self.data / 65355)
        else:
            wav.write(name, self.fs, self.data)

    def save_temp(self):
        try:
            if isinstance(self.data[0], np.float64):

                board = fx.Pedalboard([fx.Reverb(room_size=0, damping=0, wet_level=0, dry_level=1 - 0)],
                              sample_rate=self.fs)
                self.data = board(self.data)

            if max(self.data) > 1: # determine if operating on float wav or 16bit int wav
                wav.write(f"../temp/temp.wav", self.fs, self.data / 65355)
            else:
                wav.write(f"../temp/temp.wav", self.fs, self.data)
        except FileNotFoundError:
            os.mkdir("../temp")
            self.save_temp()


class DSP:
    def __init__(self, SoundData):
        self.sd = SoundData

    # zaimplementowano efekty opracowane przez firmę spotify i udostępnione pod licencją GNUv3 na
    # https://github.com/spotify/pedalboard
    def reverb(self, room_size=0.2, damping=0.07, ratio=0.2):
        if not isinstance(room_size, float) or not isinstance(damping, float) or not isinstance(damping, float):
            try:
                room_size = float(room_size)
                damping = float(damping)
                ratio = float(ratio)
            except Exception as e:
                print(e)
        board = fx.Pedalboard([fx.Reverb(room_size=room_size, damping=damping, wet_level=ratio, dry_level=1 - ratio)],
                              sample_rate=self.sd.fs)
        return board(self.sd.data)

    def chorus(self, rate=1.0, depth=0.25, delay=3.0, feedback=0.02, mix=0.5):
        board = fx.Pedalboard([fx.Chorus(rate_hz=rate, depth=depth, centre_delay_ms=delay, feedback=feedback, mix=mix)],
                              sample_rate=self.sd.fs)
        return board(self.sd.data)

    def pitch_shift(self, shift=12): #shift in semitones, 12 st = 1 oct
        board = fx.Pedalboard([fx.PitchShift(semitones=shift)], sample_rate=self.sd.fs)
        return board(self.sd.data) # na moje muzyczne ucho to chyba nawet zastosowali polifoniczny algorytm
        # dlatego trzeba z pół minuty czekać



