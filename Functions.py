import os; import numpy as np; import time; import serial

''' Device functions'''
# connect to the LCR meter through serial communication
def DeviceConnect(COMPort):
    ser = serial.Serial(COMPort, baudrate = 19200, timeout = 10)
    return ser

# disconnect the LCR meter 
def DeviceDisconnect(ser):
    return ser.close()

# define function to send commands to the LCR meter and wait for a response.
def LCRWriter(ser, command):
    # encode text to ascii.
    ser.write(f'{command}\n'.encode())

# actual experiment
def Experiment(ser, frequencies, measurement, voltage):
    '''LCR setup'''
    # set the measuerement voltage, range, and speed
    LCRWriter(ser, f'LEVel:AC {voltage}')
    LCRWriter(ser, f'MEASurement:RANGe AUTO')
    LCRWriter(ser, f'MEASurement:FUNC {measurement}')

    # set the frequency sweep mode to log. define the starting and end frequences,
    # and make the LCR meter automatically determine the points. 
    LCRWriter(ser, f'SWEEp:FREQ:STARt {frequencies[0]}')
    LCRWriter(ser, f'SWEEp:FREQ:STOP {frequencies[1]}')
    LCRWriter(ser, f'SWEEp:Mode LOG')
    
    '''Major measurement'''
    # start the sweep then allow 2 minutes to collect the data
    LCRWriter(ser, 'SWEEp:STARt 1')
    time.sleep(130)

    # request all data, then read the bit lines
    LCRWriter(ser, f'SWEEp:DATA:ALL?')
    data = ser.readlines()

    # decode the data and store in temp array
    data1 = np.array([data[i].decode('utf-8').split(',') for i in range(0, len(data))], dtype = float)
    data1 = np.delete(data1, 0, axis = 1)
    
    
    '''Minor measurement'''
    # start the second sweep then allow 2 minutes to collect the data
    LCRWriter(ser, 'SWEEp:SWAP 1')
    LCRWriter(ser, 'SWEEp:STARt 1')
    time.sleep(130)

    # request all data, then read the bit lines
    LCRWriter(ser, f'SWEEp:DATA:ALL?')
    data = ser.readlines()

    data2 = np.array([data[i].decode('utf-8').split(',') for i in range(0, len(data))], dtype = float)
    data2 = np.delete(data2, [0, 1], axis = 1)

    # concate the major and minor data 
    Data= np.hstack([data1, data2])  

    
    print('Test completed ✅\n\n')
    return Data

def DataExport(params, Data, info):
    fileName = f'{params}'
    if os.path.isfile(fileName) == 0:
        np.savetxt(f"Data/{fileName}.csv", Data, header = 'Freqency (Hz), Impedance (Ohm), Loss Tangent (deg)', delimiter = ",",
                   fmt = "%f", comments = f'{info}\n\n')
    elif os.path.isfile(fileName) == 1:
        os.remove(fileName)
        np.savetxt(f"Data/{fileName}.csv", Data, header = 'Freqency (Hz), Impedance (Ohm), Loss Tangent (deg)', delimiter = ",",
                   fmt = "%f", comments = f'{info}\n\n')