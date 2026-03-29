import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QFileDialog,
    QTextEdit, QPushButton, QLabel, QSizePolicy, QSpinBox, QLineEdit
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DotplotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dotly")
        self.setGeometry(100, 100, 1200, 600)
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # --- LEFT SIDE: Sequence inputs ---
        left_layout = QVBoxLayout()
        self.seq1_input = QTextEdit()
        self.seq1_input.setPlaceholderText("Paste sequence 1 (DNA/RNA/Protein) or load a FASTA file")
        self.seq2_input = QTextEdit()
        self.seq2_input.setPlaceholderText("Paste sequence 2 (DNA/RNA/Protein) or load a FASTA file")
        left_layout.addWidget(QLabel("Sequence 1:"))
        left_layout.addWidget(self.seq1_input)
        load1_button = QPushButton("Load FASTA 1")
        load1_button.clicked.connect(lambda: self.load_fasta(self.seq1_input))
        left_layout.addWidget(load1_button)

        left_layout.addWidget(QLabel("Sequence 2:"))
        left_layout.addWidget(self.seq2_input)
        load2_button = QPushButton("Load FASTA 2")
        load2_button.clicked.connect(lambda: self.load_fasta(self.seq2_input))
        left_layout.addWidget(load2_button)

        # --- RIGHT SIDE: Parameters + buttons + canvas ---
        right_layout = QVBoxLayout()

        # Chart title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("DotPlot")
        self.title_input.setFixedHeight(30)
        right_layout.addWidget(QLabel("Chart title:"))
        right_layout.addWidget(self.title_input)

        # X and Y axis names
        self.xlabel_input = QLineEdit()
        self.xlabel_input.setPlaceholderText("Sequence 1")
        self.xlabel_input.setFixedHeight(30)
        self.ylabel_input = QLineEdit()
        self.ylabel_input.setPlaceholderText("Sequence 2")
        self.ylabel_input.setFixedHeight(30)
        axes_layout = QHBoxLayout()
        axes_layout.addWidget(QLabel("X-axis label:"))
        axes_layout.addWidget(self.xlabel_input)
        axes_layout.addSpacing(20)
        axes_layout.addWidget(QLabel("Y-axis label:"))
        axes_layout.addWidget(self.ylabel_input)
        right_layout.addLayout(axes_layout)

        # SpinBoxes
        self.window_spin = QSpinBox()
        self.window_spin.setMinimum(1)
        self.window_spin.setMaximum(100)
        self.window_spin.setValue(3)
        self.stringency_spin = QSpinBox()
        self.stringency_spin.setMinimum(1)
        self.stringency_spin.setMaximum(100)
        self.stringency_spin.setValue(3)

        # Buttons
        self.plot_button = QPushButton("Generate DotPlot")
        self.plot_button.setFixedHeight(40)
        self.plot_button.clicked.connect(self.on_plot_button_clicked)
        self.download_button = QPushButton("Download")
        self.download_button.setFixedHeight(40)
        self.download_button.clicked.connect(self.on_download_button_clicked)

        # Layout for controls
        controls_layout = QHBoxLayout()
        params_layout = QFormLayout()
        params_layout.setLabelAlignment(Qt.AlignRight)
        params_layout.setFormAlignment(Qt.AlignLeft)
        params_layout.addRow("Window size:", self.window_spin)
        params_layout.addRow("Stringency:", self.stringency_spin)
        controls_layout.addLayout(params_layout)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(self.plot_button)
        controls_layout.addWidget(self.download_button)

        # Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        right_layout.addLayout(controls_layout)
        right_layout.addWidget(self.canvas)

        # Add both sides to main layout
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 3)

    def load_fasta(self, text_edit):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open FASTA file", "", "FASTA files (*.fasta *.fa);;All files (*)")
        if file_name:
            with open(file_name, "r") as f:
                lines = f.readlines()
            # Parse FASTA: ignore headers starting with ">"
            seq = "".join(line.strip() for line in lines if not line.startswith(">"))
            text_edit.setPlainText(seq)

    def on_plot_button_clicked(self):
        seq1 = self.seq1_input.toPlainText()
        seq2 = self.seq2_input.toPlainText()
        window = self.window_spin.value()
        stringency = self.stringency_spin.value()
        title = self.title_input.text().strip()
        xlabel = self.xlabel_input.text().strip()
        ylabel = self.ylabel_input.text().strip()

        if not seq1 or not seq2:
            print("Both sequences must be provided.")
            return

        if stringency > window:
            print("Stringency cannot be higher than the window size.")
            return

        if not title:
            title = "DotPlot"
        if not xlabel:
            xlabel = "Sequence 1"
        if not ylabel:
            ylabel = "Sequence 2"

        self.generate_dotplot(seq1, seq2, window, stringency, title, xlabel, ylabel)

    def generate_dotplot(self, seq1, seq2, window, stringency, title, xlabel, ylabel):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        x = []
        y = []

        # Remove whitespace/newlines and convert to uppercase
        seq1 = seq1.upper().replace("\n", "").replace(" ", "")
        seq2 = seq2.upper().replace("\n", "").replace(" ", "")

        len1 = len(seq1)
        len2 = len(seq2)

        for i in range(len1 - window + 1):
            window1 = seq1[i:i+window]
            for j in range(len2 - window + 1):
                window2 = seq2[j:j+window]
                matches = sum(1 for a, b in zip(window1, window2) if a == b)
                if matches >= stringency:
                    x.append(i)
                    y.append(j)

        ax.plot(x, y, 'k.', markersize=2)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_xlim(0, len(seq1))
        ax.set_ylim(0, len(seq2))

        self.canvas.draw()

    def on_download_button_clicked(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save chart as", "", "PNG Files (*.png);;All Files (*)", options=options)
        if file_name:
            self.figure.savefig(file_name)
            print(f"Chart saved to {file_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DotplotApp()
    window.show()
    sys.exit(app.exec_())