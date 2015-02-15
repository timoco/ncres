'''----------------------------------------------------------------------------------
 Module Name:         ncRes_Engine.dam
 Source Name:          C:/MyDocs/projects/eclipse_wkspc/ncReservoir/src/ncRes_Engine/dam.py
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
class Dam():
    '''Class for a dam object'''
    def __init__(self,id,num,catchId,subID,name,damX,damY,damZ):
        self.id=id
        self.num=num
        self.catchID=catchId
        self.subID=subID
        self.name=name
        self.x=damX
        self.y=damY
        self.z=damZ
        self.height=None
        self.basin=None
        self.reservoir=None
        
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

    dam=Dam(1,2,3)
    pp(dam.id)
    pp(dam.x)
    pp(dam.y)

    #-- App Code end --#
    debug(end_main)
