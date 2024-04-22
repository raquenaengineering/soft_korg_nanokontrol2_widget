import sys
import os
import time

import logging
logging.basicConfig(level=logging.WARNING)			# enable debug messages

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

)
from PyQt5 import QtCore
from PyQt5.QtCore import(
    QObject,
    QTimer,
    QThread,
    pyqtSignal
)
from PyQt5.QtGui import *


# MIDI COMMUNICATION #
import mido  # required import only for this specific update


# CUSTOM IMPORTS #

class korg_nanokontrol2_widget(QWidget):


    # CLASS VARIABLES #
    hw_ui_port = None
    channel = None                          # storage for the last channel which changed
    value = None                            # new value of the last changed channel
    param_list = None                       # list containing all available parameters to choose from (either given as parameter in constructor, or added with method)

    # signals #
    ui_changed = pyqtSignal(int ,int)       # first integer is the channel which changed, and the second the value


    def __init__(self):

        super().__init__()


        #self.chan_and_val.connect(self.custom_slot)     ## this I don't understand
        self.ui_changed.connect(self.update_widget_gui)
        #self.chan_and_val.emit()                                ## how do I put the parameters I read from update_widget_gui? # is this the right place to emit, indeed?



        #self.closeButton.setShortcut('Ctrl+D')  # shortcut key


        ## thread stuff ##

        # NOTE: we will start with a timer instead, as the implementation is simpler, but FUCKING MOVE THIS TO A THREAD !!!
        self.update_timer = QTimer()
        self.update_timer.setInterval(20)        # check for new messages every 100ms
        self.update_timer.timeout.connect(self.update_widget_gui)


        ## move to array version once started implementing response to device #
        # self.slider_pot_array = []
        # for i in range(1,12):
        #     slider_pot = slider_pot_3buttons()
        #     self.slider_pot_array.append(slider_pot)
        # self.setFixedWidth(1200)
        self.setFixedHeight(300)
        self.setFixedWidth(1200)
        # central widget #
        self.main_layout = QHBoxLayout()  # that's how we will lay out the window
        self.setLayout(self.main_layout)
        #korg control#
        self.control_side = control_nanokontrol()
        self.main_layout.addWidget(self.control_side)
        #self.main_layout.addWidget(self.control_side, alignment=QtCore.Qt.AlignRight)
        # sliders #
        self.sliders = slider_array()
        self.main_layout.addWidget(self.sliders)


        # start timers and threads #
        self.connect_hw_ui()

    def connect_hw_ui(self):                            # this method and update_hw_ui SHOULD BE MERGED !!!
        ports = mido.get_input_names()
        logging.debug(ports)
        try:
            port = ports[0]
            logging.debug(port)
            self.hw_ui_port = mido.open_input(port)
        except:
            logging.warning("No MIDI controller has been detected")
        else:
            logging.debug(self.hw_ui_port)
            self.update_timer.start()       # starts update_widget_gui
            logging.debug("connect_hw_ui finished, timer started")
            self.setEnabled(False)

    def update_widget_gui(self):
        #logging.debug("Updating GUI")
        for msg in self.hw_ui_port.iter_pending():
        # try:
        #     logging.debug(msg)
        # except:
        #     print("something got wrong processing messages")
        # else:
            try:
                msg = str(msg)
                msg_params = msg.split(" ")
            except Exception as e:
                print(e)
            else:
                #print(msg_params)
                channel_str = msg_params[2].split("=")
                channel_str = channel_str[1]
                channel = int(channel_str)
                logging.debug("Channel: " + str(channel))
                value_str = msg_params[3].split("=")
                value_str = value_str[1]
                value = int(value_str)
                logging.debug("Value: " + str(value))

                # PLAY MENU BUTTONS #
                default_button_color = self.control_side.player.prev_button.palette().button().color()
                #print(default_button_color)

                if(channel == 1):
                    if(value > 64):
                        self.control_side.player.prev_button.setDown(True)
                        self.control_side.player.prev_button.setStyleSheet("background-color: red")
                    else:
                        self.control_side.player.prev_button.setDown(False)
                        self.control_side.player.prev_button.setStyleSheet("background-color: "+str(default_button_color))

                if(channel == 2):
                    if(value > 64):
                        self.control_side.player.next_button.setDown(True)
                        self.control_side.player.next_button.setStyleSheet("background-color: red")
                    else:
                        self.control_side.player.next_button.setDown(False)
                        self.control_side.player.next_button.setStyleSheet("background-color: "+str(default_button_color))

                if(channel == 3):
                    if(value > 64):
                        self.control_side.player.stop_button.setDown(True)
                        self.control_side.player.stop_button.setStyleSheet("background-color: red")
                    else:
                        self.control_side.player.stop_button.setDown(False)
                        self.control_side.player.stop_button.setStyleSheet("background-color: "+str(default_button_color))

                if(channel == 4):
                    if(value > 64):
                        self.control_side.player.play_button.setDown(True)
                        self.control_side.player.play_button.setStyleSheet("background-color: red")
                    else:
                        self.control_side.player.play_button.setDown(False)
                        self.control_side.player.play_button.setStyleSheet("background-color: "+str(default_button_color))

                if(channel == 5):
                    if(value > 64):
                        self.control_side.player.rec_button.setDown(True)
                        self.control_side.player.rec_button.setStyleSheet("background-color: red")
                    else:
                        self.control_side.player.rec_button.setDown(False)
                        self.control_side.player.rec_button.setStyleSheet("background-color: "+str(default_button_color))

                # S buttons #
                for i in range(0,8):
                    if(channel == 32 + i):
                        if (value > 64):
                            self.sliders.slider_pot_array[i].button_s.setDown(True)
                            self.sliders.slider_pot_array[i].button_s.setStyleSheet("background-color: red")
                        else:
                            self.sliders.slider_pot_array[i].button_s.setDown(True)
                            self.sliders.slider_pot_array[i].button_s.setStyleSheet(
                                "background-color: " + str(default_button_color))
                # M buttons #
                for i in range(0,8):
                    if(channel == 48 + i):
                        if (value > 64):
                            self.sliders.slider_pot_array[i].button_m.setDown(True)
                            self.sliders.slider_pot_array[i].button_m.setStyleSheet("background-color: red")
                        else:
                            self.sliders.slider_pot_array[i].button_m.setDown(True)
                            self.sliders.slider_pot_array[i].button_m.setStyleSheet(
                                "background-color: " + str(default_button_color))
                # R buttons #
                for i in range(0,8):
                    if(channel == 64 + i):
                        if (value > 64):
                            self.sliders.slider_pot_array[i].button_r.setDown(True)
                            self.sliders.slider_pot_array[i].button_r.setStyleSheet("background-color: red")
                        else:
                            self.sliders.slider_pot_array[i].button_r.setDown(True)
                            self.sliders.slider_pot_array[i].button_r.setStyleSheet(
                                "background-color: " + str(default_button_color))

                # POTENTIOMETERS #
                for i in range(0,8):
                    if(channel == 16 + i):
                        self.sliders.slider_pot_array[i].pot.setValue(value)

                # SLIDERS #
                for i in range(0,8):
                    if(channel == 81 + i):
                        self.sliders.slider_pot_array[i].slider.setValue(value)


                self.channel = channel
                self.value = value

                self.ui_changed.emit(self.channel, self.value)

    def last_change(self):
        return(self.channel,self.value)

    def set_param_list(self, param_list):
        self.param_list = param_list

        for slider in self.sliders.slider_pot_array:
            for param in param_list:
                slider.var_selector.addItem(param)
                pass

    def update_controller(self):                                # UNFINISHED
        # cares of changing and updating the hardware controller of choice
        #self.connect_hw_ui()
        ports = mido.get_input_names()
        logging.debug(ports)
        try:
            port = self.hw_ui_port                          # should have been updated via the interface finder first
            self.hw_ui_port = mido.open_input(port)
        except:
            logging.warning("The selected MIDI device doesn't seem to be available")
        else:
            logging.debug(self.hw_ui_port)
            self.setEnabled(False)

class player_widget(QWidget):

    def __init__(self):
        super().__init__()

        # central widget #
        self.main_layout = QHBoxLayout()  # that's how we will lay out the window
        self.setLayout(self.main_layout)
        self.prev_button = QPushButton(u"\u23EE ")
        self.main_layout.addWidget(self.prev_button)
        self.next_button = QPushButton(u"\u23ED ")
        self.main_layout.addWidget(self.next_button)
        self.stop_button = QPushButton(u"\u25A0 ")
        self.main_layout.addWidget(self.stop_button)
        self.play_button = QPushButton(u"\u23F5  ")
        self.main_layout.addWidget(self.play_button)
        self.rec_button = QPushButton(u"\u23FA ")
        self.main_layout.addWidget(self.rec_button)

class control_nanokontrol(QWidget):

    def __init__(self):
        super().__init__()
        #self.setMinimumWidth(300)
        #self.setFixedWidth(400)
        self.setFixedWidth(300)
        # central widget #
        self.main_layout = QVBoxLayout()										# that's how we will lay out the window
        self.setLayout(self.main_layout)
        self.brand_label = QLabel("KORG")
        self.brand_label.setAlignment(QtCore.Qt.AlignCenter)
        self.brand_label.setFont(QFont('Arial', 16))
        self.main_layout.addWidget(self.brand_label)
        self.model_label = QLabel("nanoKONTROL2")
        self.model_label.setFont(QFont('Arial', 20))
        self.model_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.model_label)
        self.control_layout = QGridLayout()
        self.main_layout.addLayout(self.control_layout)
        self.button_track_back = QPushButton("<")
        self.control_layout.addWidget(self.button_track_back,1,1)
        self.button_track_forward = QPushButton(">")
        self.control_layout.addWidget(self.button_track_forward,1,2)
        self.button_cycle = QPushButton("CYCLE")
        self.control_layout.addWidget(self.button_cycle,2,1)
        self.button_set = QPushButton("SET")
        self.control_layout.addWidget(self.button_set,2,3)
        self.button_marker_next = QPushButton("<<<")
        self.control_layout.addWidget(self.button_marker_next,2,4)
        self.button_marker_prev = QPushButton(">>>")
        self.control_layout.addWidget(self.button_marker_prev,2,5)
        self.player = player_widget()
        self.main_layout.addWidget(self.player)

class slider_pot_3buttons(QWidget):

    # CLASS VARIABLES #


    # CLASS METHODS #

    def __init__(self):
        super().__init__()

        # central widget #
        self.main_layout = QVBoxLayout()										# that's how we will lay out the window
        self.setLayout(self.main_layout)
        self.var_selector = QComboBox()
        self.main_layout.addWidget(self.var_selector)
        self.pot = QDial()
        self.pot.setMaximum(127)                                                # max. allowed midi value
        self.main_layout.addWidget(self.pot)
        self.button_slider_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_slider_layout)
        self.buttons_layout = QVBoxLayout()
        self.button_slider_layout.addLayout(self.buttons_layout)
        self.button_s = QPushButton("S")
        self.buttons_layout.addWidget(self.button_s)
        self.button_m = QPushButton("M")
        self.buttons_layout.addWidget(self.button_m)
        self.button_r = QPushButton("R")
        self.buttons_layout.addWidget(self.button_r)
        self.slider = QSlider()
        self.slider.setMaximum(127)
        self.button_slider_layout.addWidget(self.slider)

class slider_array(QWidget):

    param_changed = pyqtSignal(int,str)     # first is the textbox slider number that has been changed, and second is the variable which will be edited on that slider

    def __init__(self):
        super().__init__()
        self.setMaximumWidth(800)
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.slider_pot_array = []
        for i in range(0,8):
            self.slider_pot = slider_pot_3buttons()
            self.slider_pot_array.append(self.slider_pot)
            self.main_layout.addWidget(self.slider_pot_array[i])

        for i in range(0,8):
            self.slider_pot_array[i].var_selector.currentTextChanged.connect(self.parameter_changed)

    def parameter_changed(self):
        logging.debug("Parameter changed method was called")
        for i in range(0,8):
            text = str(self.slider_pot_array[i].var_selector.currentText())
        logging.debug(text)


        self.param_changed.emit(1, text)         # only for testing


class MainWindow(QMainWindow):
    # class variables #

    # testing variables #
    param_list = ["pene","penis","schwanz","zib"]

    # constructor #
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testing korg nanokontrol widget")

        self.resize(1200, 300)  # setting initial window size
        # self.setFixedWidth(1200)
        self.setFixedHeight(300)
        # central widget #
        self.widget = QWidget()
        self.main_layout = QHBoxLayout()  # that's how we will lay out the window
        self.widget.setLayout(self.main_layout)
        self.korg_controller = korg_nanokontrol2_widget()
        self.korg_controller.ui_changed.connect(self.do_stuff)
        self.korg_controller.set_param_list(self.param_list)
        self.setCentralWidget(self.korg_controller)

        #self.korg_controller.param_changed.connect(self.get_target_parameters)

        self.show()  # window is created and destroyed every time we change the values

    def do_stuff(self):
        logging.debug("show_chan_and_val method called")
        channel, value = self.korg_controller.last_change()
        print("Channel: " + str(channel))
        print("Value: " + str(value))

    def get_target_parameters(self):
        print("get_target_parameters method was called")
        # # decide which slider has changed its parameter
        # self.param_changed.trigger()






if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # required to use it here
    mw = MainWindow()
    app.exec_()
