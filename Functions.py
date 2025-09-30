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


# define the frequency range and the number of points evenly spaced
def Frequencies(minFreq, maxFreq, numberOfpoints):
    frequencies = np.logspace(np.log10(minFreq), np.log10(maxFreq), num = numberOfpoints).astype(int)
    return np.round(frequencies).astype(int)


# create a stablity timer based on frequency
def TimeAdjustments(freq):
    if freq < 100:
        time.sleep(0.5)
    elif freq <=1000:
        time.sleep(0.1)
 

# collect the average data values 
def DataAveraging(ser, frequency):
    # preallocate data storage array
    data = np.zeros([0, 2])

    # take 5 measurements
    for i in range(0, 20):
        # add time delay between meaurement
        TimeAdjustments(frequency)

        # fetch data 
        LCRWriter(ser, f'FETCh?')

        # decode and remove acsii terms 
        readout = ser.readline().decode('utf-8').replace(' ','').replace('\r\n','').split(',')
        readout[0] = readout[0].removesuffix('F')
        readout = [float(k) for k in readout]
        
        # store readout for averaging
        data = np.vstack([data, readout])
    
    # remove the first element which was used to preallocatte the array
    data = np.mean(data, axis = 0)
    
    # determine the data statistics.
    data = np.insert(data, 0, frequency)
    print(f'{data}\n')
    return data


# actual experiment
def Experiment(ser, frequencies, numberOfpoints, measurement, voltage):
    # set the measurement voltage, range, speed, measurement, and output mode
    LCRWriter(ser, f'LEVel:AC {voltage}')
    LCRWriter(ser, f'MEASurement:RANGe AUTO')
    LCRWriter(ser, f'MEASurement:SPEEd 1')
    LCRWriter(ser, f'MEASurement:FUNC {measurement}')
    LCRWriter(ser, 'DISP:MODE 1')
    LCRWriter(ser, 'DISP:FONT 0')

    # preallocate Data array
    Data = np.zeros([0, 3])

    # define the starting and end frequences and collect the data. 
    frequencies = Frequencies(frequencies[0], frequencies[-1], numberOfpoints = numberOfpoints)
    print(f'Frequencies: {frequencies}\n\n')
    for i in frequencies:
        # set frequency
        print(f'Frequency: {i}')
        LCRWriter(ser, f'FREQ {i}')

        # read data and store the results
        Data = np.vstack([Data, DataAveraging(ser, i)])

    # complete test
    print('Test completed ✅\n\n')
    return Data


# data export
def DataExport(params, Data, info):
    fileName = f'{params}'
    if os.path.isfile(fileName) == 0:
        np.savetxt(f"Data/{fileName}.csv", Data, header = 'Freqency (Hz), Capacitance (F), Dissipation Factor', delimiter = ",",
                   fmt = "%e", comments = f'{info}\n\n')
    elif os.path.isfile(fileName) == 1:
        os.remove(fileName)
        np.savetxt(f"Data/{fileName}.csv", Data, header = 'Freqency (Hz), Capacitance (F), Dissipation Factor', delimiter = ",",
                   fmt = "%e", comments = f'{info}\n\n')