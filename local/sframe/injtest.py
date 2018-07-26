#! /usr/bin/python
# usage python injtest.py --scanSig -t 100
import sys
import os
import optparse
import numpy
import tempfile
import platform
from copy import deepcopy
import subprocess
import ROOT as rt
# check for python version
if platform.python_version() < "2.5.1":
  print "FATAL: you need a newer python version"
  sys.exit()

from multiprocessing import Process
import thread
import subprocess
import time
import shutil
import socket


# if ntuplizer trees are to be put into trees: python batchsubmission.py --sframe -j SignalMC_Summer16.py 
# or better yet: nohup python batchsubmission.py --sframe -j SignalMC_Summer16.py & 


class ConfigReader:
    model = []
    opt = []
    outDir=[]
    inDir =[]
    mass =[]
    masses =[]
    massmax=[]
    massmin=[]
    step=[]
    channel=[]
    purity=[]
    purities=[]
    channels=[]
    channel2=[]
    def __init__(self,filename):
        config = open(filename,'r')
        for i in config.readlines():
            if '#' in i: continue
            if 'model' in i: 
                self.model.append(  (i.split("=")[1]).split("\n")[0])
            if 'options' in i:
                self.opt .append( (i.split('"')[1]).split('"')[0])
            if 'inDir' in i:
                self.inDir .append( (i.split("=")[1]).split("\n")[0])
            if 'outDir' in i:
                self.outDir .append( (i.split("=")[1]).split("\n")[0])
            if 'masses' in i:
                self.mass .append( (i.split("=")[1]).split("\n")[0])
            if 'channels' in i:
                self.channel2 .append( (i.split("=")[1]).split("\n")[0])    
            if 'purities' in i:
                self.purity .append( (i.split("=")[1]).split("\n")[0])
            
            if 'massmax' in i:
                self.massmax .append( (i.split("=")[1]).split("\n")[0])
            if 'massmin' in i:
                self.massmin .append( (i.split("=")[1]).split("\n")[0])
            if 'step' in i:
                self.step .append( (i.split("=")[1]).split("\n")[0])
            if 'channel' in i:
                self.channel .append( (i.split("=")[1]).split("\n")[0])
        for l in self.mass:
            self.masses .append(l.split(','))
        for l in self.channel2:
            self.channels .append(l.split(','))
        for l in self.purity:
            self.purities .append(l.split(','))
        print self.model
        print self.opt
        print self.inDir
        print self.outDir
        print self.mass
        print self.masses




 
def writeSUBMIT(arguments,mem,time,name,mass,sig):
  text_file = open(name+str(mass)+"_"+str(sig)+".submit", "w")
  text_file.write("request_memory = "+str(mem)+" GB\n")
#  text_file.write("requirements = (TARGET.ProvidesCPU) && (TARGET.ProvidesEkpResources)\n")
  text_file.write("executable =  "+name+".sh \n")
  text_file.write("arguments = {0} \n".format( arguments[0]  ))
  text_file.write("log = job"+str(mass)+"_"+str(sig)+".log \n")
  text_file.write("output =  job"+str(mass)+"_"+str(sig)+".out\n")
  text_file.write("error = job"+str(mass)+"_"+str(sig)+".err\n")
  text_file.write("queue 1\n")
  text_file.close()






 
    ##################################
    ## submit job to set up CMSSW 
    ##################################
    #jobs.SetExecutable("job_setup.sh")  # set job script
    #jobs.SetArguments(' ')              # set arguments
    #jobs.SetFolder('../setup/')         # set subfolder !!! you have to copy your job file into the folder


    ##################################
    # submit job to run combine
    ##################################

    # jobs.SetExecutable(name)  # set job script
    # #jobs.SetFolder('/usr/users/dschaefer/job_submission/local/sframe')  # set subfolder !!! you have to copy your job file into the folder
    # jobs.SetArguments(arguments)              # write an JDL file and create folder f            # set arguments
    # jobs.WriteSUBMIT() # write an JDL file and create folder for log files


        

def waitForBatchJobs(nameJobFile):
    timeCheck = 10 #delay for process check
    while (True):
        time.sleep(timeCheck)
        proc = subprocess.Popen(["(condor_q zoiirene | grep "+nameJobFile+" )"], stdout=subprocess.PIPE, shell=True)
        (query, err) = proc.communicate()
        print "program output:", query
        if query.find("zoiirene")==-1:
            break
        listOfJobs = query.split('\n')
        #print listOfJobs
        jobID=[]
        numberRunningJobs=[]
        numberJobs=[]
        numberIdleJobs=[]
        numberHeldJobs=[]

        for i in range(0,len(listOfJobs)-1):
            tmp = listOfJobs[i].split(' ')
            #print tmp
            add =0
            if tmp[-2]=="...":
                add = -2
            numberRunningJobs.append(tmp[-14+add])
            numberJobs.append(tmp[-2+add])
            numberIdleJobs.append(tmp[-8+add])
            jobID.append(tmp[-1])
            numberHeldJobs.append(tmp[-4+add])
        
            print "number of submitted jobs : "+numberJobs [i]   
            print "number of idle jobs :      "+numberIdleJobs[i]
            print "number of running jobs :   "+numberRunningJobs[i]
            print "number of held jobs :      "+numberHeldJobs[i]
        #print jobID[i]
    

 
def testSignalStrenght(config,toys):
    reader = ConfigReader(config)
    masses = [1200,2000,4000]
    for i in range(0,len(reader.model)):
#            for p in reader.purities[i]:
      print "model "+reader.model[i]
#      for m in range(0,int((int(reader.massmax[i])-int(reader.massmin[i]))/100.)):
      for mass in masses:#range(0,int((int(reader.massmax[i])-int(reader.massmin[i]))/100.)):
        expSig=[]
        #mass = str(m*100+int(reader.massmin[i]))
        print "mass "+str(mass)
        f = rt.TFile(reader.inDir[i]+"CMS_jj_"+str(mass)+"_graviton_invM800_de4_13TeV__invMass_afterVBFsel_asymptoticCLs_new.root","READ") # attention root file here must be calculated from workspace below!!!
#                    f = rt.TFile("/home/dschaefer/Limits3DFit/pythia/pythia_tau21DDT_WprimeWZ_obs.root","READ") # attention root file here must be calculated from workspace below!!!
        limit=f.Get("limit")
        lim=0
        for event in limit:
#          print event.mh
          if int(event.mh)!=int(mass):
            continue
          if event.quantileExpected>0.974 and event.quantileExpected<0.976:            
            lim=event.limit
            print "limit at -2 sigma "+str(lim)
            for counter in range(0,10):
              expSig.append(round(0.0+counter*lim*2.5/10.,3))
              print "expSig "+str(expSig)
              for sig in expSig:
                #                        if reader.opt[i] == "3D":
                workspace = "CMS_jj_graviton_invM800_de45_"+str(mass)+"_13TeV.root"#"workspace_pythia.root"
                outname="biasTest_r"+str(float(sig))+"_"+reader.model[i]+"_13TeV_CMS_jj_M"+str(mass)+".root"
                datacard="CMS_jj_graviton_invM800_de45_"+str(mass)+"_13TeV__invMass_afterVBFsel.txt"
                arguments=[]
                arguments.append(reader.inDir[i]+" "+workspace+" "+str(mass)+" "+outname+" "+str(toys)+" "+str(sig)+" "+datacard)
                print arguments

                
                writeSUBMIT(arguments,1.5,30*60,"significance",mass,sig) #1.5 GB = 1500 dani 
                command = "condor_submit significance"+str(mass)+"_"+str(sig)+".submit"
                process = subprocess.Popen(command,shell=True)
                waitForBatchJobs("significance.sh")



def fitInjectedSignal(config,signal,toys):
    reader = ConfigReader(config)
    arguments=[]
    masses = [1200,2000,4000]
    for i in range(0,len(reader.model)):
#      for m in range(0,int((int(reader.massmax[i])-int(reader.massmin[i]))/100.)):
      for mass  in masses:
        print mass
        filename = signal+"_"+str(int(mass))+".root"
        print filename
        f = rt.TFile(filename,"READ")
#        mass = str(m*100+int(reader.massmin[i]))
#        g = rt.TGraph(f.Get(mass))
#        g = f.GetObject(str(mass),rt.TGraph)
#        g = rt.TGraph(f.GetObject(str(mass),rt.TGraph) )
        g = f.Get(str(mass))
        sig = g.Eval(3)  # inject signal with 3 sigma significance!
        print "signal injected for 3 sigma significance is "+str(sig)
        outname="biasTest_MaxLikelihood_r"+str(int(sig))+"_"+reader.model[i]+"_13TeV_CMS_jj_M"+str(mass)+".root"
        workspace = "CMS_jj_graviton_invM800_de45_"+str(mass)+"_13TeV.root"#"workspace_pythia.root"
        datacard="CMS_jj_graviton_invM800_de45_"+str(mass)+"_13TeV__invMass_afterVBFsel.txt"
        arguments=[]
        arguments.append(reader.inDir[i]+" "+workspace+" "+str(mass)+" "+outname+" "+str(toys)+" "+str(sig)+" "+datacard)
        print arguments
    # writeJDL(arguments,1.5,30*60,"injecteSignal.sh") #1.5 GB = 1500 dani
    # command = "condor_submit injecteSignal.submit"
    # process = subprocess.Popen(command,shell=True)
    # waitForBatchJobs("injecteSignal.sh")
 
        writeSUBMIT(arguments,1.5,30*60,"injecteSignal",mass,sig) #1.5 GB = 1500 dani 
        command = "condor_submit injecteSignal"+str(mass)+"_"+str(sig)+".submit"
        process = subprocess.Popen(command,shell=True)
        waitForBatchJobs("injecteSignal.sh")
 
 
 
 
        
if __name__=="__main__":
    optparser=optparse.OptionParser(usage="%prog -j jobOption.py")
    optparser.add_option("-j", "--jobOptions", dest="jobOptions",
                    action="store", default="Datasets.py",
                    help="joboptions to process [default = %default]")
    optparser.add_option("-s", "--saveTmp", dest="saveTmp",
                    action="store_true", default=False,
                    help="save temporary output files [default = %default]")
    
    optparser.add_option("-n", "--sframe", dest="sframe",
                    action="store_true", default=False,
                    help="do first analysis step i.e. calculate trees from ntuplizer trees [default = %default]")
    optparser.add_option("-a", "--all", dest="ALL",
                    action="store_true", default=False,
                    help="do everything from beginning to end !needs right joboptions file! [default = %default]")
    optparser.add_option("-c", "--combine", dest="combine",
                    action="store_true", default=False,
                    help="calculate the limits only [default = %default]")
    optparser.add_option("-w", "--workspaces", dest="workspaces",
                    action="store_true", default=False,
                    help="calculate workspaces and datacards for limit setting [default = %default]")
    optparser.add_option("-i", "--interpolate", dest="interpolate",
                    action="store_true", default=False,
                    help="interpolate trees for limit setting [default = %default]")
    
    optparser.add_option( "--datacardsPlusLimits", dest="dataPlusLim",
                    action="store_true", default=False,
                    help="calc datacards and limits [default = %default]")
    
    optparser.add_option( "--fullCLs", dest="fullCLs",
                    action="store_true", default=False,
                    help="calc limits using the full CLs method; attention number of toys defined in method fullCLs [default = %default]")
    
    optparser.add_option( "--limits3D", dest="limits3D",
                    action="store_true", default=False,
                    help="calc limits using the asymptotic CLs method for the new 3D limit setting procedure ")
    
    optparser.add_option( "--GoodnessOfFit", dest="GoodnessOfFit",
                    action="store_true", default=False,
                    help="calc goodness of fit using the saturated algorithm of combine for the new 3D limit setting procedure ")
    
    optparser.add_option( "--biasTests", dest="biasTests",
                    action="store_true", default=False,
                    help="calc signal injections for the new 3D limit setting procedure ")
    
    optparser.add_option( "--scanSig", dest="scanSignificance",
                    action="store_true", default=False,
                    help="calc signal injections for the new 3D limit setting procedure ")
    
    
    optparser.add_option( "--injectSig", dest="injectSignal",
                    action="store_true", default=False,
                    help="calc S+B fit for injected signal fot the new 3D limit setting procedure ")
    
    optparser.add_option( "--signal", dest="signal",
                    action="store", default="",
                    help="file containing signal strenght over significance -> use this to extract signal strenght value for --injectSignal option")
    
    
    optparser.add_option("-t", "--toys", dest="toys",
                    action="store", default=10,
                    help="calculate toys [default = 10]")
    
    
    (options, args)=optparser.parse_args()
    jobOptions=options.jobOptions
    
    print options.jobOptions
   
    #python injtest.py --scanSig -t 100
    if options.scanSignificance:
        testSignalStrenght("bulkG.cfg",options.toys)
        #waitForBatchJobs("bias.sh")
    
    #python injtest.py --injectSig --toys 200 --signal scanSignalStrength
    if options.injectSignal:
        fitInjectedSignal("bulkG.cfg",options.signal,options.toys)
