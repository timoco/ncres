'''----------------------------------------------------------------------------------
 Module Name:         ncRes_email.ncRes_email
 Source Name:          C:/MyDocs/projects/eclipse_wkspc/ncReservoir/src/ncRes_email/ncRes_email.py
 Version:                  Python 2.6
 Author:                  Timothy Morrissey, (timothy.morrissey@unc.edu) (tmorriss)
 Date:                      Apr 13, 2010
 Required Argumuments:  
 Optional Arguments:    
 Description: 
 Documentation: 
----------------------------------------------------------------------------------'''
# #####################################
#       ------ Imports --------
# #####################################
import sys,smtplib
# ######################################
#       ------ Classes --------
# ######################################
class ncResEmail():
    '''Creates an object for sending emails associated with the NC Reservoir Project'''
    def __init__(self,emailApp):
        self.__server=emailApp['server']
        self.__port=emailApp['port']
        self.__addrTo=emailApp['addr_to']
        self.__addrFrom=emailApp['addr_from']
        
        
    def sendEmail(self,msg,subj=''):
        '''Public function to format email with the NC Reservoir parameters
        INPUT: msg (email body)
               subj (optional subject/ default='NC Reservoir Project:' )'''
        subject='NC Reservoir Project: %s' % (subj)
        headers='From: %s\r\nTo: %s\r\nSubject: %s\r\n' % (self.__addrFrom,self.__addrTo,subject)
        body='**The following email is generated from the NC Reservoir Application**\n\n %s' % (msg)
        emailMsg=headers + body
        self.__send(emailMsg)
        
    def __send(self,emailMsg):
        '''Private function to send the formatted email'''
        smtpConn=smtplib.SMTP(self.__server,self.__port)
        smtpConn.sendmail(self.__addrFrom,self.__addrTo,emailMsg)
        smtpConn.quit()
       
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
    emailApp={}
    emailApp['server']='smtp.unc.edu'
    emailApp['port']='587'
    emailApp['addr_to']='timothy.morrissey@unc.edu'
    emailApp['addr_from']='ncreservoir@unc.edu'
    appEmail=ncResEmail(emailApp)

    appEmail.sendEmail('TEST NC RESERVOIR ENGINE BODY', 'TEST ENGINE')

    #-- App Code end --#
    debug(end_main)
