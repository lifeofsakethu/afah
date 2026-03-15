import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QFileDialog, QHBoxLayout, QComboBox, QSpinBox
from PyQt5.QtCore import Qt
import base64
import hashlib
import random
import string

class TextTools(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        layout.addWidget(QLabel("Input Text:"))
        layout.addWidget(self.text_edit)

        # Uppercase/Lowercase
        btn_upper = QPushButton("To UPPERCASE")
        btn_lower = QPushButton("To lowercase")
        btn_reverse = QPushButton("Reverse Text")
        btn_shuffle = QPushButton("Shuffle Lines")
        btn_remove_duplicates = QPushButton("Remove Duplicate Lines")
        btn_sort = QPushButton("Sort Lines")
        btn_base64_encode = QPushButton("Base64 Encode")
        btn_base64_decode = QPushButton("Base64 Decode")
        btn_hash = QPushButton("Hash (SHA256)")

        for btn in [btn_upper, btn_lower, btn_reverse, btn_shuffle, btn_remove_duplicates, btn_sort, btn_base64_encode, btn_base64_decode, btn_hash]:
            layout.addWidget(btn)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(QLabel("Result:"))
        layout.addWidget(self.result)

        btn_upper.clicked.connect(self.to_upper)
        btn_lower.clicked.connect(self.to_lower)
        btn_reverse.clicked.connect(self.reverse_text)
        btn_shuffle.clicked.connect(self.shuffle_lines)
        btn_remove_duplicates.clicked.connect(self.remove_duplicates)
        btn_sort.clicked.connect(self.sort_lines)
        btn_base64_encode.clicked.connect(self.base64_encode)
        btn_base64_decode.clicked.connect(self.base64_decode)
        btn_hash.clicked.connect(self.hash_text)

        self.setLayout(layout)

    def to_upper(self):
        self.result.setPlainText(self.text_edit.toPlainText().upper())

    def to_lower(self):
        self.result.setPlainText(self.text_edit.toPlainText().lower())

    def reverse_text(self):
        self.result.setPlainText(self.text_edit.toPlainText()[::-1])

    def shuffle_lines(self):
        lines = self.text_edit.toPlainText().splitlines()
        random.shuffle(lines)
        self.result.setPlainText('\n'.join(lines))

    def remove_duplicates(self):
        lines = self.text_edit.toPlainText().splitlines()
        seen = set()
        unique = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique.append(line)
        self.result.setPlainText('\n'.join(unique))

    def sort_lines(self):
        lines = self.text_edit.toPlainText().splitlines()
        lines.sort()
        self.result.setPlainText('\n'.join(lines))

    def base64_encode(self):
        text = self.text_edit.toPlainText().encode('utf-8')
        self.result.setPlainText(base64.b64encode(text).decode('utf-8'))

    def base64_decode(self):
        try:
            text = base64.b64decode(self.text_edit.toPlainText()).decode('utf-8')
            self.result.setPlainText(text)
        except Exception as e:
            self.result.setPlainText("Invalid Base64 input.")

    def hash_text(self):
        text = self.text_edit.toPlainText().encode('utf-8')
        self.result.setPlainText(hashlib.sha256(text).hexdigest())

class NumberTools(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.input_edit = QTextEdit()
        layout.addWidget(QLabel("Input Numbers (one per line):"))
        layout.addWidget(self.input_edit)

        btn_sum = QPushButton("Sum")
        btn_average = QPushButton("Average")
        btn_min = QPushButton("Min")
        btn_max = QPushButton("Max")
        btn_random = QPushButton("Random Number")

        for btn in [btn_sum, btn_average, btn_min, btn_max, btn_random]:
            layout.addWidget(btn)

        self.result = QLabel("")
        layout.addWidget(QLabel("Result:"))
        layout.addWidget(self.result)

        btn_sum.clicked.connect(self.sum_numbers)
        btn_average.clicked.connect(self.average_numbers)
        btn_min.clicked.connect(self.min_number)
        btn_max.clicked.connect(self.max_number)
        btn_random.clicked.connect(self.random_number)

        self.setLayout(layout)

    def get_numbers(self):
        try:
            return [float(line) for line in self.input_edit.toPlainText().splitlines() if line.strip()]
        except ValueError:
            self.result.setText("Invalid input.")
            return []

    def sum_numbers(self):
        nums = self.get_numbers()
        if nums:
            self.result.setText(str(sum(nums)))

    def average_numbers(self):
        nums = self.get_numbers()
        if nums:
            self.result.setText(str(sum(nums)/len(nums)))

    def min_number(self):
        nums = self.get_numbers()
        if nums:
            self.result.setText(str(min(nums)))

    def max_number(self):
        nums = self.get_numbers()
        if nums:
            self.result.setText(str(max(nums)))

    def random_number(self):
        nums = self.get_numbers()
        if nums:
            self.result.setText(str(random.choice(nums)))

class ConverterTools(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.input_edit = QTextEdit()
        layout.addWidget(QLabel("Input:"))
        layout.addWidget(self.input_edit)

        self.combo = QComboBox()
        self.combo.addItems([
            "Text to Hex", "Hex to Text",
            "Text to Binary", "Binary to Text",
            "Text to Decimal", "Decimal to Text"
        ])
        layout.addWidget(self.combo)

        btn_convert = QPushButton("Convert")
        layout.addWidget(btn_convert)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(QLabel("Result:"))
        layout.addWidget(self.result)

        btn_convert.clicked.connect(self.convert)

        self.setLayout(layout)

    def convert(self):
        text = self.input_edit.toPlainText()
        mode = self.combo.currentText()
        try:
            if mode == "Text to Hex":
                self.result.setPlainText(text.encode('utf-8').hex())
            elif mode == "Hex to Text":
                self.result.setPlainText(bytes.fromhex(text).decode('utf-8'))
            elif mode == "Text to Binary":
                self.result.setPlainText(' '.join(format(ord(c), '08b') for c in text))
            elif mode == "Binary to Text":
                self.result.setPlainText(''.join([chr(int(b, 2)) for b in text.split()]))
            elif mode == "Text to Decimal":
                self.result.setPlainText(' '.join(str(ord(c)) for c in text))
            elif mode == "Decimal to Text":
                self.result.setPlainText(''.join([chr(int(n)) for n in text.split()]))
        except Exception:
            self.result.setPlainText("Conversion error.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PineTools Local - Replication")
        self.setGeometry(100, 100, 800, 600)

        tabs = QTabWidget()
        tabs.addTab(TextTools(), "Text Tools")
        tabs.addTab(NumberTools(), "Number Tools")
        tabs.addTab(ConverterTools(), "Converters")

        self.setCentralWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())