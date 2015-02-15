'''----------------------------------------------------------------------------------
 Module Name:          ncres_app
 Source Name:          /Users/TPM/MyDocs/dev/eclipse/workspace/ncres_pydev/src/ncres_app.py
 Version:              Python 2.6
 Author:               Timothy Morrissey, (timothy.morrissey@unc.edu)
 Date:                 Mar 15, 2010
 Required Argumuments:  
 Optional Arguments:    
 Description:         Launches the NC Reservoir GIS application
 Documentation: 
----------------------------------------------------------------------------------'''
# #####################################
#       ------ Imports --------
# #####################################
from pprint import pprint as pp
import csv
import pGIS
#import import_procs
import os
#from hydro import hydro_procs as ncresHydro
#from projEmail import ncresEmail
#from pGIS import gisApp

#from inGrass import import_procs as 
# ######################################
#       ------ Classes --------
# ######################################
class ncresApp():
    '''Creates ncresApp pGIS implementation.'''
    def __init__(self):
        self.__gisApp=pGIS.gisApp('ncres')
#        pGIS.gisApp.__init__(self, 'ncres')
        #all attributes and methods from pGIS
        self.__subCntys=self.__setAllCountiesBySubsDict()
        
    def __setAllCountiesBySubsDict(self):
        '''retrieve a dictionary of counties (value) by subbasin (key) '''
        subCSV=r'%s/bsnCounties.csv' % (self.__gisApp.appCsvDir)
        subRdr=csv.reader(open(subCSV,'rb'))
        hdrRw=subRdr.next()
        subCntyDict={}
        for subRw in subRdr:
            sub=(subRw[1]).lower()
            cnty=(subRw[3]).lower()
            if sub in subCntyDict:
                subCntyDict[sub]='%s,%s' % (subCntyDict[sub],cnty)
            else:
                subCntyDict[sub]=cnty
        
        return subCntyDict

    @property
    def getNCResApp(self):
        '''return the NC Res pGIS application'''
        return self.__gisApp
    @property
    def getSubCntys(self):
        '''return the counties by sub dictionary'''
        return self.__subCntys
    
def main():
    '''main for the NC Reservoir pGIS application'''
#    gisDir= ncres.appGisDir
#    curMapset=grs.getCurMapset()
    rstList=grs.grassPermRastList
    subList=getSubs()
    grs.setCurMapset('subs')
    
    if upperNeuse:                                              ##DEBUG
        subRst='upperneuse'                                     ##DEBUG
        pp(subRst)      
        if createSub20ft:                                        ##DEBUG
            #Build the sub20
            sub20Rst=createSub20(subRst)
        else:
            sub20Rst='%s.cnty20' % (subRst)   
        pp(sub20Rst)                                            ##DEBUG
        pp(grs.grassCurMapsetRastList)                          ##DEBUG
        grs.setRegion(subRst)                                               ##REGION
        gRast.setMask(subRst)                                               ##MASK
        threshDict=getWShedThresh(subRst)
        subWshedDict=calcWatershed(subRst,threshDict)
        pp(subWshedDict)                                        ##DEBUG
        processSub(subWshedDict)                                ##DEBUG
        #START FROM pGRASS
        vAttStr=gVect.vectSelect(subRst)
        vAttL=vAttStr.split('\n')
        for vObj in vAttL:
            if len(vObj)>0:
                vCat=int(((vObj).split(','))[0])
                vArea=round(float(((vObj).split(','))[3]))
                if vArea in range(50,150):                       ##DEBUG
#                    if vCat == 383:                             ##DEBUG
                    pp(vCat)                                ##DEBUG
                    pp(vArea)                               ##DEBUG
                    vectObj=gVect.vectExtractEach(subRst, vCat,True)
                    pp(vectObj)                             ##DEBUG
                    #must set region before conversion
                    grs.setRegion(vectObj,'vect')               ##REGION
                    rObj=gVect.convVtoR(vectObj, 'area_sqmi',True)
                    pp(rObj)                                ##DEBUG
                    #set the mask to rObj
                    gRast.setMask(rObj)                                 ##MASK
                    pp(gRast.getMask())                                 ##DEBUG
                    #run the watershed for the sub20 with mask
                    #sub20WShedDict=gRast.calcWatershed(sub20Rst, '696960', '10',str(vCat),True)
                    sub20ThreshDict=getWShedThresh(sub20Rst)
#                        calcWatershed(inRast,inThreshDict,id=''):  
                    sub20WShedDict=calcWatershed(sub20Rst, sub20ThreshDict,str(vCat)) #calcWatershed(sub20Rst, '696960', '10',str(vCat),True)
                    #subWshedDict=calcWatershed(subRst,threshDict,'basin',overWrite)
                    pp(sub20WShedDict)                      ##DEBUG
                    #convert Streams to vect
                    sub20Strms=gRast.convRtoV(sub20WShedDict['stream'], 'line',True)
                    pp(sub20Strms)                          ##DEBUG
    
                    damLocDict=createDamLoc(sub20Strms)
                    #moved to createDamLoc
                    ##
#                        vStrmReport=gVect.vectReport(sub20Strms, 'length', 'feet')
#                        vStrmReport=vStrmReport.replace('\n',';')
#                        pp(vStrmReport)                         ##DEBUG
#                        vStrmReportL=((vStrmReport.split(';'))[1]).split('|')
#                        pp(vStrmReportL)                        ##DEBUG
#                        vStrmCat=vStrmReportL[0]
#                        vStrmLen=round(float((vStrmReportL[2])))
#                        pp(vStrmCat)                            ##DEBUG
#                        pp(vStrmLen)                            ##DEBUG
#                        segCnt=1
#                        segIn=''
#                        appCSVDir='C:/MyDocs/projects/nc_res/gis_data/csv' ## WILL be from pGIS
#                        segRuleFile='%s/seg.txt' % (appCSVDir) 
#                        segFile=open(segRuleFile,'wb')
#                        for vSegVal in range(1,vStrmLen,5280):
#                            segId=segCnt
#                            pp(segId)                           ##DEBUG
#                            pp(vSegVal)                         ##DEBUG
#                            segIn='P %d %s %d \n' % (segId,vStrmCat,vSegVal)
#                            segFile.write(segIn)
#                            segCnt=segCnt+1
#                        segFile.close()
#                        pp(segIn)                               ##DEBUG
#                        vSegObj=gVect.segmentLine(sub20Strms, segRuleFile, True)
#                        
##                        def getSegmentCoords(self,inSeg):
##                        vSegObj=inSeg
#                        
#                        vReport=gVect.vectReport(vSegObj, 'coor')
#                        pp(vReport)                             ##DEBUG
#                        vReportL=vReport.split('\n')
#                        vSegDict={}
#                        for vSeg in vReportL:
#                            if ((not vSeg.startswith('cat')) and (len(vSeg)>0)):
#                                vSegL=vSeg.split('|')
#                                vSegCat=vSegL[0]
#                                vSegX=vSegL[1]
#                                vSegY=vSegL[2]
#                                vSegXY='%s,%s' % (vSegX,vSegY)
#                                vSegDict[vSegCat]=vSegXY
#                        
#                        pp(vSegDict)                        ##DEBUG
#                        pp(grassGisApp.setRegion('upperneuse.383.basin10'))     ##REGION-> HCODE
                    pp(grs.getRegion)           ##DEBUG
#                        gRast.setMask('upperneuse.383.basin10')                 ##MASK -> HCODE
                    pp(gRast.getMask())                 ##DEBUG

                    damLocZDict=getDamZ(damLocDict, sub20Rst)
                    #moved to getDamZ
                    ##
#                        damLocZDict={}
#                        for pnt in vSegDict.keys():
#                            pp(vSegDict[pnt])               ##DEBUG  
##                            zVal=gRast.queryRaster('upperneuse.cnty20', vSegDict[pnt])      ##HCODE
#                            zVal=gRast.queryRaster(sub20Rst, vSegDict[pnt])
#                            damLocZDict[pnt]=zVal
#                            
#                        pp(damLocZDict)                     ##DEBUG
#                        

                    createReservoir(sub20Rst, damLocDict)
                    #moved to createReservoir
                    ##
                    #not sure if water level is relative or absolut, ie elev + waterlvl or waterlvl    ##DEBUG
#                        rLake=gRast.fillLake('upperneuse.cnty20', 100, vSegDict['1'],True)            ##HCODE      ##DEBUG
#                        rLake=gRast.fillLake(sub20Rst, 100, vSegDict['1'],True)            ##HCODE 
#                        pp(rLake)                                                                           ##DEBUG
        #END FROM pGRASS
        
#        if calcWshed:               ##DEBUG
#            grs.setRegion(subRst)
#            gRast.setMask(subRst)
#            threshDict=getWShedThresh(subRst)
#            subWshedDict=calcWatershed(subRst,threshDict,'basin',overWrite)
#            pp(subWshedDict)
#        else:   ##DEBUG
#            subWshedDict={}
#            subWshedDict['elev']=subRst
#            subWshedDict['drain']='%s.drain25' % (subRst)
#            subWshedDict['basin']='%s.basin25' %(subRst)
#            subWshedDict['stream']='%s.strms25' % (subRst)
#            subWshedDict['flAccum']='%s.accum25' % (subRst)
#            subWshedDict['thres']='108900'
        
#        processSub(subWshedDict)
    else:
        for subRst in rstList:
            if not (('.' in subRst) or (subRst=='MASK')): 
                pp(subRst)
                processSub(subRst)
    gRast.delMask()

def getDamZ(inDamLocDict,inRast):
    '''Helper function to retrieve Z vals at dam location coord
    INPUT: dictionary (dam location points (cat:coord)
           raster (raster to be queried)
    OUTPUT: dictionary (key=seq of point cat (1..n), value=z val)
    '''
    vSegDict=inDamLocDict
    sub20Rst=inRast
    damLocZDict={}
    for pnt in vSegDict.keys():
        pp(vSegDict[pnt])               ##DEBUG  
#                            zVal=gRast.queryRaster('upperneuse.cnty20', vSegDict[pnt])      ##HCODE
        zVal=gRast.queryRaster(sub20Rst, vSegDict[pnt])
        damLocZDict[pnt]=zVal
    pp(damLocZDict) 
    return damLocZDict    
    
def createDamLoc(inStrmsV):
    '''Helper function to locate points along stream for dam location
    INPUT: vector (20ft streams)
    OUTPUT: dictionary (key=seq of point cat (1..n), value=XY coord)
    '''
    sub20Strms=inStrmsV
    vStrmReport=gVect.vectReport(sub20Strms, 'length', 'feet')
    vStrmReport=vStrmReport.replace('\n',';')
    pp(vStrmReport)                         ##DEBUG
    vStrmReportL=((vStrmReport.split(';'))[1]).split('|')
    pp(vStrmReportL)                        ##DEBUG
    vStrmCat=vStrmReportL[0]
    vStrmLen=round(float((vStrmReportL[2])))
    pp(vStrmCat)                            ##DEBUG
    pp(vStrmLen)                            ##DEBUG
    segCnt=1
    segIn=''
    appCSVDir='C:/MyDocs/projects/nc_res/gis_data/csv' ## WILL be from pGIS
    segRuleFile='%s/seg.txt' % (appCSVDir) 
    segFile=open(segRuleFile,'wb')
    for vSegVal in range(1,vStrmLen,5280):
        segId=segCnt
        pp(segId)                           ##DEBUG
        pp(vSegVal)                         ##DEBUG
        segIn='P %d %s %d \n' % (segId,vStrmCat,vSegVal)
        segFile.write(segIn)
        segCnt=segCnt+1
    segFile.close()
    pp(segIn)                               ##DEBUG
    vSegObj=gVect.segmentLine(sub20Strms, segRuleFile, True)
    vReport=gVect.vectReport(vSegObj, 'coor')
    pp(vReport)                             ##DEBUG
    vReportL=vReport.split('\n')
    vSegDict={}
    for vSeg in vReportL:
        if ((not vSeg.startswith('cat')) and (len(vSeg)>0)):
            vSegL=vSeg.split('|')
            vSegCat=vSegL[0]
            vSegX=vSegL[1]
            vSegY=vSegL[2]
            vSegXY='%s,%s' % (vSegX,vSegY)
            vSegDict[vSegCat]=vSegXY
    
    pp(vSegDict)                        ##DEBUG
#                        pp(grs.setRegion('upperneuse.383.basin10'))     ##REGION-> HCODE
    pp(grs.getRegion)           ##DEBUG
#                        gRast.setMask('upperneuse.383.basin10')                 ##MASK -> HCODE
    pp(gRast.getMask()) 
    
    return vSegDict

def createReservoir(in20Rst,inDamLocDict):
    '''Helper function to create a reservoir with r.lake
    INPUT: raster (sub basin 20ft)
           dictionary (stream segment points
    '''
#    rLake=gRast.fillLake(sub20Rst, 100, vSegDict['1'],True)
    #not sure if water level is relative or absolut, ie elev + waterlvl or waterlvl    ##DEBUG
    for loc in inDamLocDict.keys():
        damCoord=inDamLocDict[loc]
        rLake=gRast.fillLake(in20Rst, 100, damCoord,True)
        #need to check the rLake volume to see if need to recalc
        
    
def createSub20(inSub):
    '''Create a mosaic'd raster of all 20ft county DEMs in the input sub.
    INPUT: raster (inSub)
    OUTPUT: raster (sub20)
    '''
    cntyList=getCountiesBySub(inSub)
    sub20Nm='%s.cnty20' % (inSub)
    cntyStr=','.join(cntyList)
    #Must set the g.region to 20ft
    grs.setRegion(cntyStr)                                      ##REGION
    mosaicSub20=gRast.mosaicRasters(cntyList,sub20Nm,overWrite)
    return mosaicSub20    
        
def processSub(inWShedDict):
    ''' Helper function to parse Watershed dictionary
    INPUT: raster (sub basin)
    '''
    subWshedDict=inWShedDict
    bsnV=gRast.convRtoV(subWshedDict['basin'],'area',True)
    gVect.addDBCol(bsnV,'area_sqmi','DOUBLE PRECISION')
    gVect.addDBVal(bsnV,'area','area_sqmi','mi')
#    if convRtoV:    ##DEBUG
#        ##CONVERT RST to vector for STREAMs & Basin
#        bsnV=gRast.convRtoV(subWshedDict['basin'])
##        strmV=gRast.convRtoV(subWshedDict['stream'],'line')
##    else:   ##DEBUG
##        bsnV='%s_basin25' %(subRst)
##        strmV='%s_strms25' %(subRst)
#        
#    if addVectDB:
#        #add area to the catchment vector
#        gVect.addDBCol(bsnV,'area_sqmi','DOUBLE PRECISION')
#        gVect.addDBVal(bsnV,'area','area_sqmi','mi')
    
    if outGTiff:
        elevOutput=createOutput(subWshedDict['elev'])
#        for k in subWshedDict.iterkeys():
        outputGTiff(elevOutput['relief'])
        outputGTiff(subWshedDict['basin'])
     
     #extract sub_basins
        
        #add cols to stream vector
#        gVect.addDBCol(strmV,'start_x','DOUBLE PRECISION')
#        gVect.addDBCol(strmV,'start_y','DOUBLE PRECISION')
#        gVect.addDBCol(strmV,'end_x','DOUBLE PRECISION')
#        gVect.addDBCol(strmV,'end_x','DOUBLE PRECISION')
#        
##        v.db.addcol $catch columns="area_sqmi DOUBLE PRECISION"
##        v.to.db  map=$catch option=area col=area_sqmi unit=mi
##        #add data to the streams vector
##        v.db.addcol $streams columns="start_x DOUBLE PRECISION,start_y DOUBLE PRECISION,end_x DOUBLE PRECISION,end_y DOUBLE PRECISION"
##        v.to.db map=$streams option=start col=start_x,start_y
##        v.to.db map=$streams option=end col=end_x,end_y
##            gVect.addDBCol(bsnV,'area_sqmi','DOUBLE PRECISION')
    
def calcWatershed(inRast,inThreshDict,id=''):  
    '''Helper function to calculate watershed parameters
    INPUT: rast
           dict (theshold vals)
           id (used for looping through cats: default='')
    OUTPUT: dict (watershed rasters)
    '''
    for thresh in inThreshDict:
        bsnDA=thresh
        threshVal=inThreshDict[bsnDA] 
        wshedDict=gRast.calcWatershed(inRast,threshVal,bsnDA,id,True) 
    return wshedDict

#def calcWShedBasin(inRast,inThreshDict,overWrt=False):  
#    '''Helper function to calculate watershed basin
#    INPUT: rast
#           dict (theshold vals)
#    OUTPUT: dict (watershed rasters)
#    '''
#    wshedDict=runWatershed('basin',inRast,inThreshDict,overWrt)
#    return wshedDict
#
#def runWatershed(reqOut,inRast,inThreshDict,overWrt=False):
#    '''Private Helper function to calculate watershed by output need (basin,stream,all,etc)
#    INPUT:  reqOut (watershed param)
#            rast
#           dict (theshold vals)
#    OUTPUT: dict (watershed rasters dictionaries)
#    '''
##    wshedList=[]
#    
#        
##        wshedList.append(wshedDict)
#        
#    return wshedDict
##    return wshedList
    
def getCountiesBySub(sub):
    '''retrieve a list of counties for input sub basin
    INPUT: subbasin
    OUTPUT: list (counties)
    '''
    cntyStr=subCntyDict[sub]
    cntyList=cntyStr.split(',')
    return cntyList
    
def getSubs():
    ''' return list of sub basins 
    OUTPUT: list (sub basin)
    '''
    subList=subCntyDict.keys()    
    return subList
              
def getWShedThresh(inRast):
    '''retrieve the watershed threshold values by dem resolution from csv
    INPUT: inRast (raster)
    OUTPUT: threshVals (dict of cell number threshold vals by drainage area)'''
    #Get resolution of inRast
    res=gRast.getRasterRes(inRast)
    inCSV=r'%s/%s' % (ncres.appCsvDir,'thresDemRes.csv')
    csvRead=csv.reader(open(inCSV,'rb'))
    hdr=csvRead.next()
    demResIdx=hdr.index('DEM_FT') 
    bsnDAIdx=hdr.index('DA_SQMI')  
    numCellsIdx=hdr.index('NUM_CELLS')
    thresValsByDA={}
    for rw in csvRead:
        if rw[demResIdx] == res:
            demRes=rw[demResIdx]
            bsnDA=rw[bsnDAIdx]
            numCells=rw[numCellsIdx]
            thresValsByDA[bsnDA]=numCells
    return thresValsByDA

def outputGTiff(inRast):
    '''Create a GeoTiff'''
    gRast.outGTiff(inRast,ncres.appOutDir)
    
def createOutput(inRast):
    '''Function to set display properties on raster - such as shaded relief and colors
    INPUT: inRast (raster)
           output types (list)
    OUTPUT: dict (output params)
    '''
    gRast.setElevColor(inRast)
    shdRast=gRast.createRelief(inRast)
    outputDict={}
    outputDict['color']='elevation'
    outputDict['relief']=shdRast
    
    return outputDict

# #####################################
#       ------ Functions --------
# #####################################

# ######################################
#       ------ Main --------
# ######################################
#instantiate a new ncresApp obj
ncresGISApp=ncresApp()
subCntyDict=ncresGISApp.getSubCntys
ncres=ncresGISApp.getNCResApp
grs=ncres.grassApp
gDisp=grs.gDisplay()
gRast=grs.gRaster()
gVect=grs.gVector()
##DEBUG params
createSub20ft=False
calcWshed=False
convRtoV=False
importData=False
addVectDB=False
upperNeuse=True
overWrite=True
outGTiff=False

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
    main()
    #-- App Code end --#
    debug(end_main)
