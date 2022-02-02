import argparse
from datetime import datetime
from modules.waveform import SoundData, DSP
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from modules import globals
import os
import ast
import json


class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        loadUi(globals.UI_PATH, self)

        self.setWindowTitle(globals.WNAME)

        sd_temp = SoundData()
        self.sound_data = sd_temp.from_numpy(np.array([0, 0, 0, 0]), 44100)

        self.player = QMediaPlayer() # https://learndataanalysis.org/source-code-how-to-play-an-audio-file-using-pyqt5-pyqt5-tutorial/

        self.fname = None

        self.volume = 80

        self.flt_labels = [self.filterParamLabel1, self.filterParamLabel2, self.filterParamLabel3]
        self.flt_inputs = [self.filterParamValue1, self.filterParamValue2, self.filterParamValue3]

        # combo box initialization
        self.filterList.addItems(globals.FILTER_LIST)
        self.filterList.setCurrentIndex(0)
        self.filterList.currentIndexChanged.connect(self.update_filters)

        self.loadButton.clicked.connect(self.load)

        self.saveButton.clicked.connect(self.save)

        self.applyButton.clicked.connect(self.apply)

        self.volumeSlider.valueChanged.connect(self.volume_control)

        self.playButton.clicked.connect(self.play_audio)

        self.pauseButton.clicked.connect(self.pause_audio)

        self.stopButton.clicked.connect(self.stop_audio)

        self.update_filters()
        self.update_graph()

    def create_graph(self):
        self.sound_data = SoundData().from_numpy([0, 0, 0, 0], 44100)

    def pause_audio(self):
        if self.player.state() == 1:
            self.player.pause()
        elif self.player.state() == 2:
            self.player.play()

    def stop_audio(self):
        self.player.stop()
        self.player.setMedia(QMediaContent())

    def play_audio(self):
        try:
            if len(self.sound_data.data) > 10:
                self.sound_data.save_temp()
                fpath = os.path.join(os.getcwd(), 'temp\\temp.wav')
                url = QUrl.fromLocalFile(fpath)
                filecontent = QMediaContent(url)

                self.player.setMedia(filecontent)
                self.player.play()
            else:
                QMessageBox.warning(self, "Error!", "Load the file before playing it!", QMessageBox.Ok)
        except Exception as e:
            print(e)

    def update_graph(self):
        data, x = self.sound_data.plot()

        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(np.linspace(0, x, x), data)
        self.MplWidget.canvas.axes.plot(np.linspace(0, x, 2), [0, 0], color="black")
        if len(self.sound_data.data) > 10:
            ticks = self.sound_data.get_time_ticks()
            self.MplWidget.canvas.axes.set_xticks(np.linspace(0, x, 5))
            self.MplWidget.canvas.axes.set_xticklabels(ticks)
        self.MplWidget.canvas.draw()

    def hide_all(self):
        for i in range(len(self.flt_inputs)):
            self.flt_inputs[i].hide()
            self.flt_labels[i].hide()

    def update_filters(self):
        self.hide_all()
        for i in range(len(globals.FILTER_LABELS[self.filterList.currentText()])):
            self.flt_labels[i].setText(globals.FILTER_LABELS[self.filterList.currentText()][i + 1])
            self.flt_labels[i].show()
            self.flt_inputs[i].setText(str(globals.FILTER_PARAMS[self.filterList.currentText().lower()][list(
                globals.FILTER_PARAMS[self.filterList.currentText().lower()].keys())[i]]))
            self.flt_inputs[i].show()

    def get_args(self):
        args = {f"{list(globals.FILTER_PARAMS[self.filterList.currentText().lower()].keys())[i]}": float(self.flt_inputs[i].text()) for i in range(len(
            globals.FILTER_PARAMS[self.filterList.currentText().lower()]))}
        return args

    def load(self):
        self.statusLabel.setText("Loading file...")
        options = QFileDialog.Options()
        self.fname, _ = QFileDialog.getOpenFileName(self, "Select file to open", "", "WAV Files (*.wav);;All files (*.*)", options=options)

        if self.fname.endswith(".wav"):
            self.sound_data.load(self.fname)
            self.statusLabel.setText("Updating waveform plot...")
            self.update_graph()
            self.statusLabel.setText(f"{self.fname}")
        elif self.fname:
            QMessageBox.warning(self, "Error!", "The app can currently process only\n*.wav files", QMessageBox.Ok)

    def save(self):
        if self.fname is None:
            QMessageBox.warning(self, "Error!", "The app can currently process only\n*.wav files", QMessageBox.Ok)
        else:
            options = QFileDialog.Options()
            save_name, _ = QFileDialog.getSaveFileName(self, "Save file", "", "WAV Files (*.wav);;All files (*.*)", options=options)
            if save_name:
                self.sound_data.save(save_name)

    def volume_control(self):
        self.volume = self.volumeSlider.value()
        self.volumeValueLabel.setText(f"{self.volume}%")
        self.player.setVolume(self.volume)

    def apply(self):
        if self.fname is None:
            QMessageBox.warning(self, "Error!", "You can't apply filter when there is\nno file loaded!", QMessageBox.Ok)
            return
        filter = self.filterList.currentText()
        try:
            kwargs = self.get_args()
        except Exception as e:
            QMessageBox.warning(self, "Error!", f"Wrong arguments passed to filter!\nError: {e}", QMessageBox.Ok)
            return
        tempsd = SoundData()
        dsp = DSP(self.sound_data)
        self.statusLabel.setText(f"Applying {filter.lower()}...")
        if filter == "Reverb":
            fx = dsp.reverb(**kwargs)
        elif filter == "Chorus":
            fx = dsp.chorus(**kwargs)
        elif filter == "Pitch shifter":
            fx = dsp.pitch_shift(**kwargs)
        tempsd.from_numpy(fx, self.sound_data.fs)
        self.sound_data.clear()
        self.sound_data = tempsd
        self.statusLabel.setText("Updating waveform plot...")
        self.update_graph()
        self.statusLabel.setText(f"{self.fname}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="pysndproc", description=globals.DESC, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-g", "--gui", action="store_true", help="Launch program in graphical mode. Needs no more args.")
    parser.add_argument("-i", "--input", default="empty", type=str, help="Path to input *.wav file.")
    parser.add_argument("-o", "--output", default=f"{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.wav", help="Path to output *.wav file")
    parser.add_argument("-f", "--filter", default="reverb", type=str, help="Name of filter to apply to file. Valid names enumerated in description")
    parser.add_argument("-p", "--params", default=str(globals.FILTER_PARAMS["reverb"]), type=str, help=globals.PARAMS_HELP)

    args = parser.parse_args()

    if args.gui is True:
        app = QApplication([])
        window = MatplotlibWidget()
        window.show()
        app.exec_()

    else:
        if not args.input == "empty":
            sd, sdmod = SoundData(), SoundData()
            try:
                sd.load(args.input)
                dsp = DSP(sd)
                if args.filter == "reverb":
                    try:
                        kwargs = json.loads(json.dumps(args.params))
                        kwargs = ast.literal_eval(kwargs)
                        mod = dsp.reverb(**kwargs)
                        sdmod.from_numpy(mod, sd.fs)
                        sdmod.save(args.output)
                        print(f"Saved file as {args.output}")
                    except Exception as e:
                        print(f"Passed wrong values with params dict!\nError message: {e}")
                elif args.filter == "chorus":
                    try:
                        kwargs = json.loads(json.dumps(args.params))
                        kwargs = ast.literal_eval(kwargs)
                        mod = dsp.chorus(**kwargs)
                        sdmod.from_numpy(mod, sd.fs)
                        sdmod.save(args.output)
                        print(f"Saved file as {args.output}")
                    except Exception as e:
                        print(f"Passed wrong values with params dict!\nError message: {e}")
                elif args.filter == "pitchshifter":
                    try:
                        kwargs = json.loads(json.dumps(args.params))
                        kwargs = ast.literal_eval(kwargs)
                        mod = dsp.pitch_shift(**kwargs)
                        sdmod.from_numpy(mod, sd.fs)
                        sdmod.save(args.output)
                        print(f"Saved file as {args.output}")
                    except Exception as e:
                        print(f"Passed wrong values with params dict!\nError message: {e}")
            except Exception as e:
                print(f"Can't load specified file!\nError message: {e}")
        else:
            print("No input file specified! Use 'python main.py -g' to launch GUI.")
