'''----------------------------------------------------------------------------------
 Module Name:         ncRes_Engine.ncresDAX
 Source Name:         C:/MyDocs/projects/eclipse_wkspc/ncReservoir/src/ncRes_Engine/ncresDAX.py
 Version:             Python 2.6
 Author:              Timothy Morrissey, (timothy.morrissey@unc.edu) (tmorriss)
 Date:                Apr 8, 2010
 Required Argumuments:  
 Optional Arguments:    
 Description:         Data access class for the NC Reservoir project
 Documentation: 
----------------------------------------------------------------------------------'''
# #####################################
#       ------ Imports --------
# #####################################
import pGIS
import csv
import shelve
import cPickle
# ######################################
#       ------ Classes --------
# ######################################
class ncresDAX():
    '''Class for the ncres data access object'''
    def __init__(self,dataSrc,dataDir=''):
        self.dataSrc=dataSrc
        if self.dataSrc == 'csv':
            self.dataDir=dataDir
            self.dataTbls=self.__getDataTbls()
        else:
            ##establish db connection
            self.dataTbls='NA'
        
        #Object data persistence
        self.subBasinObjFile='%s/subObjs.data' % (self.dataDir)
        self.catchObjFile='%s/catchObjs.data' % (self.dataDir)
        self.damObjFile='%s/damObjs.data' % (self.dataDir)
        self.resObjFile='%s/reservoirObjs.data' % (self.dataDir)
        
        
        #Table structs
        self.subBasinTbl=self.__subBasinTbl()
#        self.updateSubBasinTbl=self.__updateSubBasinTbl()
#        self.updateTempTbl=self.__updateTbl_temp()
        self.subBasinTblDef=self.__subBasinTblDef(self.subBasinTbl)
        self.subBasinTblID_idx=self.subBasinTblDef.index('ID')
        self.subBasinTblName_idx=self.subBasinTblDef.index('NAME')
        self.subBasinTblDEM80_idx=self.subBasinTblDef.index('DEM80')
        self.subBasinTblDEM20_idx=self.subBasinTblDef.index('DEM20')
        self.subBasinTblAREA80_idx=self.subBasinTblDef.index('AREA80')
        self.subCountyTbl=self.__subBasinCountyTbl()
        self.subBasinCountyTblDef=self.__subBasinCountyTblDef(self.subCountyTbl)
        self.countyTblID_idx=self.subBasinCountyTblDef.index('ID')
        self.countyTblSubID_idx=self.subBasinCountyTblDef.index('SUB_ID')
        self.countyTblSubNm_idx=self.subBasinCountyTblDef.index('SUB_NM')
        self.countyTblCntyID_idx=self.subBasinCountyTblDef.index('CNTY_ID')
        self.countyTblCntyNm_idx=self.subBasinCountyTblDef.index('CNTY_NM')
        
        
        self.subBasinsData=self.__getSubBasinsData()
        self.cntyData=self.__getCountyData()
        self.subCntyData=self.__getSubCountyData()
        
        #Spatial Objects
#        self.subDem80=

    def __subBasinTbl(self):
        '''Private function for returning the sub Basin data table (csv)'''
        subBasinTbl='%s/%s' % (self.dataDir,self.dataTbls[self.dataTbls.index('subBasin_tbl.csv')])
        subReader=csv.reader(open(subBasinTbl,'rb'))
        return subReader
#    def __updateSubBasinTbl(self):
#        '''Private function for returning the sub Basin data table (csv)'''
##        subBasinTbl=file('%s/%s' % (self.dataDir,self.dataTbls[self.dataTbls.index('subBasin_tbl.csv')]),'ab')
##        subWriter=csv.DictWriter(subBasinTbl,self.subBasinTblDef)
#        subBasinTbl='%s/%s' % (self.dataDir,self.dataTbls[self.dataTbls.index('subBasin_tbl.csv')])
#        subWriter=csv.writer(subBasinTbl,'ab')
#        return subWriter
#    def __updateTbl_temp(self):
#        '''Private function for returning the sub Basin data table (csv)'''
#        tempTbl='%s/temptbl.csv' % (self.dataDir)
#        subWriter=csv.writer(open(tempTbl,'wb'))
#        return subWriter
        
    def __subBasinTblDef(self,subBasinTbl):
        '''Private function for returning the sub Basin data table elements (csv)'''
        subBasinTblDef=subBasinTbl.next()
        return subBasinTblDef
    
    def __subBasinCountyTbl(self):
        '''Private function for returning the subBasinCounty data table (csv)'''
        subCntyTbl='%s/%s' % (self.dataDir,self.dataTbls[self.dataTbls.index('subBasinCounty_tbl.csv')])
        subCntyReader=csv.reader(open(subCntyTbl,'rb'))
        return subCntyReader
        
    def __subBasinCountyTblDef(self,subBasinCntyTbl):
        '''Private function for returning the subBasinCounty data table elements (csv)'''
        subBasinCntyTblDef=subBasinCntyTbl.next()
        return subBasinCntyTblDef
        
    def __getSubBasinsData(self):
        '''Private function for returning the sub Basin data elements'''
        subReader=self.subBasinTbl
        subBasinDataDict={}
        for subRow in subReader:
            subBasinRow=[]
            for elem in range(0, len(subRow)):
                subBasinRow.append(subRow[elem])
            subBasinKey=subRow[0]
            subBasinDataDict[subBasinKey]=subBasinRow

        return subBasinDataDict
    
    def __getCountyData(self):
        '''Private function for returning the county data elements'''
        countyTbl='%s/%s' % (self.dataDir,self.dataTbls[self.dataTbls.index('county_tbl.csv')])
        cntyReader=csv.reader(open(countyTbl,'rb'))
        hdrRow=cntyReader.next()
        cntyDict={}
        for cntyRow in cntyReader:
            cntyKey=cntyRow[0]
            cntyData=cntyRow[1]
            cntyDict[cntyKey]=cntyData
        return cntyDict
    
    def __getSubCountyData(self):
        '''Private function for returning the county data elements'''
        subCntyTbl='%s/%s' % (self.dataDir,self.dataTbls[self.dataTbls.index('subBasinCounty_tbl.csv')])
        subCntyReader=csv.reader(open(subCntyTbl,'rb'))
        hdrRow=subCntyReader.next()
        subCntyDict={}
        for subCntyRow in subCntyReader:
            subCntyKey=subCntyRow[0]
            subCntyData='%s,%s,%s,%s' % (subCntyRow[1],subCntyRow[2],subCntyRow[3],subCntyRow[4])
            subCntyDict[subCntyKey]=subCntyData
        return subCntyDict
   
    def __getDataTbls(self):
        '''Private function for returning the data elements in the dataDir'''
        import glob 
        dataTblList=glob.glob1(self.dataDir, '*.csv')
        return dataTblList
    
    #Public functions
    def getSubBasinData(self,subID):
        '''Function to return row of subBasin data by subID
        INPUT: subID (int)
        OUTPUT: subBasinDataList(list)'''
        subBasinDataList=self.subBasinsData[subID]
        return subBasinDataList
    def getSubBasinName(self,subID):
        '''Function to return name data element of subBasin data by subID
        INPUT: subID (int)
        OUTPUT: subName(string)'''
        subName=(self.subBasinsData[subID])[self.subBasinTblName_idx]
        return subName
    def getSubBasinDEM80(self,subID):
        '''Function to return dem80 data element of subBasin data by subID
        INPUT: subID (int)
        OUTPUT: subDEM80(string)'''
        subDEM80=(self.subBasinsData[subID])[self.subBasinTblDEM80_idx]
        return subDEM80
    def getSubBasinDEM20(self,subID):
        '''Function to return dem20 data element of subBasin data by subID
        INPUT: subID (int)
        OUTPUT: subDEM20(string)'''
        subDEM20=(self.subBasinsData[subID])[self.subBasinTblDEM20_idx]
        return subDEM20
        
    def getSubCounties(self,subID):
        '''Function to return a list of counties for each subBasin
        INPUT: subID (int)
        OUTPUT: countyList(list)'''
        countyList=[]
        for i in self.subCntyData.keys():
            if subID in self.subCntyData[i]:
                subCntyData=(self.subCntyData[i]).split(',')
                countyList.append(subCntyData[3])
        return countyList
    def writeSubToCSV(self):
        pass
#        
    
#    def setSubBasinSurfArea(self,subID,surfArea):
#        '''Function to set the AREA80 data element of subBasin data by subID
#        INPUT: subID (int)
#               surfArea (int)
#        OUTPUT: subDEM20(string)'''
##        subBasinData=self.subBasinTbl
##        subBasinData.next()
#        subBasinTbl='%s/%s' % (self.dataDir,self.dataTbls[self.dataTbls.index('subBasin_tbl.csv')])
##        subBasinData=csv.reader(open(subBasinTbl,'rb'))
#        subBasinData=csv.DictReader(open(subBasinTbl,'rb'))
#        subBasinUpdateTbl=self.updateSubBasinTbl
#        for row in subBasinData:
#            if row[0]==subID:
#                pp(row)
#                row[self.subBasinTblAREA80_idx]=surfArea
#                subBasinUpdateTbl.writerow(row)
#                pp(row)
                
        
#        subDEM20=(self.subBasinsData[subID])[self.subBasinTblDEM20_idx]
#        return subDEM20
#    
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
    testDataDir=r'C:/MyDocs/projects/nc_res/gis_data/csv/tbl'
    dax=ncresDAX('csv',testDataDir)
#    pp(dax.dataTbls)
#    pp(dax.subBasinData)
#    pp(dax.subCntyData)
#    for subID in dax.subBasinData.keys():
    subID='3020201'
    cntyList=dax.getSubCounties(subID)
#    pp(cntyList)    
#    pp(dax.getSubBasinData(subID))
#    pp(dax.getSubBasinDEM20(subID))
#    pp(dax.getSubBasinDEM80(subID))
#    pp(dax.getSubCounties(subID))
#    surfArea=12345
#    dax.writeObjectToCSV()
#    dax.setSubBasinSurfArea(subID, surfArea)
    dax.getObject(dax.subBasinObjFile, subID)
    #-- App Code end --#
    debug(end_main)
