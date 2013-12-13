import datetime
import math 
from mrjob.job import MRJob


class DataCombiner(MRJob):
    # number of total columns in each separate dataframe
    AIR_FIELDS = 18
    WEATHER_FIELDS = 15

    # column indices for various fields
    DEP_TIME_COL = 4
    AIR_DATE_COL = 9
    ORIGIN_COL = 13

    WEATHER_DATETIME_COL = 2
    WEATHER_STATION_COL = 10


    def mapper(self, _, line):
        full_line = line.split(',')
        
        #tweak military time to be consistent with 6 digits. 
        
        # for flight data
        if(len(full_line) == self.AIR_FIELDS):
            
            time_flight = str(full_line[self.DEP_TIME_COL])
            if(time_flight != 'CRS_DEP_TIME'):    

                #round up or down based on the minutes of the flight so that it matches with our weather data
                time_flight = float(time_flight)
                hours = str(int(round(time_flight/100)) % 24)
                
                # create the date and time object and combine them together.  
                datetime_str = full_line[self.AIR_DATE_COL] + ' ' + hours + ':00:00'
                # convert to datetime object and back for formatting so 7:45 becomes 07:45
                final_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                datetime_str = str(final_datetime)
                
                origin = full_line[self.ORIGIN_COL]   # change it back from 5 to 10 for the full dataset!!!
                key = (origin, datetime_str)
                yield key, ('Flight', full_line)

        # for weather data 
        if(len(full_line) == self.WEATHER_FIELDS):
            time_data = full_line[self.WEATHER_DATETIME_COL]
            if(time_data != "Datetime"):
                station = full_line[self.WEATHER_STATION_COL]
                key = (station, time_data)
                yield key, ('Weather',full_line)


    def reducer(self, key, values):
        # first find the value corresponding to the weather conditions
        rows = list(values)
        weatherdata = None
        flightdata = []
        for indicator, data in rows:
            if indicator == 'Weather':
                weatherdata = ','.join(data)
            else:
                flightdata.append(','.join(data))

        # error checking for flights with no weather data or vice versa
        if (weatherdata is None) or not flightdata:
            #Do something else here
            emptyline = ['']*(self.AIR_FIELDS + self.WEATHER_FIELDS)
            output = None#','.join(emptyline)
            return
        else:
            # now loop through all the remaining values, which are flight data
            lines = []
            for flight in flightdata:
                line = ','.join([flight, weatherdata])
                lines.append(line)
            output = '\n'.join(lines)
        print output
        return
        yield None, output
        
    

#Below MUST be there for things to work
if __name__ == '__main__':
    DataCombiner.run()