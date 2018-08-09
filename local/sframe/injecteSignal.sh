#!/bin/bash
## setup CMSSW
	SPAWNPOINT=`pwd`	# save work directory 
	echo ${SPAWNPOINT}


#reader.inDir[i]+" "+workspace+" "+str(mass)+" "+outname+" "+str(toys)+" "+str(sig)+" "+datacard+" "+config                                                                                                            
        # $1 input directory i.e. path to DijetCombineLimitCode                                                                                                                                             
        # $2 name of WORKSPACE                                                                                                                                                                              
        # $3 mass                                                                                                                                                                                           
        # $4 name of OUTPUTFILE                                                                                                                                                                             
        # $5 number of toys                                                                                                                                                                                 
        # $6 expected signal                                                                                                                                                                                
        # $7 name of DATACARD                                                                                                                                                                               
        # $8 radion vs graviton


	source $VO_CMS_SW_DIR/cmsset_default.sh
#	SCRAM_ARCH=slc6_amd64_gcc491
	#cd ${1}../../..
	cd /nfs/dust/cms/user/zoiirene/LimitCode/CMSSW_8_1_0/src/
        eval `scramv1 runtime -sh`		# set variables for CMSSW
	# print given arguments
	echo "arguments:"
	for a in ${BASH_ARGV[*]} ; do
	    echo -n "$a "
	done

	# go back to work directory
	cd ${SPAWNPOINT}
	mkdir ${8}_${3}_${6}
        cd ${8}_${3}_${6}
	# copy needed files
	cp ../scanSignalStrength_${3}.root .
	cp ../CMS_jj_bkg_VV_invM800_de45_${3}_13TeV.root .
	cp ../CMS_jj_${8}_invM800_de45_${3}_13TeV.root .
	cp ../CMS_jj_${8}_invM800_de45_${3}_13TeV__invMass_combined.txt .
 
	echo "combine -m ${3} -M MaxLikelihoodFit ${7} --significance --expectSignal=${6} -t ${5} --rMax 100"	 
        combine -m ${3} -M MaxLikelihoodFit ${7} --significance --expectSignal=${6} -t ${5} --rMax 100 #--run blind --verbose 3 #--rAbsAcc 0.00001 --rRelAcc 0.00001
	#mv  higgs*.root $1/Limits/$4
#	mv higgs*.root /portal/ekpbms2/home/dschaefer/Limits3DFit/biasTest/${4}

	echo '### end of job ###'

