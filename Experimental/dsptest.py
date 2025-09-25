import sys, json, numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QComboBox, QLabel, QSpinBox, QFileDialog,
    QDoubleSpinBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from scipy import signal


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure(figsize=(5, 4))
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)


class DSPStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EEE3030 DSP Studio")
        self.fs = 1024
        self.sig = np.zeros(1024)
        self._build_ui()

    # ---------------- UI -----------------
    def _build_ui(self):
        central = QWidget()
        root = QHBoxLayout(central)

        # ----- Left Controls -----
        controls = QVBoxLayout()

        # Signal generation
        controls.addWidget(QLabel("Signal Type"))
        self.sigType = QComboBox()
        self.sigType.addItems(["Sine", "Square", "Sawtooth", "Noise"])
        controls.addWidget(self.sigType)

        self.freqSpin = QDoubleSpinBox(); self.freqSpin.setRange(1, 500); self.freqSpin.setValue(50)
        controls.addWidget(QLabel("Frequency (Hz)")); controls.addWidget(self.freqSpin)

        self.ampSpin = QDoubleSpinBox(); self.ampSpin.setRange(0.1, 10); self.ampSpin.setValue(1)
        controls.addWidget(QLabel("Amplitude")); controls.addWidget(self.ampSpin)

        genBtn = QPushButton("Generate Signal")
        genBtn.clicked.connect(self.gen_signal)
        controls.addWidget(genBtn)

        # Window/FFT
        controls.addWidget(QLabel("FFT Window"))
        self.winBox = QComboBox()
        self.winBox.addItems(["Rectangular", "Hamming", "Hanning"])
        controls.addWidget(self.winBox)

        fftBtn = QPushButton("Run FFT")
        fftBtn.clicked.connect(self.run_fft)
        controls.addWidget(fftBtn)

        # FIR filter
        controls.addWidget(QLabel("FIR Order"))
        self.firOrder = QSpinBox(); self.firOrder.setRange(3, 200); self.firOrder.setValue(51)
        controls.addWidget(self.firOrder)

        controls.addWidget(QLabel("FIR Cutoff (Hz)"))
        self.firCut = QDoubleSpinBox(); self.firCut.setRange(1, self.fs/2); self.firCut.setValue(100)
        controls.addWidget(self.firCut)

        firBtn = QPushButton("Design & Apply FIR")
        firBtn.clicked.connect(self.apply_fir)
        controls.addWidget(firBtn)

        # IIR filter
        controls.addWidget(QLabel("IIR Order"))
        self.iirOrder = QSpinBox(); self.iirOrder.setRange(1, 10); self.iirOrder.setValue(4)
        controls.addWidget(self.iirOrder)

        controls.addWidget(QLabel("IIR Cutoff (Hz)"))
        self.iirCut = QDoubleSpinBox(); self.iirCut.setRange(1, self.fs/2); self.iirCut.setValue(100)
        controls.addWidget(self.iirCut)

        iirBtn = QPushButton("Design & Apply IIR")
        iirBtn.clicked.connect(self.apply_iir)
        controls.addWidget(iirBtn)

        # Save/Load
        saveBtn = QPushButton("Save Project")
        saveBtn.clicked.connect(self.save_project)
        controls.addWidget(saveBtn)
        loadBtn = QPushButton("Load Project")
        loadBtn.clicked.connect(self.load_project)
        controls.addWidget(loadBtn)

        # ----- Console -----
        controls.addWidget(QLabel("Console (use variables sig, fs)"))
        self.console = QTextEdit()
        self.console.setPlaceholderText("e.g. sig = sig*0.5\nprint(sig.mean())")
        controls.addWidget(self.console)

        runCodeBtn = QPushButton("Run Code")
        runCodeBtn.clicked.connect(self.run_console)
        controls.addWidget(runCodeBtn)

        root.addLayout(controls, 0)

        # ----- Plot -----
        self.canvas = MplCanvas()
        root.addWidget(self.canvas, 1)
        self.setCentralWidget(central)

    # ---------------- Signal/FFT -----------------
    def gen_signal(self):
        t = np.arange(0, 1, 1/self.fs)
        f = self.freqSpin.value()
        A = self.ampSpin.value()
        stype = self.sigType.currentText().lower()
        if stype == "sine":
            self.sig = A * np.sin(2*np.pi*f*t)
        elif stype == "square":
            self.sig = A * signal.square(2*np.pi*f*t)
        elif stype == "sawtooth":
            self.sig = A * signal.sawtooth(2*np.pi*f*t)
        else:
            self.sig = A * np.random.randn(len(t))
        self.plot_time()

    def run_fft(self):
        wname = self.winBox.currentText().lower()
        win = np.ones(len(self.sig))
        if wname == "hamming": win = np.hamming(len(self.sig))
        elif wname == "hanning": win = np.hanning(len(self.sig))
        X = np.fft.rfft(self.sig * win)
        f = np.fft.rfftfreq(len(self.sig), 1/self.fs)
        self.canvas.ax.clear()
        self.canvas.ax.plot(f, 20*np.log10(np.abs(X)+1e-12))
        self.canvas.ax.set_xlabel("Frequency (Hz)")
        self.canvas.ax.set_ylabel("Magnitude (dB)")
        self.canvas.ax.set_title("FFT")
        self.canvas.draw()

    # ---------------- Filters -----------------
    def apply_fir(self):
        cutoff = self.firCut.value()/(self.fs/2)
        b = signal.firwin(self.firOrder.value(), cutoff)
        self.sig = signal.lfilter(b, [1.0], self.sig)
        self.plot_time()

    def apply_iir(self):
        b, a = signal.butter(self.iirOrder.value(),
                             self.iirCut.value()/(self.fs/2))
        self.sig = signal.lfilter(b, a, self.sig)
        self.plot_time()

    # ---------------- Console -----------------
    def run_console(self):
        # give user access to sig and fs in a sandboxed dict
        local_env = {'sig': self.sig.copy(), 'fs': self.fs,
                     'np': np, 'signal': signal}
        try:
            exec(self.console.toPlainText(), {}, local_env)
            if 'sig' in local_env:
                self.sig = local_env['sig']
                self.plot_time()
        except Exception as e:
            self.canvas.ax.clear()
            self.canvas.ax.text(0.5, 0.5, f"Error:\n{e}",
                                ha='center', va='center')
            self.canvas.draw()

    # ---------------- Save/Load -----------------
    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "",
                                              "JSON Files (*.json)")
        if not path: return
        data = {
            'fs': self.fs,
            'signal': self.sig.tolist(),
            'console': self.console.toPlainText(),
            'params': {
                'sigType': self.sigType.currentText(),
                'freq': self.freqSpin.value(),
                'amp': self.ampSpin.value()
            }
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load JSON", "",
                                              "JSON Files (*.json)")
        if not path: return
        with open(path) as f:
            data = json.load(f)
        self.fs = data.get('fs', 1024)
        self.sig = np.array(data['signal'])
        self.console.setPlainText(data.get('console', ''))
        p = data.get('params', {})
        self.freqSpin.setValue(p.get('freq', 50))
        self.ampSpin.setValue(p.get('amp', 1))
        idx = self.sigType.findText(p.get('sigType', 'Sine'))
        if idx >= 0: self.sigType.setCurrentIndex(idx)
        self.plot_time()

    # ---------------- Helpers -----------------
    def plot_time(self):
        t = np.arange(len(self.sig))/self.fs
        self.canvas.ax.clear()
        self.canvas.ax.plot(t, self.sig)
        self.canvas.ax.set_xlabel("Time (s)")
        self.canvas.ax.set_ylabel("Amplitude")
        self.canvas.ax.set_title("Time Domain")
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DSPStudio()
    gui.show()
    sys.exit(app.exec())
