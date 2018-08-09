#usage:
# python signif_expsig.py --mass 1200 -l 0.0,0.017,0.033,0.05,0.066,0.083,0.1,0.116,0.133,0.15 -r "graviton"
# python signif_expsig.py --mass 2000 -l 0.0,0.004,0.008,0.012,0.016,0.02,0.024,0.028,0.033,0.037 -r "graviton"
# python signif_expsig.py --mass 4000 -l 0.0,0.002,0.004,0.006,0.008,0.01,0.012,0.014,0.016,0.018 -r "graviton"

# python signif_expsig.py --mass 1200 -l 0.0,0.012,0.023,0.035,0.047,0.059,0.07,0.082,0.094,0.106 -r "radion"
# python signif_expsig.py --mass 2000 -l 0.0,0.003,0.006,0.009,0.012,0.015,0.018,0.021,0.024,0.027 -r "radion"
# python signif_expsig.py --mass 4000 -l 0.0,0.002,0.003,0.005,0.006,0.008,0.009,0.011,0.012,0.014 -r "radion"

import ROOT

ROOT.gROOT.SetBatch(True)

import os, sys, re, optparse,pickle,shutil,json
import time
import numpy

parser = optparse.OptionParser()
parser.add_option("-m","--mass",dest="mass",help="mass of input ROOT File",default='')
parser.add_option("-s","--expSig",dest="expSig",help="signal strenghts",default='')
parser.add_option("-l","--LexpSig",dest="LexpSig",help="list of signal strenghts",default='')
parser.add_option("-r","--resonance",dest="resonance",help="radion or graviton",default="radion")

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
                  print e
            return s
      return 0



if __name__=="__main__":                        
      
      signal = getExpSig(options.LexpSig)
      masses = getExpSig(options.mass) 
      res = options.resonance
      graphs=[]         
      for mass in masses:                        
            g = ROOT.TGraphErrors()                  
            i=0               
            l={}                  
            err={}                 
            if options.LexpSig!="":              
                  for s in signal: 
                        print s
                        directory = res+"_"+str(int(mass))+"_"+str(s)+"/"
                        print directory
                        filename = "higgsCombineTest.ProfileLikelihood.mH"+str(int(mass))+".root"                 
#                        filename = "higgsCombineTest.ProfileLikelihood.mH"+str(int(mass))+".123456.root"                 
                        ldist = getLimit(directory+filename)
                        print ldist                                         
                        print numpy.mean(ldist)                  
                        g.SetPoint(i,numpy.mean(ldist),s)                                          
                        g.SetPointError(i,numpy.std(ldist),1)                                         
                        # g.SetPoint(i,s,numpy.mean(ldist))                                          
                        # g.SetPointError(i,1,numpy.std(ldist))                                         
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
            c.SaveAs("scanSignalStrength_"+res+"_"+str(int(mass))+".pdf")                                                                  
            g.SetName(str(int(mass)))                                                                  
            graphs.append(g)                                                                 
      out = ROOT.TFile("scanSignalStrength_"+res+"_"+str(int(mass))+".root","RECREATE")                                                                  
      for g in graphs:                                                                        
            g.Write()
      
