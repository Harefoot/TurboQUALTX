#ET 20160216
#A module to do manipulations of pandas dataframe that are not within the standard python package

import pandas as pd
import numpy as np

#Function for unpivot a dataframe (duplicate of WASP_Utils.unpivot - but we can remove the one in WASP_Utils later
#if we can figure out how to make modules within a package reference each other)
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