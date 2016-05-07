#import os
#import numpy as np
import pandas as pd
import os
pd.options.mode.chained_assignment = None  # default='warn'

import sys
currentpath = os.path.dirname(__file__)
sys.path.insert(0,currentpath)


import ET_Utils.QUALTX_Utils

    
#inputfolder = r'\\aus1.aus.apai\share\Projects\0449\072-01\Riverbend\2-0 Wrk Prod\Models\FromTCEQ_20160205'
#QUALTXoutfiles = ['Rhod9.out','Rhod10.out','Rhod11.out','Rhod12.out']
#
inputfolder = r'C:\Users\Ernest\Ernest_Sandbox\jupyter'
QUALTXoutfile = "RB55NOV.OUT"
Scenario = QUALTXoutfile
DOstds = [5,4.8]
WQC_of_interest = ['DO_MG/L','BOD_MG/L','NH3_MG/L','NO3+2_MG/L','PHOS_MG/L']
#ET_Utils.QUALTX_Utils.Process_QUALTX(inputfolder,QUALTXoutfile,Scenario,DOstds = DOstds)
#Scenario_xlsx = r'M:\Projects\0449\072-01\Riverbend\2-0 Wrk Prod\Models\ResultsSummary\Scenarios_Results_summary_Riverbend_20160316_1242.xlsx'
StreamNames, Rdf, Hdf, AllWQdf = ET_Utils.QUALTX_Utils.Process_QUALTX(inputfolder,QUALTXoutfile,
                                                                      Scenario,DOstds = DOstds,
                                                                      WQC_of_interest = WQC_of_interest,
                                                                      loc = 1,plot_pdf = 1)
