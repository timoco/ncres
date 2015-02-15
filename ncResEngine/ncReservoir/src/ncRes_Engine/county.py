'''----------------------------------------------------------------------------------
 Module Name:         ncRes_Engine.county
 Source Name:         C:/MyDocs/projects/eclipse_wkspc/ncReservoir/src/ncRes_Engine/county.py
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
class county():
    '''Class for a county object'''
    def __init__(self,cntyID):
        self.id=cntyID
        self.name='getfromcsv_tbl'
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
