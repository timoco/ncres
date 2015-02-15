'''----------------------------------------------------------------------------------
 Module Name:         ncRes_Engine.sub80
 Source Name:         C:/MyDocs/projects/eclipse_wkspc/ncReservoir/src/ncRes_Engine/sub80.py
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
import pGIS

# ######################################
#       ------ Classes --------
# ######################################
class subBasin():
    '''Class for a subBasin object'''
    def __init__(self,subBasinData):
#    def __init__(self,subID,subNm,subCntyList):
        self.id=subBasinData[0]
        self.name=subBasinData[1]
        self.countyList='na'
        self.dem80=subBasinData[2]
        self.dem20=subBasinData[3]
        self.surfArea='na'
        self.subCatchIDList='na'
        self.subCatchments='%s.catchments' % (self.name.lower())
        self.subCatchmentsVect='%s_catchments' % (self.name.lower())
        self.subCatchmentsVectList='na'
        self.subCatchObjects='na'
    
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
