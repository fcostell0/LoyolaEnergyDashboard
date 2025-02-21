'''
DataReader
Version: 1.1
Last Update: 10/17/24

This program reads in Loyola's BGE data and outputs as a single csv file to be used later
'''

import pandas as pd


# Class to handle data from each meter csv
class MeterData:
    # Dataframe of each meter and its respective building
    meterDF = pd.read_csv('meters.csv')
    # Dataframe of occupancy in each building
    occupancyDF = pd.read_csv('occupancy.csv')

    def __init__(self, originalCSVFile):
        
        # Store initial dataframe
        self.sourceDataFrame = pd.read_csv(originalCSVFile, skiprows=4)

        # Pull metadata from initial dataframe
        self.dataType = self.sourceDataFrame.loc[0,'Type']
        self.dataUnit = self.sourceDataFrame.loc[0,'Usage Unit']
        self.meterNumber = self.sourceDataFrame.loc[0,'Meter']
        self.buildingName = MeterData.meterDF.loc[MeterData.meterDF['meterNum'] == self.meterNumber, 'building'].values[0]

        # Building characteristics
        self.buildingSquareFootage = None
        self.buildingOccupancy = MeterData.occupancyDF.loc[MeterData.occupancyDF['building'] == self.buildingName, 'occupancy'].values[0]

        tempDF = self.standardizeTime(self.sourceDataFrame)

        # Output as a clean dataframe
        self.outputData = self.processData(tempDF)

    # Standardize the time data
    # Electric comes in 15 minute intervals while gas comes hourly, needs to be resolved
    def standardizeTime(self, dataframe):

        # Standardize as pandas datetime, set as index, and drop unnecessary columns
        dataframe['datetime'] = pd.to_datetime(dataframe['Date'] + ' '  + dataframe['Start Time'])
        dataframe.set_index(['datetime'], inplace=True)
        dataframe = dataframe.drop(['Date', 'Start Time'], axis = 1)

        # Resample rules
        dataframe = dataframe.resample('h').agg({
            'Type':'first',
            'Meter':'first',
            'Usage Unit':'first',
            'Usage':'sum'
        })

        return dataframe
    
    # Final process of data to be outputted
    def processData(self, dataframe):
        tempDF = dataframe

        tempDF = tempDF.drop(['Meter'], axis=1)

        # Add columns with new data
        tempDF['Building'] = self.buildingName
        tempDF['Occupancy'] = self.buildingOccupancy
        #tempDF['SquareFootage'] = self.buildingSquareFootage

        # Re-index dataframe
        tempDF.set_index('Building', append=True,inplace=True)

        return tempDF

def main():
    # Initialize empty dataframe to constantly append to
    outputDF = pd.DataFrame()

    # Allow for user to input multiple files
    while True:
        userInput = input("Please enter a filename or STOP to stop" + "\n")

        # Add error checking later
        if(userInput == "STOP"):
            break
        else:
            tempDF = MeterData(userInput).outputData
            outputDF = pd.concat([outputDF,tempDF])

    # Combine rows for multiple buildings into one, avoid summing gas/electric data together
    outputDF = outputDF.groupby(['Building','datetime','Type']).agg({
        'Usage Unit':'first',
        'Usage':'sum',
        'Occupancy':'first'
    }).reset_index()



    # Output to csv
    outputDF.to_csv('output.csv')

main()