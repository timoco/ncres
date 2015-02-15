'''----------------------------------------------------------------------------------
 Module Name:         ncRes_spatApp.ncresSpatialApp
 Source Name:      /Users/TPM/MyDocs/dev/eclipse/workspace/ncResEngine/ncReservoir/src/ncRes_spatApp/ncresSpatialApp.py
 Version:           Python 2.6
 Author:            Timothy Morrissey, (timothy.morrissey@unc.edu)
 Date:                Apr 25, 2010
 Required Argumuments:  
 Optional Arguments:    
 Description: 
 Documentation: 
----------------------------------------------------------------------------------'''
# #####################################
#       ------ Imports --------
# #####################################
from pprint import pprint as pp
import os,sys,shelve,glob,csv
from datetime import datetime as tstamp
from ConfigParser import ConfigParser as configParser
import pGIS
import ncRes_DAX.ncresDAX as dax
import ncRes_log.ncRes_logger as ncResLog
import ncRes_email.ncRes_email as ncResEmail
import ncRes_Engine.subBasin    
import ncRes_Engine.subCatchment


# ######################################
#       ------ Classes --------
# ######################################
class ncresApp():
    '''creates a pGIS implementation for the NC Reservoir Spatial Analysis application'''
    def __init__(self):
        self.gisApp=pGIS.gisApp('ncres')
        self.dataSrc=self.gisApp.appDataSrc
        self.dax=dax.ncresDAX(self.dataSrc,self.gisApp.appTblDir)
        self.grassApp=self.gisApp.grassApp
        self.appRast=self.grassApp.gRaster()
        self.appVect=self.grassApp.gVector()
        
        #spatial app data
        self.zonalDataDir=self.gisApp.appZonalDir        
        
        #stats
        self.sub80HdrWritten=False
        
        
        
    def run(self):
        '''Run the ncResApp'''
        pass
        
    def getZonalData(self):
        '''Get zonal shape data'''
        shpList=glob.glob1(self.zonalDataDir, '*.shp')
        zonalDSList=[]
        for extShp in shpList:
            #check to see if already in DB
            grsShp=extShp.replace('.','_')
            if self.grassApp.dsExists(grsShp):
                zonalDSList.append(grsShp)
            else:
                shp=self.appVect.linkExternalShp(self.zonalDataDir, extShp)
                if shp is None:
                    pp('%s exists in DB' % (extShp))
                else:
                    zonalDSList.append(shp)
                
        return zonalDSList
    
        #Need spatial layers list
        
        #Need zone source from NCResEngine (subCatchment,reservoir,...)
        
        #Calc zonal stats of spatial layers by zone
    
    def getSub80Stats(self,sub80):
        '''Calc univar stats for each subBasin at 80'''
        self.appRast.setRegion(sub80)
        stats=self.appRast.rastStats(sub80)
        return stats
    
    def createSub80StatsCSV(self):
        '''create the CSV writer'''
        statsCSVFile=r'%s/sub80stats.csv' % (self.gisApp.appCsvDir)
        statsCSV=csv.writer(open(statsCSVFile,'wb'))
        return statsCSV
    def writeStatsHeader(self,csvFile,hdr):
        '''write the header row for the csv'''
        if not self.sub80HdrWritten:
            csvFile.writerow(hdr)
            self.sub80HdrWritten=True
        
    def writeToCSV(self,csvFile,row):
        '''write a row to a csvFile'''
        csvFile.writerow(row)
        
    def closeCSV(self,csvFile):
        csvFile.close()
        
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
       app=ncresApp()
#       subBasinDict=app.dax.subBasinsData
#       statsFile=app.createSub80StatsCSV()
#       for subID in subBasinDict:
#           subBasin=(subBasinDict[subID])[2]
#           subBasinStats=app.getSub80Stats(subBasin)
#           if not app.sub80HdrWritten:
#               subStatsHdr=[]
#               subStatsHdr.append('subBasinNm')
#           
#           subStatsRow=[]
#           subStatsRow.append(subBasin)
#           for key in subBasinStats:
#               if not app.sub80HdrWritten:
#                   subStatsHdr.append(key)
#               subStatsRow.append(subBasinStats[key])
#           
#           if not app.sub80HdrWritten:
#               app.writeStatsHeader(statsFile, subStatsHdr)
#           app.writeToCSV(statsFile, subStatsRow)
           
       zonalDir=app.zonalDataDir
       grassVects=app.getZonalData()
       rast='upperneuse'
       for vect in grassVects:
           if vect=='urbnarea_shp':
               app.appVect.calcZonalStats(vect, rast)
       #-- App Code end --#
       debug(end_main)
