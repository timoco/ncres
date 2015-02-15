'''----------------------------------------------------------------------------------
 Module Name:         ncRes_log.ncRes_logger
 Source Name:         C:/MyDocs/projects/eclipse_wkspc/ncReservoir/src/ncRes_log/ncRes_logger.py
 Version:             Python 2.6
 Author:              Timothy Morrissey, (timothy.morrissey@unc.edu) (tmorriss)
 Date:                Apr 13, 2010
 Required Argumuments:  
 Optional Arguments:    
 Description:         Logging class for NC Reservoir app
 Documentation: 
----------------------------------------------------------------------------------'''
# #####################################
#       ------ Imports --------
# #####################################
import logging,sys,os,ConfigParser

# ######################################
#       ------ Classes --------
# ######################################
class appLog():
    '''Log class for application logging'''
    def __init__(self,app='ncResEngine'):
        '''initialization'''
        logDir=os.path.dirname(__file__)
        if app=='ncResEngine':
            ncResLogFile='%s/ncResEngine.log' %(logDir)
        
        logging.basicConfig(level=logging.DEBUG,
                            filename=ncResLogFile,
                            format='%(asctime)s %(name)-12s %(levelname)-8s : %(module)s %(funcName)s :: %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filemode='a')
        #Root log
        logging.info('----------------------------')
        logging.info('-------NC Res Log---------')

        self.log=logging.getLogger(app)
        
        self.log.info('--------------------------------')
        self.log.info('------ %s LOG started -------' % (app))
        
                            
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

    engineLog=appLog()

    #-- App Code end --#
    debug(end_main)
