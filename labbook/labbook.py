"""
A tool for **quickly** and **accurately** making **timestamped** notes.

Notes are saved in text files using Markdown formatting.
"""

import sys
import os
import string
import datetime

from PySide.QtCore import *
from PySide.QtGui import *

# Configuration
APP_DIR = os.path.expanduser("~/labbook")
HEADER_TEMPLATE = string.Template("""Date: $date
Title: $title
""")
ENTRY_TEMPLATE = string.Template("\n$time: $note")

class Labbook(QMainWindow):

    def __init__(self):
        super(Labbook, self).__init__()

        if not os.path.exists(APP_DIR):
            os.makedirs(APP_DIR)

        self._experimentRunning = False

        self._initUI()

    def _initUI(self):

        # Set up window.

        self.setWindowTitle("labbook")
        self.resize(400, 400)

        # Set up actions.

        openExperimentFolderAction = QAction("View past experiments", self)
        openExperimentFolderAction.setStatusTip('Open experiments folder')
        openExperimentFolderAction.setToolTip('Open experiments folder')
        openExperimentFolderAction.triggered.connect(self._openExperimentFolder)

        self._startExperimentAction = QAction("Start", self)
        self._startExperimentAction.setStatusTip('Start experiment')
        self._startExperimentAction.setToolTip('Start experiment')
        self._startExperimentAction.triggered.connect(self._startExperiment)

        self._addEntryAction = QAction("Add entry", self)
        self._addEntryAction.setStatusTip('Add entry to current experiment')
        self._addEntryAction.setToolTip('Add entry to current experiment')
        self._addEntryAction.triggered.connect(self._addEntry)

        self._stopExperimentAction = QAction("Stop", self)
        self._stopExperimentAction.setStatusTip('Stop experiment')
        self._stopExperimentAction.setToolTip('Stop experiment')
        self._stopExperimentAction.triggered.connect(self._stopExperiment)

        # Set up toolbar
        
        toolbar = self.addToolBar('')
        toolbar.setFloatable(False)
        toolbar.setMovable(False)

        toolbar.addAction(self._startExperimentAction)
        toolbar.addAction(self._addEntryAction)
        toolbar.addAction(self._stopExperimentAction)
        toolbar.addSeparator()
        toolbar.addAction(openExperimentFolderAction)

        # Set up central widget.
        
        centralWidget = QWidget(self)

        vboxLayout = QVBoxLayout()

        self._timerWidget = DigitalTimer()
        self._timerWidget.setFixedHeight(100)
        vboxLayout.addWidget(self._timerWidget)

        self._noteEdit = QLineEdit()
        vboxLayout.addWidget(self._noteEdit)

        hboxLayout = QHBoxLayout()

        self._startExperimentButton = QPushButton("Start")
        self._startExperimentButton.setToolTip('Start experiment')
        self._startExperimentButton.clicked.connect(self._startExperiment)

        self._addEntryButton = QPushButton("Add Entry")
        self._addEntryButton.clicked.connect(self._addEntry)
        self._addEntryButton.setEnabled(False)
        self._addEntryAction.setEnabled(False)
        self._noteEdit.returnPressed.connect(self._addEntryButton.clicked)

        self._stopExperimentButton = QPushButton("Stop")
        self._stopExperimentButton.setToolTip('Stop experiment')
        self._stopExperimentButton.clicked.connect(self._stopExperiment)
        self._stopExperimentButton.setEnabled(False)
        self._stopExperimentAction.setEnabled(False)

        hboxLayout.addWidget(self._startExperimentButton)
        hboxLayout.addWidget(self._addEntryButton)
        hboxLayout.addWidget(self._stopExperimentButton)

        vboxLayout.addLayout(hboxLayout)

        self._notesView = QPlainTextEdit()
        self._notesView.setReadOnly(True)
        vboxLayout.addWidget(self._notesView)

        centralWidget.setLayout(vboxLayout)

        self.setCentralWidget(centralWidget)

        # Set up status bar.
        self.statusBar()

        # Show window.

        self.show()

    def _startExperiment(self):
        if self._experimentRunning:
            self._stopExperiment()
        self._experimentRunning = True

        self._experimentStartTime = datetime.datetime.now()

        ok = False
        while not ok:
            title, ok = QInputDialog.getText(self, 'Experiment title', 
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
        self._addEntryAction.setEnabled(True)
        self._stopExperimentButton.setEnabled(True)
        self._stopExperimentAction.setEnabled(True)

    def _addEntry(self):
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

    def _stopExperiment(self):
        self._experimentRunning = False

        self._timerWidget.stop()

        self._experimentFile.close()

        self._addEntryButton.setEnabled(False)
        self._addEntryAction.setEnabled(False)
        self._stopExperimentButton.setEnabled(False)
        self._stopExperimentAction.setEnabled(False)

    def _openExperimentFolder(self):
        QDesktopServices.openUrl(QUrl("file:///" + APP_DIR, QUrl.TolerantMode))


class DigitalTimer(QLCDNumber):

    def __init__(self, parent=None):
        super(DigitalTimer, self).__init__(parent)
        self.setSegmentStyle(QLCDNumber.Filled)
        self._time = QTime(0, 0)
        self.display("00:00")

        self._displayUpdater = QTimer()
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
        elapsedTime = QTime(0, 0)
        elapsedTime = elapsedTime.addMSecs(elapsedMs)
        return elapsedTime.toString("mm:ss")


def main():
    app = QApplication(sys.argv)
    labbook = Labbook()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()