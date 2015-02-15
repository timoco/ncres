'''----------------------------------------------------------------------------------
 Module Name:         ncRes_Engine.subCatchment
 Source Name:         C:/MyDocs/projects/eclipse_wkspc/ncReservoir/src/ncRes_Engine/subCatchment.py
 Version:             Python 2.6
 Author:              Timothy Morrissey, (timothy.morrissey@unc.edu) (tmorriss)
 Date:                Apr 8, 2010
 Required Argumuments:  
 Optional Arguments:    
 Description: 
 Documentation: 
----------------------------------------------------------------------------------'''
# #####################################
#       ------ Imports --------
# #####################################
#import pGIS
import os
from pprint import pprint as pp


# ######################################
#       ------ Classes --------
# ######################################
class Catchment():
    '''Class for a subBasin catchment object'''
    def __init__(self,catchID,subID,subNm,name):
        self.id=catchID
        self.subID=subID
        self.subNm=subNm
        self.name=name
        self.rastObj=name.replace('_','.')
        self.vectObj=name
        self.surfArea='na'
        self.drain='%s.drain' % (name)
        self.stream='%s_stream' % (name)
        self.damLocs='%s_dams' % (self.stream)
        self.damCoords='na'
        self.damObjects=None
        self.resObjects=None
        self.mask='%s.mask' % (self.rastObj)
        
        
# #####################################
#       ------ Functions --------
# #####################################

# ######################################
#       ------ Main --------
# ######################################


# ######################################
#       ------ Unit Testing --------
# ######################################
if __name__=='__main__':
       def debug(msg):
              print msg

       start_main="Start main (%s)" % (__file__)
       end_main="End main (%s)" % (__file__)

       debug(start_main)
       #-- App Code start --#

       #-- App Code end --#
       debug(end_main)
