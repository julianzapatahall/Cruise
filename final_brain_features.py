import time
import numpy as np
import pandas as pd

from sys import exit
import warnings
warnings.filterwarnings('ignore')

import brain_data_computations

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

class braindata:

    def __init__(self, boardID=-1, serial=''):
        self.isRunning = False
        self.myBoardID = boardID
        BoardShim.enable_dev_board_logger()
        self.params = BrainFlowInputParams()
        self.params.serial_port = serial
        # parameters for playing back a file
        # self.params.other_info = 0 # board id of headset used in file
        # self.params.file = 'OpenBCI-RAW-2021-10-31_13-45-28' # file name
        self.board = BoardShim(self.myBoardID, self.params)
        self.start_time = time.time()
        self.brain_df = pd.DataFrame()
        self.row_index = 0
        # self.all_data == 0
        self.is_5s = False
        self.features_list = ['mean_0', 'mean_d_h2h1_0', 'mean_q1_0', 'mean_q2_0', 'mean_q3_0',
        'mean_q4_0', 'mean_d_q1q2_0', 'mean_d_q1q3_0', 'mean_d_q1q4_0',
        'mean_d_q2q3_0', 'mean_d_q2q4_0', 'mean_d_q3q4_0', 'std_0',
        'std_d_h2h1_0', 'max_0', 'max_d_h2h1_0', 'max_q1_0', 'max_q2_0',
        'max_q3_0', 'max_q4_0', 'max_d_q1q2_0', 'max_d_q1q3_0', 'max_d_q1q4_0',
        'max_d_q2q3_0', 'max_d_q2q4_0', 'max_d_q3q4_0', 'min_0', 'min_d_h2h1_0',
        'min_q1_0', 'min_q2_0', 'min_q3_0', 'min_q4_0', 'min_d_q1q2_0',
        'min_d_q1q3_0', 'min_d_q1q4_0', 'min_d_q2q3_0', 'min_d_q2q4_0',
        'min_d_q3q4_0', 'topFreq_1_0', 'topFreq_2_0', 'topFreq_3_0',
        'topFreq_4_0', 'topFreq_5_0', 'topFreq_6_0', 'topFreq_7_0',
        'topFreq_8_0', 'topFreq_9_0', 'topFreq_10_0', 'freq_011_0',
        'freq_021_0', 'freq_032_0', 'freq_043_0', 'freq_053_0', 'freq_064_0',
        'freq_075_0', 'freq_085_0', 'freq_096_0', 'freq_107_0', 'freq_117_0',
        'freq_128_0', 'freq_139_0', 'freq_149_0', 'freq_160_0']
        self.brain_training_features = pd.DataFrame(columns=self.features_list)

    def startStream(self):
        """
        Tells the bord to being streaming data
        """
        BoardShim.enable_dev_board_logger()
        self.board.prepare_session()
        # initiate stream
        self.board.start_stream(45000, '')
        self.isRunning = True
        self.board.log_message(LogLevels.LEVEL_INFO, "Start sleeping in the main thread")
        # time.sleep(sleepTime)  # sleep 30 seconds
        # get the data
        self.data = self.board.get_board_data()

    def getData(self):
        """
        Gets the data from the board (presumably all of it since stream
        was started
        :return: The data from the board
        """
        return self.board.get_board_data()

    def getCurrentData(self, num_samples: int):
        """
        Gets the current (updated) data from the board
        :param num_samples: The amount of samples the returned ndarray will hold
        :return: The current board data
        """
        return self.board.get_current_board_data(num_samples)

    def getSamplingRate(self):
        """
        Get the rate at which the board samples data
        (i.e.: The muse has an SR of about 256 Hz
        :return: The sampling rate of a certain board
        """
        return self.board.get_sampling_rate(self.myBoardID)

    def getEEGChannels(self):
        """
        Gets the EEG channels from the board being used
        :return: The amt of channels for streaming EEG on the board
        """
        return self.board.get_eeg_channels(self.myBoardID)

    def stopStream(self):
        """
        Tells the board to stop streaming data
        """
        if self.isRunning:
            print('Stopping Stream')
            self.board.stop_stream()
            self.board.release_session()
        else:
            print("BOARD WAS NEVER STARTED")

    def run(self, streamTime: int):
        """
        Tells the board to run a specific test for a specific amt of time
        [FOR DEBUGGING]
        :param streamTime: The time the board will be streaming
        """
        BoardShim.enable_dev_board_logger()
        params = BrainFlowInputParams()

        # BOARD IDs internally in brainflow
        SYNTH_BOARD = int(-1)
        CYTON = int(0)
        MUSE2 = int(22)

        myCytonSerialPort = 'COM3'
        noSerial = ''

        params.serial_port = noSerial

        # create our board
        # board = BoardShim(SYNTH_BOARD, params)
        board = BoardShim(self.myBoardID, params)
        board.prepare_session()

        # initiate stream
        board.start_stream(45000, '')
        board.log_message(LogLevels.LEVEL_INFO, "Start sleeping in the main thread")
        time.sleep(streamTime)  # sleep 30 seconds

        # get the data
        self.data = board.get_board_data()

        # board.stop_stream()
        # board.release_session()

        print(self.data)  # for now print the data we can write it to a file

    def getBoard(self):
        """
        Lets us know what board we are using
        :return: The id of the board being used
        """
        if self.myBoardID == -1:
            print("Default Board is being used: SYNTHETIC")
        elif self.myBoardID == 0:
            print("OpenBCI Cyton is being used: CYTON")
        elif self.myBoardID == 22:
            print("Interaxon Muse 2 with bluetooth dongle is being used: MUSE2")
        elif self.myBoardID == 38:
            print("Interaxon Muse 2 without bluetooth dongle is being used: MUSE2")
        return self.myBoardID

    def setBoard(self, boardID: int):
        """
        Change the ID of the Board we are using
        :param boardID: -1 for Synth, 0 for Cyton, 22 for MUSE2
        """
        self.myBoardID = boardID

    def collectData(self):
        myBoard = braindata(-1, 'COM3')

        # alternative to while true loop since gets stuck when performing multiprocessing
        for i in range (0, 10000):
            # if type(myBoard.getCurrentData(1)) != int and type(myBoard.getCurrentData(1250)):
                # print(len(myBoard.getCurrentData(1)),len(myBoard.getCurrentData(1250)))
            # print(len(myBoard.getCurrentData(1)))
            total_brain_data = brain_data_computations.calc_feature_vector(myBoard.getCurrentData(1250).T)
            
            try:
                self.brain_training_features.columns = total_brain_data[-1]
            except ValueError:
                self.brain_training_features = pd.DataFrame(columns=total_brain_data[-1])
            self.brain_df = pd.DataFrame(columns=total_brain_data[-1])

            # every 5s collect one row of data
            if (int(time.time() - self.start_time)) % 5 == 1.0 and (int(time.time() - self.start_time)) != 0:
                self.is_5s = True
            elif (int(time.time() - self.start_time)) % 5 == 0.0 and (int(time.time() - self.start_time)) != 0 and self.is_5s == True:
                
                """
                # mean of each column based on number of rows outputted every 5s
                mean_brain = self.appended_summary_brain_df.iloc[:self.appended_summary_brain_df.shape[0]].mean(axis=0)
                # mean returns a pandas series, convert back to dataframe
                mean_brain_df = mean_brain.to_frame()
                # opposite dimensions, transpose
                self.transposed_mean_brain_df = mean_brain_df.T 
                """

                # append so dataframe continuously grows for 5 min
                self.brain_training_features.loc[len(self.brain_training_features)] = total_brain_data[0]
                self.is_5s = False
                self.row_index += 1
                print(self.brain_training_features)

                # for every feature where there are 1250 columns, take mean of these and compress into 63 features
                # 16 channels, 63 features, 1008 total columns
                # for self.features_list in range (0, len(self.features_list)):
                    # self.all_data = np.zeros((63, 1250))
                # np_brain_training_features = self.brain_training_features.to_numpy
                # np_brain_training_features.reshape()
                # print(np_brain_training_features)
                # print(self.brain_training_features)
                
                # create initial csv file for records
                self.brain_training_features.to_csv("brain.csv")
                
                # every 5s append one row to existing csv file to update records
                self.brain_training_features.loc[self.row_index - 1:self.row_index].to_csv("brain.csv", mode="a", header=False)

if __name__ == "__main__":
    myBoard = braindata(-1, 'COM3')
    myBoard.startStream()
    # myBoard.getSamplingRate()
    # myBoard.getEEGChannels()
    myBoard.collectData()
    # myBoard.stopStream() 