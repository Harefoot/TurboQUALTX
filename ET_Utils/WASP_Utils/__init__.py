
import numpy as np
import pandas as pd
import os

import datetime
from scipy.interpolate import interp1d

def GetDateTimeVal(df):
    DateTimeVal = []
    YEAR = np.asarray(df['YEAR'],dtype = int)
    MONTH = np.asarray(df['MONTH'],dtype = int)
    DAY = np.asarray(df['DAY'],dtype = int)
    HOUR = np.asarray(df['HOUR'],dtype = int)
    MINUTE = np.asarray(df['MINUTE'],dtype = int)

    for i in range(0,len(df)):
        DateTimeVal.append(datetime.datetime(YEAR[i],MONTH[i],DAY[i],HOUR[i],MINUTE[i]))
                           
    return DateTimeVal

#Function for unpivot a dataframe
def unpivot(df,Keep_VARIABLEs):
    #Unpivoting

    N, K = df.shape

    data = {'VARIABLE' : np.asarray(df.columns).repeat(N),
            'VALUE' : df.values.ravel('F')}

    up = pd.DataFrame(data, columns=['VARIABLE', 'VALUE'])
    #Append Keep_VARIABLEs as columns
    for KV in Keep_VARIABLEs:
        #np.tile constructs an array by repeating A the number of times given by reps
        up[KV] = np.tile(np.asarray(df[KV]), K)

    #filter out the VARIABLEs that we are already including as columns
    for KV in Keep_VARIABLEs:
        up = up[(up['VARIABLE']<> KV)]

    #Reorder the columns in the data frame such that the Keep_VARIABLEs
    #are on the left hand side and then followed by VARIABLE and VALUE
    reorder = Keep_VARIABLEs
    reorder.append('VARIABLE')
    reorder.append('VALUE')
    up = up[reorder]

    return up

def parse_WASPdays_datenum(df,basedate):
    DAYZ = np.asarray(df['DAYS'],dtype = float)
    N = len(df['DAYS'])
    YEAR = np.zeros(N)
    MONTH = np.zeros(N)
    DAY = np.zeros(N)
    HOUR = np.zeros(N)
    MINUTE = np.zeros(N)
    YYYYMMDD = np.zeros(N)
    DATETIME = []
    
    for i in range(0,N):
        DAYe = DAYZ[i]

        python_datetime = basedate + datetime.timedelta(DAYe)
        YEAR[i] = python_datetime.year
        MONTH[i] = python_datetime.month
        DAY[i] = python_datetime.day
        HOUR[i] = python_datetime.hour
        MINUTE[i] = python_datetime.minute
        YYYYMMDD[i] = YEAR[i]*10000+MONTH[i]*100+DAY[i]
        DATETIME.append(python_datetime.strftime('%m/%d/%Y %H:%M'))
    #put it all in a dataframe
    Sdict = {'YEAR':YEAR,'MONTH':MONTH,'DAY':DAY,'HOUR':HOUR,'MINUTE':MINUTE,'YYYYMMDD':YYYYMMDD,'DATETIME':DATETIME}

    #Convert it to a dataframe
    Datedf = pd.DataFrame(Sdict)
    df = pd.concat([Datedf, df], axis=1)
    return df

def Dates_to_MatlabDateNum(Inputdf,DateField):

    CCMODdf = Inputdf.copy()
    CCMODdf = CCMODdf.reset_index()
    DateTimeArr = CCMODdf[DateField]

    MatlabDateNum = []
    #a = datetime.datetime(1899, 12, 31,0,0)
    #fmt = '%Y-%m-%d %H:%M:%S %Z'
    
    for i in range(len(CCMODdf)):
        
        DateTimeElement= DateTimeArr[i]
        MatlabDateNum.append(datetime.datetime.toordinal(DateTimeElement)+366.+DateTimeElement.hour/24.+DateTimeElement.minute/3600.)       
                                        
    CCMODdf['MATLABDATENUM'] = MatlabDateNum
    return CCMODdf

def interpolate(x,y,x1):
    xnoNaN = x[np.isfinite(y) & np.isfinite(x)]
    ynoNaN = y[np.isfinite(y) & np.isfinite(x)]
    inds = xnoNaN.argsort()

    ynoNaN = ynoNaN[inds]
    xnoNaN = xnoNaN[inds]
    f = interp1d(xnoNaN,ynoNaN,bounds_error = False)
    return f(x1)
    
#Function that parses individual WASP csv files and unpivots them
def parseWASPcsv(modelpath,csvfile):
   print csvfile
   #Get parameter from csvfile name
   parameter = csvfile.split('.')[0]

   #Get num columns 
   df = pd.read_csv(os.path.join(modelpath,csvfile), skiprows = 1)   
   num_Segs = len(df.columns)-1#2
  
   column_names = ['Days']
   for i in range(1,num_Segs+1):
       column_names.append('Seg'+str(int(i)))

   column_names.append('STORETCODE')
   #print column_names
   column_names = np.asarray(column_names)
                                   
   df = pd.read_csv(os.path.join(modelpath,csvfile), skiprows = 1, header = None, names = column_names) #index_col = 0,   
       
   df['STORETCODE'] = np.asarray(df['STORETCODE'],dtype = '|S100')
   df['STORETCODE'][:] = parameter
   Keep_VARIABLEs = ['Days','STORETCODE'] 
   up = unpivot(df,Keep_VARIABLEs)
      
   return up#,mindepth_filter
    
#def prep_model_results(modelpath, outputpath, csvfiles_of_interest,SegmentsOfInterest, calibration_csv, basedate, mindepth, num_Segs):    
def prep_model_results(modelpath, outputpath, pdf,SegmentsOfInterest, calibration_csv, basedate):    
    
    #Get a list of which files to read
    csvfiles_of_interest = []
    #parameters_of_interest = pdf['PlotParameter']
    #for parameter in parameters_of_interest:
    for i in pdf.index:
        if pdf['PlotFlag'][i]==1:
            csvfiles_of_interest.append(pdf['PlotParameter'][i] + '.csv')
 
    #Use only unique see http://stackoverflow.com/questions/12897374/get-unique-VALUEs-from-a-list-in-python
    csvfiles_of_interest = list(set(csvfiles_of_interest))
    
    #Need to find way to figure out the number of segments automatically
    
    if os.path.exists(outputpath) == False:
        os.mkdir(outputpath)
            
    os.chdir(modelpath)
    
    #Use segment depth as base file
    #Basedf = parseWASPcsv(modelpath,'Segment_Depth.csv').reset_index()
    #Basedf,mindepth_filter = parseWASPcsv_SegDepth(modelpath,'Segment_Depth.csv',mindepth)
    Basedf = parseWASPcsv(modelpath,'Segment_Depth.csv')
    Basedf = Basedf.reset_index()
    Basedf.columns = ['index','DAYS', 'STORETCODE', 'SITECODE','SEGMENT_DEPTH']
    Basedf = Basedf[['DAYS', 'SITECODE','SEGMENT_DEPTH']]
      
    Basedf = parse_WASPdays_datenum(Basedf,basedate)
     
    #Define timeseries columns
    Tcols = ['AGENCY','SITECODE','MONTH','DAY','YEAR','HOUR','MINUTE','DATE','YYYYMMDD','QUALIFIER',
              'SEGMENT_DEPTH','DATATYPE','STORETCODE','VALUE_ORIG','STORETCODE_NEW','VALUE_NEW']
    #Basedf['MIN_SEG_DEP'] = match['SEGMENT_DEPTH_min']            
    Basedf['AGENCY'] = np.asarray(Basedf['SITECODE'], dtype = str)
    Basedf['AGENCY'][:] = 'WASP model' #+ modelpath
    Basedf['DATATYPE'] = np.asarray(Basedf['SITECODE'], dtype = str)
    Basedf['DATATYPE'][:] = 'WASP_results'
    Basedf['DATE'] = Basedf['DATETIME']
    Basedf['QUALIFIER'] = Basedf['SITECODE']
    Basedf['QUALIFIER'] = ''
    #Basedf['QUALIFIER'][Basedf['SEGMENT_DEPTH']<= mindepth] = 'DRY SEGMENT'
    
    #Basedf.to_csv(os.path.join(outputpath,'Basedf.csv'),index = False)                            
    #If you want to get a list of all WASP outputfiles
    # just print allcsvfiles
    #Process all other csvfiles
    #for csvfile in allcsvfiles[(allcsvfiles !='SEGMENT_DEPTH')]:
    Builder = Basedf.copy()
    for csvfile in csvfiles_of_interest:        
       df = parseWASPcsv(modelpath,csvfile).reset_index()
       df2 = pd.concat([Basedf, df[['STORETCODE','VALUE']]], axis=1)      
       df2['VALUE_ORIG'] = df2['VALUE']
       df2['VALUE_NEW'] = df2['VALUE']
       df2['STORETCODE_NEW'] = df2['STORETCODE']
       df2 = df2[Tcols]#.reset_index()                    
       #df2.to_csv(os.path.join(outputpath,'TimeSeries_'+csvfile),index = False)
       col_name = df2['STORETCODE'][0]
       Builder[col_name] = df2['VALUE_NEW']
 
    Builder['TKN'] = Builder['Total_Organic_N'] +Builder['Ammonia']
    Builder.to_csv(os.path.join(outputpath,'TimeSeries_WQ_multicolumns.csv'),index = False)
          
    #When calibrating, only extract cells from segments of interest
    Boris = Builder[Builder['SITECODE'].isin(SegmentsOfInterest)]
    
    #Keep_VARIABLEs = ['DATETIME','	DAY','HOUR','MINUTE','	MONTH','YEAR','YYYYMMDD','DAYS','SITECODE','IMPACT_BY_DRY_FLAG','SEGMENT_DEPTH','AGENCY','DATATYPE','DATE','QUALIFIER','Unstable_flag']
    Keep_VARIABLEs = ['AGENCY','SITECODE','MONTH','DAY','YEAR','HOUR','MINUTE','DATE','DATETIME','YYYYMMDD','QUALIFIER','SEGMENT_DEPTH','DATATYPE']
    Calibdf = unpivot(Boris,Keep_VARIABLEs)
    Calibdf['STORETCODE'] = Calibdf['VARIABLE']
    Calibdf['VALUE_ORIG'] = Calibdf['VALUE']
    Calibdf['STORETCODE_NEW'] = Calibdf['VARIABLE']
    Calibdf['VALUE_NEW'] = Calibdf['VALUE']
    #Tcols.append('Unstable_flag')
    Calibdf = Calibdf[Tcols]
    Calibdf = Calibdf[Calibdf['STORETCODE']!='DAYS']
    
    columns = list(Calibdf.columns)
    
    Calibdf = pd.merge(Calibdf,pdf,how = 'inner', left_on = 'STORETCODE', right_on = 'PlotParameter')
    Calibdf['VARIABLE']=Calibdf['PlotParameter']
    Calibdf['UNIT']=Calibdf['Units']
    
    columns.append('VARIABLE')
    columns.append('UNIT')
    
    Calibdf = Calibdf[columns]
    Calibdf['DEPTH_IN_METERS'] = Calibdf['SEGMENT_DEPTH'][:]/2
    #Calibdf = Calibdf.reset_index()
    
    Calibdf.to_csv(calibration_csv,index = False)
        
#---------------------------------------------------------------------------------------------------------------------------------
def main_processor(modelpath, pdf, prep_model_results_flag,SegmentsOfInterest,basedate):
    
    outputpath = os.path.join(modelpath,'parsed')

    #sitecodes_of_interest = ['OsoPlant','HRI_WestOso','HRI_OsoWard','HRI_OsoMouthShallow','HRI_NAS','HRI_Hwy358']
    #sitecodes_plot_names = ['Oso Plant Outfall Channel','West Oso','Ward','Near Oso Mouth','NAS','Hwy358']
    
    #SiteNames = ['Basin','Waller Ck','Lamar & South First Bridges','Barton Ck','Redbud Isle','Tom Miller Dam']

    calibration_csv = os.path.join(outputpath,'TimeSeries_Calibration.csv')
    
    #basedataYYYYMMDD = 20120701  
        
    #Plot_OsoMouthDeep_flag =0 #specify whether to plot Oso Mouth Deep
    if prep_model_results_flag == 1:
        print 'Prepare calibration file'
        #prep_model_results(modelpath, outputpath, csvfiles_of_interest,SegmentsOfInterest, calibration_csv, basedate,mindepth,num_Segs)
        prep_model_results(modelpath, outputpath, pdf,SegmentsOfInterest, calibration_csv, basedate)
        

    #print 'Read model results'
    #Calibdf = pd.read_csv(calibration_csv)
    #Calibdf['DATETIMEVAL'] = GetDateTimeVal(Calibdf)

#============================================================MAIN DECK=======================================================================================
def MAIN_DECK(modelpaths, SegmentsOfInterest,basedate):
    print 'Start processing...'
    #modelpaths = [r'C:\G\LS20_Seg43_162MGD_20BOD5_20_4_5_4_20150615_cent_adj3']
           
    prep_model_results_flag = 1
    parameter_key_file =os.path.join(os.path.dirname(__file__),'ParameterKey.csv')
    print parameter_key_file
    #parameter_key_file = r'D:\APAI\M_drive\Projects\0382\022-05\2-0 Wrk Prod\Models\WASP\LBL\PostProcessing\Calibration\ParameterKey.csv'
    pdf = pd.read_csv(parameter_key_file)
    #pdf = pdf[pdf['PlotFlag']==1]    
    
    for modelpath in modelpaths:
        print modelpath
        main_processor(modelpath, pdf, prep_model_results_flag,SegmentsOfInterest,basedate)    
    
    print "done!"

if __name__ == '__main__':
#    Just as an example 
    modelpaths = [r'C:\G_Drive\LadyBirdLake\WASP\20151216_1049']
    SegmentsOfInterest = ['Seg31','Seg57','Seg67','Seg69','Seg73','Seg80','Seg117','Seg124']
    basedate = datetime.datetime(2012,7,1,0,0)
    MAIN_DECK(modelpaths, SegmentsOfInterest,basedate)