import sys
import os
import time

import logging
logging.basicConfig(level=logging.DEBUG)			# enable debug messages

from PyQt5.QtWidgets import(
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,																# create a new widget, which contains the MyGraph window
    QVBoxLayout,
    QLabel,
    QComboBox,
    QDial,
    QPushButton,
    QSlider,
    QGridLayout,
    QListWidget

)
from PyQt5 import QtCore
from PyQt5.QtCore import(
    QObject,
    QTimer,
    QThread,
    pyqtSignal,
    Qt
)
from PyQt5.QtGui import *


# MIDI COMMUNICATION #
import mido  # required import only for this specific update


# CUSTOM IMPORTS #

class midi_interface_finder(QWidget):

    done_finding = pyqtSignal(str)                 # and I will return the device name using this signal
    interface_name = None

    def __init__(self):

        # CLASS VARIABLES #

        hw_ui_port = None


        super().__init__()

        ## thread stuff ##

        # NOTE: we will start with a timer instead, as the implementation is simpler, but FUCKING MOVE THIS TO A THREAD !!!
        self.update_timer = QTimer()
        self.update_timer.setInterval(1000)        # check for new messages every 100ms
        self.update_timer.timeout.connect(self.update_device_list)

        # signals stuff #
        # we will need a signal to be triggered when the interface is chosen
        self.inferface_selected = pyqtSignal()

        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedHeight(300)
        # central widget #
        self.main_layout = QVBoxLayout()  # that's how we will lay out the window
        self.setLayout(self.main_layout)
        #midi device list#
        self.midi_device_list = QListWidget()
        self.main_layout.addWidget(self.midi_device_list)
        self.midi_device_list.doubleClicked.connect(self.on_item_double_click)
        #buttons#
        self.buttons_layout = QHBoxLayout()
        self.main_layout.addLayout(self.buttons_layout)
        self.button_update = QPushButton("Update")
        self.buttons_layout.addWidget(self.button_update)
        self.button_update.clicked.connect(self.update_device_list)
        self.button_select = QPushButton("Select")
        self.button_select.clicked.connect(self.on_select_button)
        self.buttons_layout.addWidget(self.button_select)
        self.button_cancel = QPushButton("Cancel")
        self.button_cancel.clicked.connect(self.on_cancel_button)
        self.buttons_layout.addWidget(self.button_cancel)
        # start timers and threads #
        self.connect_hw_ui()
        # other initialisation requirements #
        self.update_device_list()

    def connect_hw_ui(self):
        pass

    def update_device_list(self):
        print("Updating device list")
        ports = mido.get_input_names()
        self.midi_device_list.clear()
        for port in ports:
            print(port)
            self.midi_device_list.addItem(port)

        # set the first item on the list as the default selected
        self.midi_device_list.setCurrentRow(0)

    def on_select_button(self):
        print("select button clicked")
        try:
            self.done_finding.emit(self.midi_device_list.currentItem().text())
        except:
            self.done_finding.emit(None)
            logging.warning("No interface was found/selected")
        self.close()
        return()
    def on_cancel_button(self):
        self.close()                    # this closes only the widget, but not the parent window
        # trigger here a signal the main window can read, and close itself also
    def on_item_double_click(self):
        print("on_item_double_click method called")
        self.on_select_button()


class MainWindow(QMainWindow):
    # class variables #

    # constructor #
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testing midi_interface_finder widget")

        self.resize(400, 300)  # setting initial window size
        # self.setFixedWidth(1200)
        self.setFixedHeight(300)
        # central widget #
        self.widget = QWidget()
        self.main_layout = QHBoxLayout()  # that's how we will lay out the window
        self.widget.setLayout(self.main_layout)
        self.midi_finder = midi_interface_finder()
        self.setCentralWidget(self.midi_finder)
        self.show()  # window is created and destroyed every time we change the values

        #set shortcuts#
        #self.closeButton.setShortcut('Ctrl+D')  # shortcut key

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # required to use it here
    mw = MainWindow()
    app.exec_()
