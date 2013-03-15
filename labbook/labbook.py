"""
A tool for **quickly** and **accurately** making **timestamped** notes.

Notes are saved in text files using Markdown formatting.
"""

import sys
import os
import string
import datetime

from PySide import QtCore, QtGui

# Configuration
APP_DIR = os.path.expanduser("~/labbook")
HEADER_TEMPLATE = string.Template("""Date: $date
Title: $title
""")
ENTRY_TEMPLATE = string.Template("\n$time: $note")

class Labbook(QtGui.QWidget):

    def __init__(self):
        super(Labbook, self).__init__()

        if not os.path.exists(APP_DIR):
            os.makedirs(APP_DIR)

        self._experimentRunning = False

        self._initUI()

    def _initUI(self):

        self.setWindowTitle("Labbook")
        self.resize(400, 400)

        vboxLayout = QtGui.QVBoxLayout()

        self._timerWidget = DigitalTimer()
        self._timerWidget.setFixedHeight(100)
        vboxLayout.addWidget(self._timerWidget)

        self._noteEdit = QtGui.QLineEdit()
        vboxLayout.addWidget(self._noteEdit)

        hboxLayout = QtGui.QHBoxLayout()

        self._startButton = QtGui.QPushButton("Start")
        self._startButton.clicked.connect(self._start)

        self._addEntryButton = QtGui.QPushButton("Add Entry")
        self._addEntryButton.clicked.connect(self._add)
        self._addEntryButton.setEnabled(False)
        self._noteEdit.returnPressed.connect(self._addEntryButton.clicked)

        self._stopButton = QtGui.QPushButton("Stop")
        self._stopButton.clicked.connect(self._stop)
        self._stopButton.setEnabled(False)

        hboxLayout.addWidget(self._startButton)
        hboxLayout.addWidget(self._addEntryButton)
        hboxLayout.addWidget(self._stopButton)

        vboxLayout.addLayout(hboxLayout)

        self._notesView = QtGui.QPlainTextEdit()
        self._notesView.setReadOnly(True)
        vboxLayout.addWidget(self._notesView)

        self.setLayout(vboxLayout)

        self.show()

    def _start(self):
        if self._experimentRunning:
            self._stop()
        self._experimentRunning = True

        self._experimentStartTime = datetime.datetime.now()

        ok = False
        while not ok:
            title, ok = QtGui.QInputDialog.getText(self, 'Experiment title', 
                'Experiment title:')
        self._experimentTitle = title

        # Create experiment file
        filePath = "%s/%s.txt" % (APP_DIR, self._experimentStartTime.strftime("%Y-%m-%d-%H-%M-%S"))
        self._experimentFile = open(filePath, 'w')
        header = HEADER_TEMPLATE.substitute(
            date=self._experimentStartTime.strftime("%d/%m/%Y %H:%M:%S"),
            title=title
        )
        self._experimentFile.write(header)
        self._notesView.setPlainText(header)


        self._timerWidget.start()

        self._addEntryButton.setEnabled(True)
        self._stopButton.setEnabled(True)

    def _add(self):
        if not self._experimentRunning:
            return

        # Remove trailing whitespace (from enter being pressed in lineedit)
        note = self._noteEdit.text().strip()

        entry = ENTRY_TEMPLATE.substitute(
            time=self._timerWidget.time(),
            note=note
        )
        self._experimentFile.write(entry)
        self._notesView.setPlainText(self._notesView.toPlainText() + entry)

        self._noteEdit.clear()

    def _stop(self):
        self._experimentRunning = False

        self._timerWidget.stop()

        self._experimentFile.close()

        self._addEntryButton.setEnabled(False)
        self._stopButton.setEnabled(False)


class DigitalTimer(QtGui.QLCDNumber):

    def __init__(self, parent=None):
        super(DigitalTimer, self).__init__(parent)
        self.setSegmentStyle(QtGui.QLCDNumber.Filled)
        self._time = QtCore.QTime(0, 0)
        self.display("00:00")

        self._displayUpdater = QtCore.QTimer()
        self._displayUpdater.timeout.connect(self._updateDisplay)

    def start(self):
        self._time.restart()
        self._displayUpdater.start(1000)

    def stop(self):
        self._displayUpdater.stop()

    def _updateDisplay(self):
        time = self.time()
        self.display(time)

    def time(self):
        elapsedMs = self._time.elapsed()
        elapsedTime = QtCore.QTime(0, 0)
        elapsedTime = elapsedTime.addMSecs(elapsedMs)
        return elapsedTime.toString("mm:ss")


def main():
    app = QtGui.QApplication(sys.argv)
    labbook = Labbook()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()