'''----------------------------------------------------------------------------------
 Module Name:         ncRes_Engine.reservoir
 Source Name:          C:/MyDocs/projects/eclipse_wkspc/ncReservoir/src/ncRes_Engine/reservoir.py
 Version:                  Python 2.6
 Author:                  Timothy Morrissey, (timothy.morrissey@unc.edu) (tmorriss)
 Date:                      Apr 28, 2010
 Required Argumuments:  
 Optional Arguments:    
 Description: 
 Documentation: 
----------------------------------------------------------------------------------'''
# #####################################
#       ------ Imports --------
# #####################################

# ######################################
#       ------ Classes --------
# ######################################
class Reservoir():
    '''Class definition for a reservoir object'''
    def __init__(self,resID,num,catchID,subID,subNm,damObj):
        self.id=resID
        self.num=num
        self.catchID=catchID
        self.subID=subID
        self.subNm=subNm
        
        self.floodZoneRast=None
        self.floodZoneVect=None
        self.volume=None
        self.surfArea=None
        self.surfVolRatio=None
        self.damObj=None
        
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
    from pprint import pprint as pp
    def debug(msg):
        pp(msg)
    start_main="Start main (%s)" % (__file__)
    end_main="End main (%s)" % (__file__)

    debug(start_main)
    #-- App Code start --#



    #-- App Code end --#
    debug(end_main)
