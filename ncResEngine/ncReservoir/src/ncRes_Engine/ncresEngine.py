'''----------------------------------------------------------------------------------
 Module Name:         ncRes_Engine.ncresEngine
 Source Name:         C:/MyDocs/projects/eclipse_wkspc/ncReservoir/src/ncRes_Engine/ncresEngine.py
 Version:             Python 2.6
 Author:              Timothy Morrissey, (timothy.morrissey@unc.edu) (tmorriss)
 Date:                Apr 8, 2010
 Required Argumuments:  
 Optional Arguments:    
 Description:         The main processing file for the NC Reservoir processing engine
 Documentation: 
----------------------------------------------------------------------------------'''
# #####################################
#       ------ Imports --------
# #####################################
from pprint import pprint as pp
import os,sys,shelve
from datetime import datetime as tstamp
from ConfigParser import ConfigParser as configParser
import pGIS
import ncRes_DAX.ncresDAX as dax
import ncRes_log.ncRes_logger as ncResLog
import ncRes_email.ncRes_email as ncResEmail 
import subBasin    
import subCatchment
import dam
import reservoir
# ######################################
#       ------ Classes --------
# ######################################
class ncresEngine():
    '''creates a pGIS implementation for the NC Reservoir Engine application'''
    def __init__(self):
        self.gisApp=pGIS.gisApp('ncres')
        self.dataSrc=self.gisApp.appDataSrc
        self.dax=dax.ncresDAX(self.dataSrc,self.gisApp.appTblDir)
        self.grassApp=self.gisApp.grassApp
        self.appRast=self.grassApp.gRaster()
        self.appVect=self.grassApp.gVector()
        #application log
        self.log=(ncResLog.appLog()).log
        #email app
        self.appEmail=ncResEmail.ncResEmail(self.gisApp.emailApp)

        #application data
        self.subBasinsData=self.dax.subBasinsData
#        self.subBasinData=self.dax.subBasinData
        self.cntyData=self.dax.cntyData
        self.subBasinObjList=[]
                
        #Lists for preprocessing needs
        self.sub20ToCreateList=[]
        self.sub20createdList=[]
        #watershed processing params
        self.threshold80=65340        #DA=15
        #self.threshold80=43560         #DA=10 
        self.threshold20=696960       #DA=10   
        #self.threshold20=1045440       #DA=15 
        
        #app region & mask
        self.appMask=None
        self.appRegion=None
        self.appMapset='ncResEngine'

    def createSub20List(self,subObj):
        '''Create a list of 20ft DEM needed to create for each subBasin
        INPUT: subObj (subBasin Object)'''
        sub20=subObj.dem20
        if not self.grassApp.dsExists(sub20):
            self.sub20ToCreateList.append(subObj)
        else:
            self.sub20createdList.append(subObj)
        
    def createSubBasin20(self,subObj):
        '''Create a 20ft DEM dataset needed for each subBasin
        INPUT: subObj (subBasin Object)
        OUTPUT subObj.dem20 (string of raster name)'''
        if self.grassApp.dsExists(subObj.dem20):
            sub20Nm=subObj.dem20
        else:
            #Need to set region to county list
            self.appRegion=self.setAppRegion(subObj.countyList)
#            self.grassApp.setRegion(subObj.countyList)
            self.appMask=self.setAppMask(subObj.dem80)
#            self.appRast.setMask(subObj.dem80)
            sub20Nm=self.appRast.mosaicRasters(subObj.countyList, subObj.dem20)
            if sub20Nm is None:
                self.log.error('!!!ERROR!!!!\t Creating subBasin.dem20 for subBasin: %s FAILED!' % (subObj.name))

        return sub20Nm
         
    def createSubBasinSurfArea(self,subObj):
        '''Calculates the surface area for each subBasin (subObj.dem80) & sets value on object
        INPUT: subObj (subBasin Object)
        OUTPUT: surface area (float)
        '''
        return self.appRast.calcSurfArea(subObj.dem80)     
        
    def createSubCatchments(self,subObj):
        '''Create the subBasin catchments for the subBasin object
        INPUT: subObj (subBasin Object)
        OUTPUT: subCatchNm (string of raster name)''' 
        if self.grassApp.dsExists(subObj.subCatchments):
            subCatchNm=subObj.subCatchments
        else:
            subCatchNm=self.appRast.calcWatershedCatchments(subObj.dem80,self.threshold80)
            if subCatchNm is None:
                self.log.error('!!!ERROR!!!!\t Creating subCatchments for subBasin: %s FAILED!' % (subObj.name))
            else:
                self.log.info('\t Reclass nulls in subCatchment raster: %s ' %(subObj.subCatchments))
                self.reclassNulls(subObj.subCatchments)

        return subCatchNm
        
    def createStreamNetwork(self,catchObj):
        '''Create the dainage area and stream network for the catchment from subObj.dem20
        INPUT: subObj (subBasin)
               catchObj (subCatch)
        OUTPUT: catchHydroDict (dict of drain & stream rasters)'''
        memUse=engineCtrls['memorysize']
        catchHydroDict={}
        if self.grassApp.dsExists(catchObj.drain):
            catchHydroDict['drain']=catchObj.drain
            catchHydroDict['stream']=catchObj.stream
        else:
            catchHydroDict=self.appRast.calcWatershedDrainStream(catchObj.rastObj, catchObj.drain, catchObj.stream, self.threshold20, memUse)
            if catchHydroDict is None:
                self.log.error('!!!ERROR!!!!\t Creating drain (%s) and stream network (%s) for subCatchment: %s FAILED!' % (catchObj.drain,catchObj.stream,catchObj.name))
                
            #thin & convert stream raster to vector
            catchStreamVect=self.appRast.convRtoV(catchHydroDict['stream'], 'line')
            if catchStreamVect is None:
                self.log.error('!!!ERROR!!!!\t Converting stream network (%s) to vector for subCatchment: %s FAILED!' % (catchObj.stream,catchObj.name))
            else:
                catchHydroDict['stream']=catchStreamVect
                
        return catchHydroDict


    def createDamLocations(self,catchObj):
        '''Segment the stream network and create dam locations
        INPUT: catchObj
        OUTPUT: damLocDict'''
        
        #First segment line
        if self.grassApp.dsExists(catchObj.damLocs):
            damLocs=catchObj.damLocs
        else:
            #Get stream length
            streamLen=self.appVect.getLineLength(catchObj.stream,'f')
            streamLenMiles=int(round(float(streamLen)/5280.00))
            
            #Segment stream network
            damInterval=5280
            damLoc=1
            damSegFileNm='damSeg.txt'
            damSegFile=open(damSegFileNm,'wb')
            for pt in range(1,streamLenMiles):
                damSegFile.write('P %i 1 %i \n' % (pt,damLoc))
                damLoc=damLoc+damInterval
                
            #neet to put a damLoc at the begin/end of each stream
            damEndLoc=int(float(streamLen)) 
            damSegFile.write('P %i 1 %i \n' % ((pt+1),damEndLoc))
            self.log.info('There are %i dam locations for %s stream segment at 1 mile intervals' % (pt,catchObj.stream))
            damSegFile.close()
                        
            #Create the dam locations and set it on catchObj
            damLocs=self.appVect.segmentLine(catchObj.stream, damSegFileNm,'dams')
            if damLocs is None:
                self.log.error('!!!ERROR!!!!\t Creating dam locations for subCatch: %s FAILED!' % (catchObj.name))
            
        return damLocs
        
    def getDamCoords(self,catchObj):
        '''create dictionary of dam pnt (key) and xyz coords
        INPUT: catchObj
        OUTPUT: damCoords (dictionary)'''
        damCoordDict=self.appVect.getPointCoords(catchObj.damLocs)
        #Get the z value of the dam 
        for key in damCoordDict.keys():
            damCoord=(damCoordDict[key]).split(',')
            damZ=self.appRast.queryRaster(catchObj.rastObj, damCoord)
            
            damXYZ=[damCoord[0],damCoord[1],damZ]
            damCoordDict[key]=damXYZ
        return damCoordDict
    
    def createReservoirBasin(self,catchObj,damObj):
        '''create reservoir basin
        INPUT: catchObj
               damObj
        OUTPUT: resBasin'''
        outBasinNm='%s_dam%s_basin' % (catchObj.name,damObj.num)
        if self.grassApp.dsExists(damObj.basin):
                resBasin=damObj.basin
        elif self.grassApp.dsExists(outBasinNm):
                resBasin=outBasinNm
        else:
            resBasin=self.appRast.calcWaterOutlet(catchObj.drain, damObj.x, damObj.y, outBasinNm)
            if resBasin is None:
                self.log.error('!!!ERROR!!!!\t Creating reservoir basin %s FAILED!' % (outBasinNm))
            else:
                self.log.info('\t Reclass nulls in reservoir basin raster: %s ' %(damObj.basin))
        
        self.reclassNulls(resBasin)
        
        return resBasin

    def createReservoir(self,catchObj,damObj,resObj):
        '''create reservoir inundated raster
        INPUT: catchObj
               damObj
               waterLvl
        OUTPUT resNm'''
        outResNm='%s_res%s_%i' % (catchObj.name,damObj.num,damObj.height)
        if self.grassApp.dsExists(resObj.floodZoneRast):
            resNm=resObj.floodZoneRast
        else:
            resCoord='%s,%s' % (damObj.x,damObj.y)
            waterLvl=int(round(float(damObj.z))) + damObj.height
            #waterLvl=damObj.height
            resNm=self.appRast.createLake(catchObj.rastObj,waterLvl, resCoord, outResNm)
            if resNm is None:
                self.log.error('!!!ERROR!!!!\t Creating reservoir %s FAILED!' % (outResNm))
            
        return resNm
        
        
    def reclassNulls(self,inDS):
        '''Reclass NULL data to 0 for calculations
        INPUT: inDS (subBasin)'''
        self.appRast.nullToZero(inDS)

    def createSubCatchmentsVect(self,subObj):
        '''Convert subBasinCatchments raster to vector
        INPUT: subObj'''
        if self.grassApp.dsExists(subObj.subCatchmentsVect):
            subCatchVect=subObj.subCatchmentsVect
        else:
            subCatchVect=self.appRast.convRtoV(subObj.subCatchments, 'area')
            if subCatchVect is None:
                self.log.error('!!!ERROR!!!!\t Converting subCatchments to vector for subBasin.subCatchments: %s FAILED!' % (subObj.subCatchments))
                return subCatchVect
            
        #add sqmi as attr
#        self.log.info('Adding sqmi attribute to vector %s' % (subCatchVect))
#        self.appVect.dropDBCol(subCatchVect, 'area_sqmi') 
#        self.appVect.addDBCol(subCatchVect, 'area_sqmi', 'double precision')
#        self.log.info('Populating sqmi attribute value to vector %s' % (subCatchVect))
#        self.appVect.addDBVal(subCatchVect, 'area', 'area_sqmi', 'mi')
        
        #clean out small areas
#        echo "Removing small areas from vector ${sub80catchVect} ..."
#        self.appVect.delVectWhere(subCatchVect,'area_sqmi < 2.0')
        #v.edit tool=delete map=$sub80catchVect where="area_sqmi < 2.0"
        return subCatchVect
    
    def getSubCatchVectCatList(self,subObj):
        '''Builds the list of subCatchment Vector Objects for the subBasin
        INPUT: subObj (subBasin object)
        OUTPUT: cat list (subCatchment Vector objects)'''
        subCatchCatList=[]
        #Get a dictionary of cat/area where area is greater than 5.0
        subCatchCatAreaDict=self.appVect.getVectCatAreaByThreshold(subObj.subCatchmentsVect, 5.0)
        for subCatchCat in subCatchCatAreaDict.keys():
            subCatchCatList.append(subCatchCat)
            
        return subCatchCatList

    def createCatchmentObj(self,subObj,subCatchID):
        '''Create the subCatchment object
        INPUT: subObj
               subCatchID (cat)
        OUTPUT: subCatchment.Catchment object'''
        subCatchNm='%s_catch%s' % (subObj.dem80,subCatchID)
        if self.grassApp.dsExists(subCatchNm):
            pass
        else:
            subCatchNm=self.appVect.vectExtractEach(subObj.subCatchmentsVect,subObj.dem80,subCatchID)
            if subCatchNm is None:
                self.log.error('!!!ERROR!!!!\t Extracting subCatchments vector with cat : %s FAILED!' % (subCatchID))
                return None
            
        subCatchObj=subCatchment.Catchment(subCatchID,subObj.id,subObj.name,subCatchNm)
        return subCatchObj
    
    def createCatchMask(self,catchObj):
        '''Convert vector to raster for masking of dem20
        INPUT: catchObj (subCatchment Object)
        OUTPUT: catchMaskNm'''
        #v.extract input=$sub80catchVect output=$sub80catchVObj list=$catchID
        catchMaskNm='%s.mask' % (catchObj.rastObj)
        if self.grassApp.dsExists(catchMaskNm):
            catchMaskNm=catchObj.mask
        else:
            catchMaskNm=self.appVect.convVtoR(catchObj.vectObj,catchObj.id,catchMaskNm)
            if catchMaskNm is None:
                self.log.error('!!!ERROR!!!!\t Converting subCatchments vector to raster for subCatch: %s FAILED!' % (catchObj.name))
            #rename to .mask
#            else:
#                catchMaskNm=self.grassApp.renameDS(catchRastNm, catchMaskNm, 'rast')
        return catchMaskNm
    
    def createCatchmentRast(self,subObj,subCatchObj):
        '''Create a 20' raster for the subCatchment
        INPUT:  subObj (subBasin object)
                subCatchObj (subCatchment object)
        OUTPUT: subCatch20'''
        catchRastNm=(subCatchObj.vectObj).replace('_','.')
        if self.grassApp.dsExists(catchRastNm):
            catchRast=subCatchObj.rastObj
        else:
            catchRast=self.appRast.clipRasterByRegion(subObj.dem20, catchRastNm)
            if catchRast is None:
                self.log.error('!!!ERROR!!!!\t Creating 20ft DEM for subCatchment: %s FAILED!' % (subCatchObj.name))
        return catchRast
        
    def setAppRegion(self,regDS,regTyp='rast'):
        '''Set the region of processing according to the input dataset
        INPUT: regDS (dataset)
               regTyp (rast/vect)'''
        self.grassApp.setRegion(regDS, regTyp,regDS)
        self.log.info('\t Region set to %s, and zoomed to %s' % (regDS,regDS))
        return regDS
    
    def setAppMask(self,maskDS,cat=''):
        '''Set the processing mask according to the input dataset
        INPUT: maskDS (dataset)
               cat (category optional)'''
        if len(cat)>0:
            self.appRast.setMask(maskDS, cat)
        else:
            self.appRast.setMask(maskDS)
        self.log.info('\t Processing mask set to : %s' % (maskDS))
        return maskDS
    
    def setPermMapset(self):
        self.grassApp.setCurMapset('PERMANENT')
        
    def setMapset(self,inMapset):
        self.grassApp.setCurMapset(inMapset)
        
    def ncResEngineMapset(self):
        '''Change the mapset to ncResEngine create it if needed'''
        mapsets=self.grassApp.getMapsets
        resEngMapset='ncResEngine'
        if not resEngMapset in mapsets:
            self.grassApp.createMapset(resEngMapset)
            self.log.info('\t Mapset %s created' % (resEngMapset))
        
        self.grassApp.setCurMapset('ncResEngine') 
        self.log.info('\t Current mapset set to %s' % (resEngMapset))
        
        
# #####################################
#       ------ Functions --------
# #####################################
def run(debugParams=''):
    '''Main method for running the NC Reservoir Engine'''
    resEng=ncresEngine()
    log=resEng.log
    appData=resEng.dax
    
#    resEng.ncResEngineMapset()
    #resEng.setPermMapset()
    
    #remove any masks created
    resEng.appRast.delMask
  
    ##DEBUG
    if len(debugParams)>0:
        subID=debugParams['sub80']
    
    #for subID in resEng.subBasinsData:
    subID=debugParams['sub80']
    if subID==debugParams['sub80']:
        if engineCtrls['deleteobjs']:
            subObj=delObj(appData.subBasinObjFile, subID)
        
        subTStamp0=tstamp.now()
        log.info('START -> SubBasinID : %s' %(subID))

        subCatchObjList=[]
        #First check to see if object already created in persistent storage
        subObj=getObj(appData.subBasinObjFile, subID)
        if subObj is None:
            subBasinData=appData.getSubBasinData(subID)
            subObj=subBasin.subBasin(subBasinData)
            subObj.countyList=appData.getSubCounties(subID)
            
        #Start the app processing
        #Set the region & mask to the subBasin.dem80
        #    resEng.appRegion=resEng.setAppRegion(subObj.dem80,'rast')
        #    resEng.appMask=resEng.setAppMask(subObj.dem80)
     
            #Change to the ncResEngine mapset
            resEng.ncResEngineMapset()
    
            #CHECK CONTROL FILE
            if engineCtrls['createsub20']:
#                #create a county20 object from countyList
                tstamp0=tstamp.now()
                log.info('\t Creating dem20 for subBasin: %s' % (subObj.name))
#
                subObj.dem20=resEng.createSubBasin20(subObj)
#                
                tstamp1=tstamp.now()
                log.info('\t SubBasin.dem20 created: %s.%s ' %(subObj.name,subObj.dem20))
                duration=tstamp1-tstamp0
                log.info('\t \t dem20 creation duration (HH:MM:SS:MS): %s' % (str(duration)))
#           
#            if engineCtrls['calcsurfarea']:
#                #calc surface area of entire subBasin for metrics
#                tstamp0=tstamp.now()
#                log.info('\t Calculating surface area for subBasin: %s' % (subObj.name))
#                
#                subObj.surfArea=resEng.createSubBasinSurfArea(subObj)
#                
#                tstamp1=tstamp.now()
#                log.info('\t Surface area for subBasin: %s = %s' %(subObj.name,subObj.surfArea))
#                duration=tstamp1-tstamp0
#                log.info('\t \t Surface area duration (HH:MM:SS:MS): %s' % (str(duration)))
#                
            if engineCtrls['createsubcatchments']:
#                #create SubCatchments
                tstamp0=tstamp.now()
                log.info('\t Creating the subCatchments for : %s with a threshold of 15 sqmi (%i cells) ' % (subObj.name,resEng.threshold80))
#                
                subObj.subCatchments=resEng.createSubCatchments(subObj)
                if subObj.subCatchments is None:
                    sys.exit('subObj.subCatchments is None: %s' % (subObj.name))

                tstamp1=tstamp.now()
                log.info('\t SubBasin.subCatchments created: %s ' %(subObj.subCatchments))
                duration=tstamp1-tstamp0
                log.info('\t \t subCatchment duration (HH:MM:SS:MS): %s' % (str(duration)))
#                    
#                #reclass nulls on basins
#                log.info('\t Reclass nulls in subCatchment raster: %s ' %(subObj.subCatchments))
#                resEng.reclassNulls(subObj)

            if engineCtrls['createsubcatchmentvector']:
                #convert subBasinCatchments to vector
                tstamp0=tstamp.now()
                log.info('\t Creating the subCatchments vector (%s)' % (subObj.subCatchments))
#                
                subObj.subCatchmentsVect=resEng.createSubCatchmentsVect(subObj)
                subObj.subCatchmentsVectList=resEng.getSubCatchVectCatList(subObj)
#
                tstamp1=tstamp.now()
                log.info('\t SubBasin.subCatchments vector created: %s ' %(subObj.subCatchmentsVect))
                duration=tstamp1-tstamp0
                log.info('\t \t subCatchment duration (HH:MM:SS:MS): %s' % (str(duration)))

                if engineCtrls['loopcatchments']:
                    #Set the mapset
                    #resEng.setMapset(subObj.dem80)
                    #Extract each vector object
                    for cat in subObj.subCatchmentsVectList:
                        if not cat=='17':
                            continue
                        pp(cat)
                        tstampCatch0=tstamp.now()
                        log.info('\t Start processing subCatchment cat : %s ' % (cat)) 
                        subCatchObj=resEng.createCatchmentObj(subObj, cat)
                        resEng.appRegion=resEng.setAppRegion(subObj.dem20)
                        subCatchObj.mask=resEng.createCatchMask(subCatchObj)
#                        resEng.appMask=resEng.setAppMask(subObj.subCatchments,cat)
                        resEng.appMask=resEng.setAppMask(subCatchObj.mask)
                        subCatchObj.rastObj=resEng.createCatchmentRast(subObj,subCatchObj)
    
                        if engineCtrls['createstreamnet']:
                            #Set the region & mask to the catch vector
#                            resEng.setAppRegion(subCatchObj.vectObj, 'vect')
                            resEng.appRegion=resEng.setAppRegion(subCatchObj.rastObj)
                            resEng.appMask=resEng.setAppMask(subCatchObj.rastObj)
                            
                            tstampStrm0=tstamp.now()
                            log.info('\t Creating stream network for catchment: %s' % (subCatchObj.name))
                            
                            #create the stream network & drainage for catchment
                            catchDrainStreamDict=resEng.createStreamNetwork(subCatchObj)
                            subCatchObj.drain=catchDrainStreamDict['drain']
                            subCatchObj.stream=catchDrainStreamDict['stream']
                            
                            tstampStrm1=tstamp.now()
                            log.info('\t Stream network vector created: %s.%s ' %(subCatchObj.name,subCatchObj.stream))
                            duration=tstampStrm1-tstampStrm0
                            log.info('\t \t Stream network duration (HH:MM:SS:MS): %s' % (str(duration)))
                        
                        if engineCtrls['createdamlocs']:
                            #Create dam locations along stream network
                            tstamp0=tstamp.now()
                            log.info('\t Creating dam locations for subCatchment %s ... ' % (subCatchObj.name))
    #                       
    #NEW 
                            #set the mask & region for the calc_reservoir from the water outlet
                            resEng.appMask=resEng.setAppMask(subCatchObj.drain)
                            resEng.appRegion=resEng.setAppRegion(subCatchObj.drain)
                            subCatchObj.damLocs=resEng.createDamLocations(subCatchObj)
    #NEW
    #                    
                            tstamp1=tstamp.now()
                            log.info('\t Finished creating dam locations for subCatchment %s' % (subCatchObj.name))
                            duration=tstamp1-tstamp0
                            log.info('\t \t dam creation for %s duration (HH:MM:SS:MS): %s' % (subCatchObj.name,str(duration)))
                            
                            #set the damLoc coords on subCatchObj
                            subCatchObj.damCoords=resEng.getDamCoords(subCatchObj)
                            
                            if engineCtrls['loopdamlocs']:
                                damObjList=[]
                                resObjList=[]
                                for damPnt in subCatchObj.damCoords:
#                                    damCoord=(subCatchObj.damCoords[damPnt]).split(',')
                                    damCoord=subCatchObj.damCoords[damPnt]
                                    damID='%s%s%s' %(subObj.id,subCatchObj.id,damPnt)
                                    damNum=damPnt
                                    damCatchID=subCatchObj.id
                                    damSubID=subCatchObj.subID
                                    damNm='%s_dam%s' % (subCatchObj.name,damPnt)
                                    damX=damCoord[0]
                                    damY=damCoord[1]
                                    damZ=damCoord[2]
                                    
                                    damObj=getObj(appData.damObjFile, damID)
                                    if damObj is None:
                                        damObj=dam.Dam(damID,damNum,damCatchID,damSubID,damNm,damX,damY,damZ)
                    #WORKS
                                        #damObj.height=150
                    #WORKS
                                    #create reservoir objects    
                                    if engineCtrls['createresobjects']:
                                        log.info('\t Creating reservoir basin for dam location %s ... ' % (damObj.name))
                                        damObj.basin=resEng.createReservoirBasin(subCatchObj, damObj)
                                    
            ##SHOULD EXPORT damObj.basin for spatial App
                                    
                                    
#                                        #set the mask & region for the calc_reservoir from the water outlet
                                        resEng.appMask=resEng.setAppMask(damObj.basin)
                                        resEng.appRegion=resEng.setAppRegion(damObj.basin)
                                        #Reservoir object params
                    #WORKS              resID=damID
                                        
                                        #Loop through dam heights
                    #NEW
                                        damHtList=[25,50,75,100,125,150]
                                        pp('Looping through dam heights %s' % (damHtList))
                                        for damHt in damHtList:
                                        #create dam objects
                                            damObj.height=damHt
                                            resID='%s%i' % (damID,damHt)
                                            resNum='%s%i' % (damObj.num,damObj.height)
                                            resObj=reservoir.Reservoir(resID,resNum,subCatchObj.id,subObj.id,subObj.name,damObj)
                                            #Inundate 
                                            tstampFlood0=tstamp.now()
                                            log.info('\t Creating reservoir at dam location %s at dam height %i... ' % (damObj.name,damObj.height))
    #                    
                                            resObj.floodZoneRast=resEng.createReservoir(subCatchObj,damObj,resObj)
                                            
                                            tstampFlood1=tstamp.now()
                                            log.info('\t Finished reservoir at dam location %s at dam height %i... ' % (damObj.name,damObj.height))
                                            duration=tstampFlood1-tstampFlood0
                                            log.info('\t \t Reservoir inudation creation for %s duration (HH:MM:SS:MS): %s' % (damObj.name,str(duration)))
                      
                    #NEW
                    #WORKS
                                        
#                                        resNum='%s%s' % (damObj.num,damObj.height)
#                                        resObj=getObj(appData.resObjFile, resID)
#                                        if resObj is None:
#                                            resObj=reservoir.Reservoir(resID,resNum,subCatchObj.id,subObj.id,subObj.name,damObj)
#
##                                       #Inundate 
#                                        tstampFlood0=tstamp.now()
#                                        log.info('\t Creating reservoir at dam location %s at dam height %i... ' % (damObj.name,damObj.height))
##                    
#                                        resObj.floodZoneRast=resEng.createReservoir(subCatchObj,damObj,resObj)
#                                        
#                                        tstampFlood1=tstamp.now()
#                                        log.info('\t Finished reservoir at dam location %s.' % (damObj.name))
#                                        duration=tstampFlood1-tstampFlood0
#                                        log.info('\t \t Reservoir inudation creation for %s duration (HH:MM:SS:MS): %s' % (damObj.name,str(duration)))
#                      
#                                        resObjList.append(resObj)
#                                        damObjList.append(damObj)
                                
                                        #persist the dam objects
#                                        setObj(appData.resObjFile, resID, resObj)
#                                        setObj(appData.damObjFile, damID, damObj)
                      #WORKS              
                                log.info('\t Finished creating dam objects for subCatchment %s' % (subCatchObj.name))
                                subCatchObj.damObjects=damObjList
                                subCatchObj.resObjects=resObjList
                                 
                                
                                 
                        #set the subCatchObj on the subBasin
                        subCatchObjList.append(subCatchObj)
                        subObj.subCatchObjects=subCatchObjList
                        #persist object to filesystem
                        setObj(appData.catchObjFile,cat,subCatchObj)
                        
                        tstampCatch1=tstamp.now()
                        log.info('\t Finished processing subCatchment %s' % (subCatchObj.name))
                        duration=tstampCatch1-tstampCatch0
                        log.info('\t \t subCatchment %s duration (HH:MM:SS:MS): %s' % (subCatchObj.name,str(duration)))

#               
#            if engineCtrls['loopcatchments']:   
##                tstampC0=tstamp.now()
##                log.info('\t Looping through each of the %i subCatchments of %s ' % (len(subCatchList),subObj.name))
#                testCat='118'
#                #if testCat' in subObj.subCatchmentsVectList:
#                if testCat=='118':
#                    cat='118'
#                    catchObj=getObj(appData, cat)
#                    tstamp0=tstamp.now()
#                    log.info('\t Start processing subCatchment cat : %s ' % (cat))
#                
                 #   subCatchObj=resEng.createCatchmentObj(subObj, cat)
#                    #Set the region to the sub20 for raster conversion to 20'
#                    resEng.setAppRegion(subObj.dem20)
#                    subCatchObj.rastObj=resEng.createCatchmentRaster(subCatchObj)
##                    #Set the region & mask to the catch vector
#                    resEng.setAppRegion(subCatchObj.vectObj)
#                    resEng.setAppMask(subCatchObj.rastObj)
#                    
                        
#                    tstampStrm0=tstamp.now()
#                    log.info('\t Creating stream network for catchment: %s' % (subCatchObj.name))
#                    
#                    #create the stream network & drainage for catchment
#                    catchDrainStreamDict=resEng.createStreamNetwork(subObj)
#                    subCatchObj.drain=catchDrainStreamDict['drain']
#                    subCatchObj.stream=catchDrainStreamDict['stream']
#                    
#                    tstampStrm1=tstamp.now()
#                    log.info('\t Stream network vector created: %s.%s ' %(subCatchObj.name,subCatchObj.stream))
#                    duration=tstampStrm1-tstampStrm0
#                    log.info('\t \t Stream network duration (HH:MM:SS:MS): %s' % (str(duration)))
#                    
#                    #Create dam locations along stream network
#                    
#                    #`v.report map=upns20_catch3_strms option=length units=f`
#                    
#                    tstamp1=tstamp.now()
#                    log.info('\t Finished processing subCatchment cat : %s ' % (cat))
#                    duration=tstamp1-tstamp0
#                    log.info('\t \t subCatchment %s duration (HH:MM:SS:MS): %s' % (cat,str(duration)))
#                
#                tstampC1=tstamp.now()
#                log.info('\t Finished all of the %i subCatchments of %s ' % (len(subCatchList),subObj.name))
#                duration=tstampC1-tstampC0
#                log.info('\t \t Total subCatchment processing duration (HH:MM:SS:MS): %s' % (str(duration)))
#                
            #persist object to filesystem
            setObj(appData.subBasinObjFile,subID,subObj)
             
#            if engineCtrls['sendemail']:
#                subEmail='SubBasin %s processed'%(subObj.name)
#                resEng.appEmail.sendEmail(subEmail,'SubID %s' % (subObj.id))
        else:
            pp(subObj.name)
        
        subTStamp1=tstamp.now()
        duration=subTStamp1-subTStamp0
        log.info('END -> SubBasinID : %s' %(subID))
        log.info('\t \t SubBasin processing duration (HH:MM:SS:MS): %s' % (str(duration)))
        #remove any masks created
        resEng.appRast.delMask
        
    #remove any masks created
    pp('deleting mask')
    resEng.appRast.delMask
#                      
def getObj(objDBFile,objKey):
    '''Retrieve an object from persistent storage (shelve)
    INPUT:  objDBFile (file for persistent storage)
            objKey (object key)
    OUTPUT: object'''          
    objDB=shelve.open(objDBFile)
    if objDB.has_key(objKey):
        obj=objDB[objKey]
        objDB.close()
        return obj
    
def setObj(objDBFile,objKey,obj):
    '''Set an object on persistent storage (shelve)
    INPUT:  objDBFile (file for persistent storage)
            objKey (object key)'''
    subDB=shelve.open(objDBFile)
    subDB[objKey]=obj

def delObj(objDBFile,objKey):
    '''Helper function to delete and object during debugging'''
    objDB=shelve.open(objDBFile)
    if objDB.has_key(objKey):
        del objDB[objKey]
        
        objDB.close()

def createSubBasinMapsets():
    resEng=ncresEngine()
    appData=resEng.dax
    subsDict=appData.subBasinsData
    mapsets=resEng.grassApp.getMapsets
    for key in subsDict.iterkeys():
        subNm=(subsDict[key])[2]
        if not subNm in mapsets:
            resEng.grassApp.createMapset(subNm)
            pp('%s mapset created' % (subNm))
        
        
def moveSubDatatoSubMapset():
    resEng=ncresEngine()
    appData=resEng.dax
    subsDict=appData.subBasinsData
    #resEng.grassApp.setCurMapset('ncResEngine')
    engMapset=resEng.appMapset
    mapsets=resEng.grassApp.getMapsets
    pp(mapsets)
    for key in subsDict.iterkeys():
        subNm=(subsDict[key])[2]
        if subNm=='upperneuse':
            if not subNm in mapsets:
                resEng.grassApp.createMapset(subNm)
                pp('%s mapset created' % (subNm))
                
            #copy subData to appropriate subMapset
            subDataRastList=resEng.grassApp.getRastListByPatternByMapset(subNm, engMapset) 
            subDataVectList=resEng.grassApp.getVectListByPatternByMapset(subNm,engMapset)
            #set the mapset to the subMapset
            resEng.grassApp.setCurMapset(subNm)
            pp('Current mapset : %s' % (resEng.grassApp.getCurMapset()))
            for subR in subDataRastList:
                if len(subR)>1:
    #                pp(subR)
                    subDS=(subR.split('@'))[0]
    #                pp(subDS)
    #                cpyCmd="'%s,%s'" %(subR,subDS)
    #                pp(cpyCmd)
    #                #copy from ncResEngine to subMapset
                    resEng.grassApp.copyRastToMapset(subR,subDS)
#            for subV in subDataVectList:
#                if len(subV)>1:
#                    subVDS=(subV.split('@'))[0]
#                    resEng.grassApp.copyVectToMapset(subV,subVDS)
#                

def exportGrassDataToArc(inPat,outDir):
    
    #Export raster to arcAscii
    exportToArcASCII(inPat, outDir)
    
    #Export vector to shapefile
    exportToShp(inPat,outDir)

def exportToArcASCII(inPat,outDir):
    pp('Running export...')
    resEng=ncresEngine()
    appRast=resEng.appRast
    grassApp=resEng.grassApp
    rastList=grassApp.getRastListByPatternByMapset(inPat, 'ncResEngine')
#    outArcDir=r'C:/MyDocs/projects/nc_res/gis_data/rast/grsExport/upperneuse'
    outArcDir=outDir
    pp('Exporting the following rasters to arc ascii to %s :' % (outArcDir))
    pp(rastList)
    arcAscList=[]
    for rast in rastList:
        arcAscNm='%s.asc' % (((rast.split('@'))[0]).replace('.','_'))
        pp('Exporting %s to %s as %s ...' % (rast,outArcDir,arcAscNm))
        outArc=appRast.outArcGrid(rast, arcAscNm, outArcDir)
        arcAscList.append(outArc)
        pp('Done')

def exportToShp(inPat,outDir):
    pp('Running export...')
    resEng=ncresEngine()
    appVect=resEng.appVect
    grassApp=resEng.grassApp
    vectList=grassApp.getVectListByPatternByMapset(inPat, 'ncResEngine')
    outShpDir=outDir
#    outShpDir=r'C:/MyDocs/projects/nc_res/gis_data/grsExport/upperneuse'
    pp('Exporting the following vectors to shapefile %s :' % (outShpDir))
    pp(vectList)
    shpList=[]
    for vect in vectList:
        shpNm=(vect.split('@'))[0]
        pp('Exporting %s to %s as %s ...' % (vect,outShpDir,shpNm))
        outShp=appVect.exportToShp(vect, outShpDir)
        shpList.append(outShp)
        pp('Done')


            
# ######################################
#       ------ Main --------
# ######################################

#Application control file for running certain functions
engDir=os.path.dirname(__file__)
ncResEngine_ctrl='%s/ncresEngine_appControl.ini' % (engDir)
appCtrlConf=configParser()
appCtrlConf.read(ncResEngine_ctrl)
appConfCtrls=appCtrlConf.items('appCtrl')

##pp(engineCtrls)
engineCtrls={}
for ctrl in appConfCtrls:
    engineCtrls[ctrl[0]]=ctrl[1]

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
    def delDamObjects():
        damsDB=shelve.open(damsDBFile)
        for key in damsDB:
            pp(key)
            del damsDB[key]
        damsDB.close()
    
    def delResObjects():
        resDB=shelve.open(resDBFile)
        for key in resDB:
            pp(key)
            del resDB[key]
        resDB.close()
    #-- App Code start --#
    #delete dam objects
    dbLoc=r'C:/MyDocs/projects/nc_res/gis_data/csv/tbl'
    damsDBFile=r'%s/damObjs.data' % (dbLoc)
    resDBFile=r'%s/resObjs.data' % (dbLoc)
    
    if engineCtrls['deleteobjs']:
        delDamObjects()
        delResObjects()
        
    
    
    debugDict={}
   # debugDict['sub80']='3020201'   ##upperneuse
    #debugDict['sub80']='3040101'   ##upperyadkin
    #debugDict['sub80']='3030005'   ##lowercapefear
    debugDict['sub80']='3030002'    ##haw
#    debugDict['sub80']='3030003'   ##deep
       
    #Start the process
    run(debugDict)
    
#    damsDB=shelve.open(damsDBFile)
#    for key in damsDB:
#        pp(key)
#        del damsDB[key]
#    damsDB.close()
    
    
#    expPat='upperneuse*'
#    exportDir=r'D:/MyDocs/projects/nc_res/gis_data/grassExport/upperneuse'
#    exportGrassDataToArc(expPat,exportDir)


#    exportToArcASCII(expPat)
#    exportToShp(expPat)
    
    
    
    
    

#    if objDB.has_key(objKey):
#        del objDB[objKey]
#        objDB.close()
#    damsDB=shelve.open(damsDBFile)
#    if objDB.has_key(objKey):
#        obj=objDB[objKey]
#        objDB.close()
#        return obj
#    createSubBasinMapsets()
    #moveSubDatatoSubMapset()
    #-- App Code end --#
    debug(end_main)