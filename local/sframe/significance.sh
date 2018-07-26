#!/bin/bash
## setup CMSSW
	SPAWNPOINT=`pwd`	# save work directory 
	echo ${SPAWNPOINT}
#reader.inDir[i]+" "+workspace+" "+str(mass)+" "+outname+" "+str(toys)+" "+str(sig)+" "+datacard
	# $1 input directory i.e. path to DijetCombineLimitCode
	# $2 name of WORKSPACE
	# $3 mass 
	# $4 name of OUTPUTFILE
	# $5 number of toys
	# $6 expected signal
	# $7 name of DATACARD
#	
	
	source $VO_CMS_SW_DIR/cmsset_default.sh
	#SCRAM_ARCH=slc6_amd64_gcc491
	#cd ${1}../../..
	cd /nfs/dust/cms/user/zoiirene/LimitCode/CMSSW_8_1_0/src/ #job_submission/local/sframe/
        eval `scramv1 runtime -sh`		# set variables for CMSSW
	# print given arguments
	echo "arguments:"
	for a in ${BASH_ARGV[*]} ; do
	    echo -n "$a "
	done

	# go back to work directory
	cd ${SPAWNPOINT}
	
	mkdir graviton_${3}_${6}
	cd graviton_${3}_${6}

	# copy needed files
	cp ${1}/${2} .
	cp ${1}/${7} .
	cp ${1}/CMS_jj_bkg_VV_invM800_de45_${3}_13TeV.root .
#	ls
	
	
	echo "combine -m ${3} -M ProfileLikelihood ${2} --significance --expectSignal=${6} -t ${5} --toysFrequentist --name ${4}"	 
        combine -m ${3} -M ProfileLikelihood ${7} --significance --expectSignal=${6} -t ${5} --toysFrequentist #--run blind --verbose 3 #--rAbsAcc 0.00001 --rRelAcc 0.00001
        #mv  higgs*.root $1/Limits/$4
	#mv higgs*.root ${1}/Output/ #${4}

	echo '### end of job ###'

