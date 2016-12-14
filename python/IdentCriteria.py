"""
This module defines the abstract base class for Event Identification Criteria in Stride Search.
Implementations for basic criteria are included.
"""
from Event import Event, print_copyright
from abc import ABCMeta, abstractmethod
from numpy import amax, amin, ones, mean, argmax, argmin, array, linspace, concatenate
from SectorList import Sector
from datetime import datetime

class Criterion(object):
    """
    Each criterion will be evaluated once for each sector, during each time step.
    If an evaluation returns True, then the Criterion can return the corresponding Event.
    """
    __metaclass__ = ABCMeta
    
    def __init__(self, varname, threshold):
        self.varnames = [varname]
        self.threshold = threshold
    
    def addVariableName(self, varname):
        self.varnames.append(varname)    
                
    def __repr__(self):
        return "<%s: varname = %s, threshold = %s>"%(self.__class__.__name__, self.varnames[0], self.threshold)
    
    @abstractmethod
    def evaluate(self, sector, workspace):
        pass
      
    @abstractmethod
    def returnEvent(self, sector, workspace, dtime):
        pass
   
    def printData(self):
    	for att in ['varnames', 'threshold']:
    		print '\t', att, ':', getattr(self, att)
    
class MaxCriterion(Criterion):
    """ 
    Maximum value criterion.  Returns True if the maximum value of the data 
    meets or exceeds the threshold
    """
    def evaluate(self, sector, workspace):
        return amax(workspace[self.varnames[0]], axis=0) >= self.threshold

            
    def returnEvent(self, sector, workspace, dtime):
        val = amax(workspace[self.varnames[0]])
        ind = argmax(workspace[self.varnames[0]])
        vals = {self.varnames[0] : val}
        desc = self.varnames[0] + " max"
        return Event(desc, sector.dataPoints[ind], dtime, sector.dataPointIndices[ind], vals)

                                                        
class MinCriterion(Criterion):
    """ 
    Minimum value criterion.  Returns True if the minimum value of the data meets 
    or falls below the threshold.
    """
    def evaluate(self, sector, workspace):
        return amin(workspace[self.varnames[0]]) <= self.threshold

            
    def returnEvent(self, sector, workspace, dtime):
        val = amin(workspace[self.varnames[0]])
        ind = argmin(workspace[self.varnames[0]])
        vals = {self.varnames[0] : val}
        desc = self.varnames[0] + ' min'
        return Event(desc, sector.dataPoints[ind], dtime, sector.dataPointIndices[ind], vals)
 

class MaxAverageCriterion(Criterion):
    """ 
    Maximum average criterion. Returns True if the mean of the data meets or 
    exceeds the threshold.
    
    NOTE: The average computed here is an arithmetic average, not a spatial average.
    """ 
    def evaluate(self, sector, workspace):
        return mean(workspace[self.varnames[0]]) >= self.threshold

    def returnEvent(self, sector, workspace, dtime):
        val = amax(mean(workspace[self.varnames[0]]))
        ind = argmax(mean(workspace[self.varnames[0]]))
        vals = {self.varnames[0] : val}
        desc = 'max avg(' + self.varnames[0] + ')'
        return Event(desc, sector.dataPoints[ind], dtime, sector.dataPointIndices[ind], vals)
        
class VariationExcessCriterion(Criterion):
    """ 
    Variation excess criterion.  Returns True if the maximum data value exceeds 
    the data average by the threshold value or greater.
    
    NOTE: The average computed here is an arithmetic average, not a spatial average.
    """
    def evaluate(self, sector, workspace):
        return amax(workspace[self.varnames[0]] - mean(workspace[self.varnames[0]])) >= self.threshold

    def returnEvent(self, sector, workspace):
        val = amax(workspace[self.varnames[0]] - mean(workspace[self.varnames[0]]))
        ind = argmax(workspace[self.varnames[0]] - mean(workspace[self.varnames[0]]))
        vals = {'var(' + self.varnames[0] + ')' : val}
        desc = 'max var(' + self.varnames[0] + ')'
        return Event(desc, sector.dataPoints[ind], dtime, sector.dataPointIndices[ind], vals)

class DifferenceCriterion(Criterion):
    """
    Difference criterion. Returns True if the maximum element-wise value of the 
    difference data1 - data2 meets or exceeds the threshold.
    """
    def __init__(self, varname1, varname2, threshold):
        Criterion.__init__(self, varname1, threshold)
        self.addVariableName(varname2)
    
    def evaluate(self, sector, workspace):
        if amax(workspace[self.varnames[0]] - workspace[self.varnames[1]]) >= self.threshold:
            return True
        else:
            return False
            
    def __repr__(self):
       return "<%s: varname = %s, varname2 = %s, threshold = %s>"%(self.__class__.__name__, 
        self.varnames[0], self.varnames[1], self.threshold)       
    
    def returnEvent(self, sector, workspace, dtime):
        val = amax(workspace[self.varnames[0]] - workspace[self.varnames[1]])
        ind = argmax(workspace[self.varnames[0]] - workspace[self.varnames[1]])
        vals = { 'diff(' + self.varnames[0] + ',' + self.varnames[1] + ')' : val}
        desc = 'max(' + self.varnames[0] + ' - ' + self.varnames[1] + ')'
        return Event(desc, sector.dataPoints[ind], dtime, sector.dataPointIndices[ind], vals)         
        
if __name__ == "__main__":
    print_copyright()
    # Test constructor, basic fns
    c = MaxCriterion("vorticity", 1.0E-4)
    print 'MaxCriterion created.'
    print(c)
    c.printData()
    # Test evaluate
    rn = datetime.now()
    testDt = datetime(rn.year, rn.month, rn.day, rn.hour)
    secLats = linspace(-6.0, 6.0, 13)
    secLons = linspace(-6.0, 6.0, 13)
    secDataPts = [(lat,lon) for lat in secLats for lon in secLons]
    latInds = linspace(84, 96, 13, dtype = int)
    lonIndsLeft = linspace(354, 359, 6, dtype = int)
    lonIndsRight = linspace(0, 6, 7, dtype = int)
    lonInds = concatenate((lonIndsLeft, lonIndsRight))
    secInds = [(i, j) for i in latInds for j in lonInds]
    testSector = Sector(0.0, 0.0, 1000.0, 500.0, 500.0, secDataPts, secInds)
    maxWorkspace = {'vorticity': linspace(0.0, 1.0, len(secDataPts))}
    print 'max criterion evaluate result = ', c.evaluate(testSector, maxWorkspace)
    maxEv = c.returnEvent(testSector, maxWorkspace, testDt)
    print 'max criterion returned event = ', maxEv
    maxEv.printData()
    
    diffWorkspace = {'a' : linspace(0.0, 50.0, len(secDataPts)), 'b' : linspace(50.0, 100.0, len(secDataPts))}
    cd = DifferenceCriterion("b","a", 1.0)
    print 'DifferenceCriterion created.'
    print cd
    cd.printData()
    print 'DifferenceCriterion evaluate result = ', cd.evaluate(testSector, diffWorkspace)
    diffEv = cd.returnEvent(testSector, diffWorkspace, testDt)
    print 'Difference criterion returned event = ', diffEv
    diffEv.printData()
        
                        