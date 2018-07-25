#usage:
#python /home/dschaefer/Limits3D/biasTest/scanSignalStrength.py --mass 1200,1300,1400,1500,1700,1800,2000,2100,2200,2300,2400,2500,2600,2700,2800,2900,3000,3100,2100,3200,3300 ,3400,3500,3600,3700,3800,3900,4000,4100,4200,4300,4400,1900,1600 
import ROOT

ROOT.gROOT.SetBatch(True)

import os, sys, re, optparse,pickle,shutil,json
import time
import numpy

parser = optparse.OptionParser()
parser.add_option("-m","--mass",dest="mass",help="mass of input ROOT File",default='')
parser.add_option("-s","--expSig",dest="expSig",help="signal strenghts",default='')
parser.add_option("-l","--LexpSig",dest="LexpSig",help="list of signal strenghts",default='')

(options,args) = parser.parse_args()
  
def getLimit(filename):
      f=ROOT.TFile(filename,"READ")
      limit=f.Get("limit")
      if limit==None:
            return []
      data=[]
      for event in limit:    
            if event.quantileExpected<0:                       
                  data.append(event.limit)  #*0.01
      f.Close()           
      return data
            
def calcPValue(func,v,vmax):                  
      p = func.Integral(v,vmax)               
      return p
            
def getExpSig(expSig):                
      if expSig!="":              
            exp = expSig.split(",")            
            s=[]                  
            for e in exp:                        
                  s.append(float(e))
            return s
      return 0



if __name__=="__main__":                        
      
      signal = getExpSig(options.LexpSig)
      masses = getExpSig(options.mass) 
      graphs=[]         
      for mass in masses:                        
            g = ROOT.TGraphErrors()                  
            i=0               
            l={}                  
            err={}                 
            if options.LexpSig!="":                       
                  for s in signal:                       
                        filename = "biasTest_r"+str(int(s))+"_pythia_tau21DDT_WprimeWZ_13TeV_CMS_jj_HPHP_M"+mass+".root"                 
                        ldist = getLimit(filename)
                        print ldist                                         
                        print numpy.mean(ldist)                  
                        g.SetPoint(i,s,numpy.mean(ldist))                                          
                        g.SetPointError(i,1,numpy.std(ldist))                                         
                        i+=1                                          
            if not (options.expSig==""):                                                
                  for filename in os.listdir(os.getcwd()):                                                      
                        print filename                                                    
#if filename.find("MaxLike")!=-1:                                                     
#    continue                        
                        if filename.find(options.expSig)==-1:                              
                              continue                                                      
                        if filename.find("M"+str(int(mass)))!=-1:                                                            
                              print filename                                                            
#filename = "biasTest_r"+str(int(s))+"_pythia_tau21DDT_WprimeWZ_13TeV_CMS_jj_HPHP_M"+mass+".root"                                                            
                              s = filename.split("_"+options.expSig)[0]                                                            
                              s = s.split("_r")[1]                                                            
                    #print filename                                                            
                              ldist = getLimit(filename)                                                            
                              if len(ldist)==0:                                                                  
                                    continue                                                            
                        #print ldist                                                            
#print numpy.mean(ldist)                                                            
                              l[float(s)]= numpy.mean(ldist)                                                            
                              err[float(s)] = numpy.std(ldist)                                                            
                  for s in sorted(l.keys()):                                                                  
                        g.SetPoint(i,l[s],float(s))                                                                  
#g.SetPointError(i,err[s],1)                                                                  
                        i+=1                                                                  
            print mass                                                                  
            c = ROOT.TCanvas("c","c",400,400)                                                                  
            g.GetXaxis().SetTitle("significance")                                                                 
            g.GetYaxis().SetTitle("signal strength")                                                                  
            g.Draw("ALP")                                                                  
            c.SaveAs("scanSignalStrength_"+str(mass)+".pdf")                                                                  
            g.SetName(str(int(mass)))                                                                  
            graphs.append(g)                                                                 
      out = ROOT.TFile("scanSignalStrength.root","RECREATE")                                                                  
      for g in graphs:                                                                        
            g.Write()
      
