#! /usr/bin/python
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
        #print self.model
        #print self.opt
        #print self.inDir
        #print self.outDir
        #print self.mass
        #print self.masses


class XMLcreator:
    inputDir = ''  
    inputFile =''
    tmpJobDir =''
    typeName =''
    version =''
    def __init__(self,filename):
        jobOptionsFile=open(filename, 'r')
        command2=""
        for i in [o for o in jobOptionsFile.readlines()]:
            if ("#E" + "nd") in i : break
            command2+=i
        jobOptionsFile.close()
        exec command2
        self.userItems = userItems
        self.dataSets = dataSets
        self.path2xml= path2xml
        self.path2tmp = path2tmp
        self.outDir = outDir
        self.jobName =jobName
        self.cycleName = cycleName
        self.nEventsMax = nEventsMax
        self.nProcesses = nProcesses
        self.nFiles = nFiles
        self.hCPU = hCPU
        self.hVMEM = hVMEM
        self.postFix=postFix
        self.loadPacks = loadPacks
        self.loadLibs = loadLibs
        self.storage = storage
        self.path2ExoDir = path2ExoDir
        
        
    def makeXML(self,name,inputFile):
        a = inputFile.split('"')
        print a
        l = a[1].split('/')
        infilename =''
        for s in a:
            #print s
            if s.find('storage')==1: 
                infilename+=l[-1]+'"'
                continue
            infilename +=s+'"' 
        tmp = infilename.split('\n')
        self.inputFile = l[-1]
        s1,s2 = l[-1].split('.')
        for i in range(0,len(l)-1):
            self.tmpJobDir +=l[i]+"/"
        print name
        name1,name2,name3 = name.split('.')    
        self.xml = open(self.path2tmp+name,'w')
        self.xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.xml.write('<!DOCTYPE JobConfiguration PUBLIC "" "JobConfig.dtd">\n')
        self.xml.write('<JobConfiguration JobName="'+self.jobName+'" OutputLevel="INFO">\n')
        for lib in self.loadLibs:
            self.xml.write('<Library Name="'+lib +'" />\n') 
        for pack in self.loadPacks:
            self.xml.write('<Package Name="'+pack+'" />\n')
        self.xml.write('<Cycle Name="'+self.cycleName+'" OutputDirectory="" PostFix="'+self.postFix+'" ProofServer="lite" ProofWorkDir="" RunMode="LOCAL" TargetLumi="1.0">\n')
        self.xml.write('<InputData Lumi="0.0" NEventsMax="'+str(self.nEventsMax)+'" NEventsSkip="0" SkipValid="False" Version="'+s1+'" Type="'+name1 +'">\n')
        self.xml.write(tmp[0]+"\n")  
        self.xml.write('<InputTree Name="ntuplizer/tree" /> \n  <OutputTree Name="tree" /> \n </InputData> \n')
        self.xml.write('<UserConfig>\n')      
        for i in self.userItems:
             self.xml.write(' <Item Name="'+i[0]+'" Value="'+i[1]+'" />\n') 
        self.xml.write('</UserConfig> \n </Cycle> \n </JobConfiguration>')
        self.inputDir = self.storage+self.tmpJobDir
        self.typeName = name1
        self.version = s1
        self.xml.close()

 
 
def writeJDL(arguments,mem,time,name):
    #jobs = JDLCreator('condocker')  #run jobs on condocker cloude site
    jobs = JDLCreator('condocker') # matthias schnepf told me i don't need this after all! (23.01.18)
    jobs.wall_time = time
    jobs.memory = mem 
    jobs.requirements = "(TARGET.ProvidesCPU) && (TARGET.ProvidesEkpResources)"
    jobs.accounting_group = "cms.top"
    ##################################
    ## submit job to set up CMSSW 
    ##################################
    #jobs.SetExecutable("job_setup.sh")  # set job script
    #jobs.SetArguments(' ')              # set arguments
    #jobs.SetFolder('../setup/')         # set subfolder !!! you have to copy your job file into the folder


    ##################################
    # submit job to run combine
    ##################################
    jobs.SetExecutable(name)  # set job script
    #jobs.SetFolder('/usr/users/dschaefer/job_submission/local/sframe')  # set subfolder !!! you have to copy your job file into the folder
    jobs.SetArguments(arguments)              # write an JDL file and create folder f            # set arguments
    jobs.WriteJDL() # write an JDL file and create folder for log files


        
def calcSframeTrees(joboptions):
    parser = XMLcreator(jobOptions)
    counter=0
    arguments=[]
    Njobs=0
    haddList=[]
    finalName=[]
    
    # arg1 = name of .xml file for this job 
    # arg2 = ordner to copy input file from
    # arg3 = temoporary dir to copy input file into
    # arg4 = name of input file to be copied
    # arg5 = name of output OutputDirectory
    #
    tmplist=[]
    tmpTypeName="tmp"
    for dset in parser.dataSets:
        filedset = open(parser.path2xml+dset[1][0],'r')
        for line in filedset:
            if line.find("<!--")!=-1:
                continue
            if line =="\n":
                continue
            counter+=1
            parser.makeXML(dset[0]+parser.postFix+"_"+str(counter)+".xml",line)
            #print parser.inputDir
            arguments.append(dset[0]+parser.postFix+"_"+str(counter)+".xml"+" "+parser.storage+" "+parser.tmpJobDir+" "+parser.inputFile+" "+parser.outDir+ " "+parser.path2ExoDir+" "+parser.path2tmp)
            print parser.tmpJobDir
            
            parser.tmpJobDir =''
            print tmpTypeName
            if parser.typeName.find(tmpTypeName)==-1:
                if len(tmplist)!=0:
                    haddList.append(tmplist)
                tmplist=[]
                finalName.append(parser.outDir+parser.cycleName+"."+parser.typeName+parser.postFix+".root")
            tmplist.append(parser.outDir+parser.cycleName+"."+parser.typeName+"."+parser.version+parser.postFix+".root")
            tmpTypeName = parser.typeName
    haddList.append(tmplist)
    #finalName.append(parser.outDir+parser.cycleName+"."+parser.typeName+parser.postFix+".root")
    Njobs = counter
    time.sleep(10)
    writeJDL(arguments,3000,30*60,"job_calc.sh")
    command = "condor_submit job_calc.jdl"
    process = subprocess.Popen(command,shell=True)
    
    waitForBatchJobs("job_calc")
    
    
    i=0
    ts=""
    for s in finalName:
        haddString =""
        ts = ""
        for h in haddList[i]:
            ts += h+" "
        i+=1
        haddString = "hadd -f "+s + " "+ts
        print haddList
        print haddString 
        os.system(haddString)
    if not options.saveTmp:
        tmp = ""
        for l in haddList:
            for h in l:
                print "rm "+h
                tmp+=h+ " "
                #os.system("rm -f "+tmp)
            #print haddList
    

def waitForBatchJobs(nameJobFile):
    timeCheck = 10 #delay for process check
    while (True):
        time.sleep(timeCheck)
        proc = subprocess.Popen(["(condor_q dschaefer | grep "+nameJobFile+" )"], stdout=subprocess.PIPE, shell=True)
        (query, err) = proc.communicate()
        print "program output:", query
        if query.find("dschaefer")==-1:
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
    

def doInterpolation(config):
    print "starting interpolation jobs"
    reader = ConfigReader(config)
    arguments =[]
    for i in range(0,len(reader.model)):
        print "use model " +reader.model[i]
        outfilename = reader.model[i]+"_VV"
        if "Qstar" in reader.model[i]:
            outfilename = reader.model[i]+"_qV"
        if "Data" in reader.model[i]:
            outfilename = "ReRecoData_VVdijet"
        if "Data" in reader.model[i] and "q" in reader.model[i]:
            outfilename = "ReRecoData_qVdijet"
        if "QCD" in reader.model[i] and "madgraph" in reader.model[i]:
            outfilename = "QCD_madgraph_pythia8"
        if "QCD" in reader.model[i] and "pythia" in reader.model[i]:
            outfilename = "QCD_pythia8"
        if "QCD" in reader.model[i] and "herwig" in reader.model[i]:
            outfilename = "QCD_herwig"
        if "QCD" in reader.model[i] and "Summer16" in reader.inDir[i]:
            outfilename += "_summer16"
            
        
        if "SB" in reader.model[i]:
            outfilename+="_SB"
        outfilename+=".root"
        for j in range(0,len(reader.masses[i])):
            print "use masses" + reader.masses[i][j]
            arguments.append(reader.model[i]+" "+reader.masses[i][j]+" "+reader.opt[i]+" "+reader.inDir[i]+" "+reader.outDir[i]+" "+outfilename)
    writeJDL(arguments,30,10*60,"interpolate.sh")
    command = "condor_submit interpolate.jdl"
    process = subprocess.Popen(command,shell=True)
    waitForBatchJobs("interpolate.sh")
    
    arguments=[]
    for i in range(0,len(reader.model)):
        for m in range(0,int((int(reader.massmax[i])-int(reader.massmin[i]))/100.)):
            #print m*100+int(reader.massmin[i])
            arguments.append(reader.model[i]+" "+str(m*100+int(reader.massmin[i]))+" "+reader.outDir[i])
    writeJDL(arguments,30,10*60,"interpolate2.sh")
    command = "condor_submit interpolate2.jdl"
    process = subprocess.Popen(command,shell=True)
    waitForBatchJobs("interpolate2.sh")
    samplemin=1
    samplemax=10
    for i in range(0,len(reader.model)):
        suffix = "VV"
        if "Zprime" in reader.model[i]:
            samplemin=7
            samplemax=8
        if "Wprime" in reader.model[i]:
            samplemin=8
            samplemax=9
        if "BulkWW" in reader.model[i]:
            samplemin=5
            samplemax=6
        if "BulkZZ" in reader.model[i]:
            samplemin=6
            samplemax=7
        if "QstarQW" in reader.model[i]:
            samplemin=3
            samplemax=4
            suffix="qV"
        if "QstarQZ" in reader.model[i]:
            samplemin=4
            samplemax=5
            suffix="qV"
        # mini tree produce takes all masses! might not work if not all masses are interpolated!    
        command2 = 'root -b -q "/usr/users/dschaefer/CMSSW_7_4_7/src/DijetCombineLimitCode/MiniTreeSignalProducer'+suffix+'13TeV.C('+str(samplemin)+','+str(samplemax)+')"'
        print command2
        os.system(command2)
    
    return 0


def makeDatacards(config):
    reader = ConfigReader(config)
    arguments=[]
    chan =1
    sample=2
    for i in range(0,len(reader.model)):
        if "prime" in reader.model[i]:
            sample =2
        if "Bulk" in reader.model[i]:
            sample = 4
            
        if "q" in reader.model[i] or "Q" in reader.model[i]:
            sample = 6
        if "RS" in reader.model[i]:
            sample =0
        if "qV" in reader.channel[i]:
            chan= 2
        for m in range(0,int((int(reader.massmax[i])-int(reader.massmin[i]))/100.)):
            #print m*100+int(reader.massmin[i])
            arguments.append(str(m*100+int(reader.massmin[i]))+" "+str(sample)+" "+str(chan)+" "+reader.opt[i]+" "+reader.channel[i]+ " "+reader.inDir[i]+" "+reader.model[i]+" /usr/users/dschaefer/SFrame_setup/ExoDiBosonAnalysis/forSystematics/")
    writeJDL(arguments,150,10*60,"datacards.sh")
    print arguments
    command = "condor_submit datacards.jdl"
    process = subprocess.Popen(command,shell=True)
    waitForBatchJobs("datacards.sh")
    
    
def calcLimits(config):
        # $1 input directory i.e. path to DijetCombineLimitCode
	# $2 name of datacard
	# $3 name of workspace
	# $4 name of background workspace
	# $5 mass of the resonance
	# $6 output directory
	# $7 name of output file
    reader = ConfigReader(config)
    arguments=[]
    for i in range(0,len(reader.model)):
        for c in reader.channels[i]:
            #for p in reader.purities[i]:
                for m in range(0,int((int(reader.massmax[i])-int(reader.massmin[i]))/100.)):
                    mass = str(m*100+int(reader.massmin[i]))
                    if "new" in c:
                        print " datacards must be combined: start CombineDatacards.py"
                        if reader.opt[i] =="meep":
                            os.system("python /usr/users/dschaefer/CMSSW_7_4_7/src/DijetCombineLimitCode/Limits/CombineDatacards.py --batch --signal "+reader.model[i]+" --mass "+mass )
                        else:
                            os.system("python /usr/users/dschaefer/CMSSW_7_4_7/src/DijetCombineLimitCode/Limits/CombineDatacards.py --batch --signal "+reader.opt[i]+reader.model[i]+" --mass "+mass )
                    datacard = "CMS_jj_"+reader.opt[i]+reader.model[i]+"_"+mass+"_13TeV_CMS_jj_"+c+".txt"
                    workspace = "CMS_jj_"+reader.opt[i]+reader.model[i]+"_"+mass+"_13TeV.root"
                    bkgworkspace = "CMS_jj_bkg_"+reader.channel[i]+reader.opt[i]+"_13TeV.root"
                    outputname = "CMS_jj_"+mass+"_"+reader.opt[i]+reader.model[i]+"_13TeV_CMS_jj_"+c+"_asymptoticCLs_new.root"
                    if reader.opt[i] == "meep":
                        datacard = "CMS_jj_"+reader.model[i]+"_"+mass+"_13TeV_CMS_jj_"+c+".txt"
                        workspace = "CMS_jj_"+reader.model[i]+"_"+mass+"_13TeV.root"
                        bkgworkspace = "CMS_jj_bkg_"+reader.channel[i]+"_13TeV.root"
                        outputname = "CMS_jj_"+mass+"_"+reader.model[i]+"_13TeV_CMS_jj_"+c+"_asymptoticCLs_new.root"
                    if reader.model[i] =="HVTtriplett":
                        workspace = "CMS_jj_*_"+mass+"_13TeV.root"
                    arguments.append(reader.inDir[i]+" "+datacard+" "+workspace+" "+bkgworkspace+" "+mass+" "+reader.outDir[i]+" "+outputname)
    writeJDL(arguments,500,10*60,"limits.sh")
    command = "condor_submit limits.jdl"
    process = subprocess.Popen(command,shell=True)
    waitForBatchJobs("limits.sh")
    
    
    
def calcLimits3D(config):
    reader = ConfigReader(config)
    arguments=[]
    for i in range(0,len(reader.model)):
            for p in reader.purities[i]:
                for m in range(0,int((int(reader.massmax[i])-int(reader.massmin[i]))/100.)):
                    mass = str(m*100+int(reader.massmin[i]))
                    if reader.opt[i] == "3D":
                        #workspace = "workspace_JJ_"+p+"_13TeV.root"
                        #workspace = "workspace_test_HPHP_13TeV.root"
                        #workspace = "workspace_pythia_nominal.root"
                        #workspace = "workspace_pythia_tails3D.root"
                        workspace = "workspace_pythia.root"
                        #workspace = "workspace_tau21DDT.root"
                        #outname="AsympLimit_"+reader.model[i]+"_13TeV_CMS_jj_"+p+"_M"+mass+".root"
                        outname="pythia_tau21DDT_"+reader.model[i]+"_13TeV_CMS_jj_"+p+"_M"+mass+".root"
                    arguments.append(reader.inDir[i]+" "+workspace+" "+mass+" "+outname)

    writeJDL(arguments,900,30*60,"limits3D.sh")
    command = "condor_submit limits3D.jdl"
    process = subprocess.Popen(command,shell=True)
    waitForBatchJobs("limits3D.sh")
 
 
def testSignalStrenght(config,toys):
    reader = ConfigReader(config)
    arguments=[]
    for i in range(0,len(reader.model)):
            for p in reader.purities[i]:
                for m in range(0,int((int(reader.massmax[i])-int(reader.massmin[i]))/100.)):
                    expSig=[]
                    f = rt.TFile("/home/dschaefer/Limits3DFit/pythia/pythia_tau21DDT_WprimeWZ_obs.root","READ") # attention root file here must be calculated from workspace below!!!
#                    f = rt.TFile("/home/dschaefer/Limits3DFit/pythia/pythia_tau21DDT_WprimeWZ_obs.root","READ") # attention root file here must be calculated from workspace below!!!
                    mass = str(m*100+int(reader.massmin[i]))
                    limit=f.Get("limit")
                    lim=0
                    for event in limit:
                        #print event.mh
                        if int(event.mh)!=int(mass):
                            continue
                        if event.quantileExpected>0.974 and event.quantileExpected<0.976:            
                            lim=event.limit
                            print lim
                    for counter in range(0,10):
                        expSig.append(round(0.0+counter*lim*2.5/10.,3))
                    print expSig
                    for sig in expSig:
                        if reader.opt[i] == "3D":
                            workspace = "workspace_pythia.root"
                            outname="biasTest_r"+str(float(sig))+"_pythia_tau21DDT_"+reader.model[i]+"_13TeV_CMS_jj_"+p+"_M"+mass+".root"
                        arguments.append(reader.inDir[i]+" "+workspace+" "+mass+" "+outname+" "+str(toys)+" "+str(sig))

    writeJDL(arguments,1500,30*60,"bias.sh")
    command = "condor_submit bias.jdl"
    process = subprocess.Popen(command,shell=True)
    waitForBatchJobs("bias.sh")



def fitInjectedSignal(config,signal,toys):
    reader = ConfigReader(config)
    arguments=[]
    for i in range(0,len(reader.model)):
            for p in reader.purities[i]:
                for m in range(0,int((int(reader.massmax[i])-int(reader.massmin[i]))/100.)):
                    f = rt.TFile(signal,"READ")
                    mass = str(m*100+int(reader.massmin[i]))
                    g = f.Get(mass)
                    sig = g.Eval(3)  # inject signal with 3 sigma significance!
                    if reader.opt[i] == "3D":
                            workspace = "workspace_pythia.root"
                            outname="biasTest_MaxLikelihood_r"+str(int(sig))+"_pythia_tau21DDT_"+reader.model[i]+"_13TeV_CMS_jj_"+p+"_M"+mass+".root"
                    arguments.append(reader.inDir[i]+" "+workspace+" "+mass+" "+outname+" "+str(toys)+" "+str(sig))

    writeJDL(arguments,1500,30*60,"bias2.sh")
    command = "condor_submit bias2.jdl"
    process = subprocess.Popen(command,shell=True)
    waitForBatchJobs("bias2.sh")
 
 
 
 
 
def GoodnessOfFit(config,toys):
    reader = ConfigReader(config)
    arguments=[]
    for i in range(0,len(reader.model)):
            for p in reader.purities[i]:
                for m in range(0,int((int(reader.massmax[i])-int(reader.massmin[i]))/100.)):
                    mass = str(m*100+int(reader.massmin[i]))
                    if reader.opt[i] == "3D":
                        #workspace = "workspace_JJ_"+p+"_13TeV.root"
                        #workspace = "workspace_test_HPHP_13TeV.root"
                        workspace = "workspace_WprimeWZ_pythia_HPHP.root"
                        #workspace = "workspace_pythia_nominal_dataherwig.root"
                        for t in range(0,int(toys)):
                            outname="GoodnessOfFit_pythia_"+reader.model[i]+"_13TeV_CMS_jj_"+p+"_M"+mass+"_toy_"+str(int(t))+".root"
                            arguments.append(reader.inDir[i]+" "+workspace+" "+mass+" "+outname+" 1")
                        if toys == 0:
                            outname="GoodnessOfFit_pythia_"+reader.model[i]+"_13TeV_CMS_jj_"+p+"_M"+mass+".root"
                            arguments.append(reader.inDir[i]+" "+workspace+" "+mass+" "+outname)
                            

    writeJDL(arguments,900,30*60,"GoodnessOfFit.sh")
    command = "condor_submit GoodnessOfFit.jdl"
    process = subprocess.Popen(command,shell=True)
    waitForBatchJobs("GoodnessOfFit.sh")
   




    
    

def calcfullCLs(config):
    reader = ConfigReader(config)
    arguments=[]
    print "attention: for this to work the asymptotic limits must already exist!!!"
    for i in range(0,len(reader.model)):
        for c in reader.channels[i]:
            #for p in reader.purities[i]:
                for m in range(0,int((int(reader.massmax[i])-int(reader.massmin[i]))/100.)):
                    mass = str(m*100+int(reader.massmin[i]))
                    signal = reader.model[i]
                    if reader.opt[i]!="meep":
                        signal = reader.opt[i]+reader.model[i]
                    datacard = "CMS_jj_"+signal+"_"+mass+"_13TeV_CMS_jj_"+c+".txt"
                    workspace = "CMS_jj_"+signal+"_"+mass+"_13TeV.root"
                    bkgworkspace = "CMS_jj_bkg_"+signal+"_13TeV.root"
                    outputnameAsymptotic = "CMS_jj_"+mass+"_"+signal+"_13TeV_CMS_jj_"+c+"_asymptoticCLs_new.root"
                    rf = rt.TFile(reader.outDir[i]+outputnameAsymptotic ,"READ")
                    tree = rf.Get("limit")
                    asymlimits={}
                    for quantile in tree:
                        asymlimits[int(tree.quantileExpected*100)] = tree.limit*10
                    print reader.model[i]+" "+c+" "+str(mass)
                    print asymlimits
                    # make list of signal strenghts for toys: use n toys between 0.8 and 1.2 *asymp 2 sigma error band 
                    toys=[]
                    n = 50
                    for frac in range(1,n):
                        s = round(asymlimits[2]*0.8 +  (asymlimits[97]*1.2 - asymlimits[2]*0.8)/frac,4)
                        toys.append(s)
                    print toys
        # 1 = directory of DijetCombineLimitCode
        # 2 = name of datacard
        # 3 = name of signal workspace
        # 4 = name of background workspace
        # 5 = mass
        # 6 = output directory
        # 7 = signal strenght for toy
        # 8 = model
                    for toy in toys:
                        arguments.append(reader.inDir[i]+" "+datacard+" "+workspace+" "+bkgworkspace+" "+str(mass)+" "+reader.outDir[i]+" "+str(toy)+""+reader.model[i])
        writeJDL(arguments,500,40*60,"toys.sh")
        command = "condor_submit toys.jdl"
        process = subprocess.Popen(command,shell=True)
        waitForBatchJobs("toys.sh")
        
        #command00 = "cd "+reader.outDir[i]
        #command0  = "hadd -f all_merged.root higgsCombine*"+str(mass)+"*.root"
        #command1  = "combine datacard.txt -M HybridNew --freq --grid=all_merged.root --expectedFromGrid 0.5 --mass "+str(mass)+" >> "+reader.model[i]+"_"+str(mass)+".txt"
        #os.system(command00)
        #os.system(command0)
        #os.system(command1)
    
    return 1

        
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
    if options.sframe:
        calcSframeTrees(jobOptions)
    
    if options.interpolate:
        doInterpolation("interpolation.cfg")
        
    if options.workspaces:
        makeDatacards("datacards.cfg")
    
    if options.combine:
        calcLimits("datacards.cfg")
        
    if options.ALL:
        calcSframeTrees(jobOptions)
        doInterpolation("interpolation.cfg")
        makeDatacards("datacards.cfg")
        calcLimits("datacards.cfg")
        
    if options.dataPlusLim:
        makeDatacards("datacards.cfg")
        calcLimits("datacards.cfg")
    
    if options.fullCLs:
        print "calculate full CLs limits "
        calcfullCLs("datacards.cfg")
    
    if options.limits3D:
        print "calculate limits for new 3D framework"
        calcLimits3D("datacards.cfg")
    
    
    if options.GoodnessOfFit:
        print "calculate goodness of fit for new 3D framework"
        GoodnessOfFit("datacards.cfg",options.toys)
   
    if options.scanSignificance:
        testSignalStrenght("datacards.cfg",options.toys)
        #waitForBatchJobs("bias.sh")
    
    #py batchsubmission.py --injectSig --toys 200 --signal /home/dschaefer/Limits3DFit/biasTest/scanSignalStrength.root
    if options.injectSignal:
        fitInjectedSignal("datacards.cfg",options.signal,options.toys)
