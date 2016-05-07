#ET 20160210
#This script reads in a QUALTX output file and figures out what and where the DO sag is
import os
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import sys
sys.path.insert(0,r'M:\Library\Python\Packages')


import struct

def parse_card_df(ldf,REACH_cols,fws,value_row_offset,startstring,endstring):
   
    REACH_mask =  ldf.index[ldf['lines'] == startstring]
    columns = REACH_cols
    
    count = REACH_mask[0]+value_row_offset    
    
    ENDmask = ldf.index[ldf['lines'] == endstring][0]
    #print count
    #print ENDmask
    cldf = ldf[count:ENDmask].reset_index()
    
    blanks = np.asarray(np.zeros(len(cldf)),dtype = str)
    blanks[:] = ""
    for column in columns:
        #print column
        cldf[column] = blanks
    
    #fws = [12,3,2,32,10,10,10]
    fwstr = ""    
    for fw in fws:    
        fwstr = fwstr+str(fw)+'s'
    
    for i in cldf.index:
        templine = cldf['lines'][i]
        #Scroll all the way to the right to see the end of the statement below
        templine = (templine + '                                                                                                                           ')[0:np.sum(fws)]
#        print templine
        values = struct.unpack(fwstr,templine)
        values = [value.strip() for value in values]
        if startstring =='$$$ DATA TYPE 8 (REACH IDENTIFICATION DATA) $$$':
            values[4] = values[4].split("TO")[0].strip()
            temp = values[3].split(" TO ")
            values.append(temp[0].strip())
            try:
                values.append(temp[1].strip())
            except IndexError:
                print "Can't split by 'TO'"
                pass                    

        if startstring =='$$$ DATA TYPE 21 (HEADWATER DATA FOR DO, BOD, AND NITROGEN) $$$':
            #Remove any illegal characters and replace with underscores
            Illegal_chars = [r"/",r"*"]
            for Illegal_char in Illegal_chars:
                values[2] = '_'.join(values[2].split(Illegal_char))            

        for j in range(len(columns)):
            #print i
            #print columns[j]
            #print values[j]
            cldf[columns[j]][i] = values[j]
    
    cldf = cldf[columns]
    return cldf
    #f.close()   
    
def parse_QUALTXoutfile(inputfolder, QUALTXoutfile):

    #---------------------------------------------------------------------------------------------------------
    #Hard code in the WQC headers
    WQC = ['ELEM_NO.', 'ENDING_DIST', 'TEMP_DEG_C', 'SALN_PPT', 'CM-I_*', 'CM-II_*', 'DO_MG/L',
                'BOD_MG/L', 'EBOD_MG/L', 'ORGN_MG/L', 'NH3_MG/L', 'NO3+2_MG/L', 'TOTN_MG/L',
                'PHOS_MG/L', 'CHL_A_UG/L', 'MACRO_**', 'COLI_#/100ML', 'NCM_*']
    
    #---------------------------------------------------------------------------------------------------------
    #Figure out the original input file first
    #Read all rows into a 1D array
    f = open(QUALTXoutfile,'r')
    lines = f.readlines()
    f.close()
    
    #Save lines as dataframe for querying
    Sdict = {'lines':lines}
    ldf = pd.DataFrame(Sdict)
    
    #remove the silly \n
    #and remove leading leading and trailing spaces
    for i in ldf.index:
        templine = ldf['lines'][i].strip()
        ldf['lines'][i] = templine.split('\n')[0]
    
        
    ldf['CARD'] = ldf['lines']
    ldf['CARD'][:] = ''
    
    #We are only interested in reading results from the outputfile
    #no need to read echos from input file
    #Do a search for WATER QUALITY CONSTITUENT VALUES 
    WQSV_mask = ldf.index[ldf['lines'] == 'WATER QUALITY CONSTITUENT VALUES']
    WQdf = ldf.copy()
    WQC = ['Stream']+WQC
    
    blanks = np.asarray(np.zeros(len(WQdf)),dtype = str)
    blanks[:] = ""
    
    for WQCe in WQC:
        WQdf[WQCe] = np.zeros(len(WQdf))
    
    WQdf['Stream'] = blanks
    
    StreamNames = []
    #Loop through each report and creat a WQ csv
    row = 0
    for i in WQSV_mask:
        
        #Grab the name of the stream
        StreamName = ldf['lines'][i-1].split(r':')[1].strip()
        #Remove any illegal characters and replace with underscores
        Illegal_chars = [r"/",r"*"]
        for Illegal_char in Illegal_chars:
            StreamName = '_'.join(StreamName.split(Illegal_char))
        
        print StreamName
        
        count = i+5
        while True:        
            templine = ldf['lines'][count]        
            values = templine.split()
            values = [StreamName]+values
            if len(values)==len(WQC):
                #f.write(StreamName+','+','.join(values)+'\n')                
                for j in range(len(WQC)):
                    WQdf[WQC[j]][row] = values[j]
                row = row + 1
                count = count + 1
            else:
                break
            
        #f.close()
        StreamNames.append(StreamName)
        
    #Parse the reaches
    #http://www.gossamer-threads.com/lists/python/python/93022
    startstring = '$$$ DATA TYPE 8 (REACH IDENTIFICATION DATA) $$$'
    #REACH_cols = ['CARD TYPE','REACH','ID','NAME','BEGIN REACH KM','END REACH KM','ELEM LENGTH KM','REACH LENGTH KM','ELEMS PER RCH','BEGIN ELEM NUM','END ELEM NUM']
    REACH_cols = ['CARD TYPE','REACH','ID','NAME','BEGIN REACH KM','END REACH KM','ELEM LENGTH KM','REACH LENGTH KM',
                  'ELEMS PER RCH','BEGIN ELEM NUM','END ELEM NUM','BEGIN NAME','END NAME']
    fws = [11,7,4,37,12,8,9,10,9,8,4]
    value_row_offset = 5
    
    endstring = 'ENDATA08'
    Rdf = parse_card_df(ldf,REACH_cols,fws,value_row_offset,startstring,endstring)

    #Parse the hydraulics
    startstring = '$$$ DATA TYPE 9 (ADVECTIVE HYDRAULIC COEFFICIENTS) $$$'    
    REACH_cols = ['CARD TYPE','REACH','ID','VELOCITY_A','VELOCITY_B','DEPTH_C','DEPTH_D','DEPTH_E','MANNINGS_N']
    fws = [15,7,4,15,15,15,15,15,17]    
    value_row_offset = 5
    
    endstring = 'ENDATA09'
    Hdf = parse_card_df(ldf,REACH_cols,fws,value_row_offset,startstring,endstring)

    #Parse the headwaters
    startstring = '$$$ DATA TYPE 21 (HEADWATER DATA FOR DO, BOD, AND NITROGEN) $$$'    
    REACH_cols = ['CARD TYPE','ELEMENT','NAME','DO','BOD','ORG-N','NH3','NO3+2']
    fws = [14,10,25,7,10,10,10,10]
    value_row_offset = 4    
    endstring = 'ENDATA21'
    Hdf = parse_card_df(ldf,REACH_cols,fws,value_row_offset,startstring,endstring)

    AllWQdf = WQdf[WQdf['Stream']!=""].reset_index()
    AllWQdf = AllWQdf[WQC]
    return StreamNames, Rdf, Hdf, AllWQdf

def Plot_QUALTX(StreamNames, Rdf, Hdf, AllWQdf,outputfolder,QUALTXoutfile,Scenario,DOstds = [],WQC_of_interest = ['DO_MG/L','BOD_MG/L','NH3_MG/L','NO3+2_MG/L','PHOS_MG/L'],loc = 1):
    import ET_Utils.Plot_Utils
    figs = []
    for StreamName in StreamNames:
        
        #Start Plotting
        WQdf = AllWQdf[AllWQdf['Stream']==StreamName].copy()
        SRdf = Rdf[Rdf['StreamName']==StreamName].reset_index()
        
        outputpdf = os.path.join(outputfolder, StreamName+'.pdf')
        pageorientation = 'landscape'
        fig, pp, axisartist = ET_Utils.Plot_Utils.setup_page(outputpdf, pageorientation)
        numrows = 1
        numcols = 1
        subplot_counter = 1
        ax = fig.add_subplot(axisartist.Subplot(fig, numrows,numcols,subplot_counter))        
        #x_range = [max(WQdf['ENDING_DIST']),min(WQdf['ENDING_DIST'])]
        x_range = [min(WQdf['ENDING_DIST']),max(WQdf['ENDING_DIST'])]
        #y_range = [0,25]
        y_label = 'mg/L'
        x_label = 'km'
        
        ls = []
        
        maxy = []
        for tempWQC in WQC_of_interest:
            maxy.append(max(WQdf[tempWQC]))
        y_range = [0,max(maxy)]
      
        x_labelsize = 15
        y_labelsize = 15
        ET_Utils.Plot_Utils.setup_axes(ax, x_range, y_range, x_label, y_label,x_labelsize = x_labelsize,y_labelsize = y_labelsize)#, x_tickinterval = x_tickinterval, y_tickinterval = y_tickinterval)
        ax.axis["bottom"].label.set_pad(6)  #specifies number of points between axis title and axis
        ax.invert_xaxis()
        #matplotlib.rcParams.update({'font.size': 22})
        
        lws = np.zeros(len(WQC_of_interest))+2
        plot_colors = ['blue','black','green','cyan','orange']
        plot_symbols = ['-','-','-','-','-']
        markersizes = np.zeros(len(WQC_of_interest))+1
        
        for k in range(0,len(WQC_of_interest)):        
            ls.append(ax.plot(np.asarray(WQdf['ENDING_DIST']),np.asarray(WQdf[WQC_of_interest[k]]),plot_symbols[k], lw = lws[k],markersize=markersizes[k],
                              color = plot_colors[k],label = WQC_of_interest[k]))
                
        #Show grid
        #ax.grid(True,linestyle='-',color='0.4', zorder=1)
        
        #Overplot reach start and end points of each reach
        if len(SRdf) > 0:
            Points1 = list(SRdf['BEGIN NAME'])
            Rkms1 = list(SRdf['BEGIN REACH KM'])
            if len(SRdf) > 1:
                Points2 = [SRdf['END NAME'][SRdf.index[-1]]]
                Rkms2 = [SRdf['END REACH KM'][SRdf.index[-1]]]
            else:
                Points2 = list(SRdf['END NAME'])
                Rkms2 = list(SRdf['END REACH KM'])
                
            Points = Points1 + Points2
        
            #Rkms = Rkms1.append(Rkms2)
            Rkms = Rkms1+Rkms2
        
            for i in range(0,len(Points)):
                ax.plot([Rkms[i],Rkms[i]],y_range,'--',color = 'k')
                ax.text(Rkms[i],np.mean(y_range),Points[i],va = 'center',rotation = 'vertical')

        if len(DOstds) > 0:
            for DOstd in DOstds:
                ax.plot(x_range,[DOstd,DOstd],'--',color = 'k')
                ax.text(np.mean(x_range),DOstd,"DO std = "+"{:4.1f}".format(DOstd)+" mg/L")
        #Plot legend
        handles, labels = ax.get_legend_handles_labels()
        #legend at top right corner, loc = 1
        #legend at top left corner, loc = 2
        #legend at bottom left corner, loc = 3
        #legend at bottom right corner, loc = 4
        ax.legend(handles, labels, loc=loc)
        
        fig.text(0.1,0.05, "Water quality profiles for " +StreamName + '.',fontsize = 16)
        fig.text(0.1,0.02, QUALTXoutfile+' ('+Scenario+').',fontsize = 12)
        figs.append(fig)
        pp.savefig(fig)
        pp.close()            
        ET_Utils.Plot_Utils.make_png(outputpdf)
        #print "monkey"
    return figs
    
def Process_QUALTX(inputfolder,QUALTXoutfile,Scenario,DOstds = [],
                   WQC_of_interest = ['DO_MG/L','BOD_MG/L','NH3_MG/L','NO3+2_MG/L','PHOS_MG/L'],loc = 1,plot_pdf = 1):
    
    outputsubfolder = "_".join(QUALTXoutfile.split("."))+"_plots"
    outputfolder = os.path.join(inputfolder,outputsubfolder)
    
    if os.path.exists(outputfolder) == False:
        os.mkdir(outputfolder)    
    
    inputfile = os.path.join(inputfolder,QUALTXoutfile)
    
    StreamNames, Rdf, Hdf, AllWQdf = parse_QUALTXoutfile(outputfolder, inputfile)#,HYDRcsv,REACHcsv)
 
    #print Hdf.columns
    Hdfcols = list(Hdf.columns)
    Hdf = pd.merge(Hdf,Rdf,left_on = 'ELEMENT',right_on = 'BEGIN ELEM NUM', how = "inner", suffixes = ['','_right']).reset_index()
    Hdfcols.append('ID')
    Hdf = Hdf[Hdfcols]
    Rdfcols = list(Rdf.columns)
    Rdf = pd.merge(Rdf,Hdf,on = 'ID', how = "outer", suffixes = ['','_right']).reset_index()
    Rdf['StreamName'] = Rdf['NAME_right']
    Rdfcols.append('StreamName')
    Rdf = Rdf[Rdfcols]

    if plot_pdf == 1:
        Plot_QUALTX(StreamNames, Rdf, Hdf, AllWQdf,outputfolder,QUALTXoutfile,Scenario,DOstds = [],WQC_of_interest = ['DO_MG/L','BOD_MG/L','NH3_MG/L','NO3+2_MG/L','PHOS_MG/L'],loc = 1)
    
    return StreamNames, Rdf, Hdf, AllWQdf
