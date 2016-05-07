import os
import numpy as np
import datetime
import pandas as pd

def Parse_Dates(Inputdf,DateField,parseYYYYMMDD = False):
    print 'Parsing dates'
    CCMODdf = Inputdf.copy()    
    DateTimeStrArr = CCMODdf[DateField]
    DateTimeArr = []
    MatlabDateNum = []
    HECRASDate = []
    DateArr = []
    TimeArr = []
    
    if parseYYYYMMDD == True:
        YEAR = []
        MONTH = []
        DAY = []
        HOUR = []
        MINUTE = []
        YYYYMMDD = []
    #a = datetime.datetime(1899, 12, 31,0,0)
    #fmt = '%Y-%m-%d %H:%M:%S %Z'
    
    for i in CCMODdf.index:
        
        DateTimeStr = DateTimeStrArr[i]
        #print DateTimeStr
        if (type(DateTimeStr) == datetime.datetime) | (type(DateTimeStr) == pd.tslib.Timestamp):
            DateTimeElement = DateTimeStr
        else:            
            try:
                DateTimeElement = datetime.datetime.strptime(DateTimeStr, "%m/%d/%Y %H:%M")
            except ValueError:
                try:
                    DateTimeElement = datetime.datetime.strptime(DateTimeStr, "%m/%d/%Y")
                except ValueError:                    
                    try:
                        DateTimeElement = datetime.datetime.strptime(DateTimeStr, "%Y-%m-%d %H:%M:%S")
                    except ValueError:  
                        try:
                            DateTimeElement = datetime.datetime.strptime(DateTimeStr, "%Y-%m-%d")
                        except ValueError:
                            DateTimeElement = datetime.datetime.strptime(DateTimeStr, "%m/%d/%Y %H:%M:%S")
                            
        DateTimeArr.append(DateTimeElement)       

        #Matlab's datenum representation is the number of days since midnight on Jan 1st, 0 AD.
        #Python's datetime.fromordinal function assumes time is the number of days since midnight on Jan 1st, 1 AD.
        #Therefpore need to account for the 366 days in '0AD' (actually 1 BC to be exact)
        MatlabDateNum.append(datetime.datetime.toordinal(DateTimeElement)+366)       
        HECRASDate.append(datetime.datetime.strftime(DateTimeElement,"%d%b%Y %H:%M:%S"))                             
        DateArr.append(datetime.datetime.strftime(DateTimeElement,"%m/%d/%Y"))
        TimeArr.append(datetime.datetime.strftime(DateTimeElement,"%H:%M"))
        
        if parseYYYYMMDD == True:
            YEAR.append(DateTimeElement.year)
            MONTH.append(DateTimeElement.month)
            DAY.append(DateTimeElement.day)
            HOUR.append(DateTimeElement.hour)
            MINUTE.append(DateTimeElement.minute)
            YYYYMMDD.append(datetime.datetime.strftime(DateTimeElement,"%Y%m%d"))
            
    CCMODdf['DATETIME'] = DateTimeArr        
    CCMODdf['MATLABDATENUM'] = MatlabDateNum
    CCMODdf['HECRASDate'] = HECRASDate
    
    CCMODdf['DateArr'] = DateArr
    CCMODdf['TimeArr'] =TimeArr

    if parseYYYYMMDD == True:
        CCMODdf['YEAR'] = YEAR
        CCMODdf['MONTH'] = MONTH
        CCMODdf['DAY'] = DAY
        CCMODdf['HOUR'] = HOUR
        CCMODdf['MINUTE'] = MINUTE
        CCMODdf['YYYYMMDD'] = YYYYMMDD
            
    print 'Done parsing dates'
    return CCMODdf
    
    