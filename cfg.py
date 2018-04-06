#!/usr/bin/env python
import os, sys, re
import ROOT
import os
import socket
from array import array

# tubeSpecies = ["ET","ET","ET","ET",             # 0 1 2 3 
# 			   "R878","R878","R878","ET",      #  4 5 6 7	
# 			   "R7725","R7725","R7725","R7725",	# 8 9 10 11
# 			   "R878","R878","R878","R878"]    # 12 13 14 15
tubeSpecies = ["R878"]*32
for et in [8,9,17,24,25]:
	tubeSpecies[et]="ET"
for r7 in [5,22]:
	tubeSpecies[r7]="R7725"
for vet in [18,27,29,20,10,19,30,11,28,31,14,26,21]:
	tubeSpecies[vet]="veto"


#treeDir="/net/cms6/cms6r0/milliqan/milliqanOffline/trees/"
hostname = socket.gethostname()
if "MacBook" in hostname:
	treeDir="/Users/heller/milliqan/trees/"
	webBaseDir="/Users/heller/Sites/milliqan/"
else: 
	treeDir="/net/cms26/cms26r0/milliqan/milliqanOffline/trees/"
	webBaseDir= "/net/cms29/cms29r0/heller/milliqanMeasureCosmic/"

tableHV = {24:[1050,800,800],
		   25:[1150,900,900],
		   28:[1250,1000,1000],
		   30:[1250,1000,1000],
		   31:[1350,1100,1100], 
		   32:[1350,1100,1100],
		   33:[1450,1200,1200],
		   34:[1450,1200,1200],
		   48:[1150,1000,1000],#channel 10 is actually 1100
		   50:[1250,1100,1100], #channel 10 is actually 1000
		   53:[1050,1200,900], # channel 10 actually 1200
		   66:[1500,1450,1500],
		   67:[1550,1450,1550],
		   68:[1650,1450,1650],
		   69:[1700,1450,1700],
		   70:[1600,1450,1600],
		   95:[900,700,700],
		   97:[800,600,600],
		   156:[1600,1450,1600],
		   157:[1500,1425,1450],
		   159:[900,900,900],
		   160:[800,800,800],
		   161:[1050,700,700],
		   171:[1150,600,600],
		   172:[1000,1000,1000],
		   173:[1000,1000,1000],
		   193:[1500,1400,1500],
		   194:[1550,1400,1550],
		   195:[1600,1425,1600],
		   196:[1650,1425,1650],
		   197:[1700,1450,1700],
		   425:[1000,800,800]
		   }

specCosThresh = {425:[700,3200,1500]}
tableCosmicThresh ={
					24:[0.,3500.,1500.,1000.,
						2500.,3000.,2000.,2000.,
						50.,50.,50.,1250.,
						0.,0.,0.,0.],
					25:[1000.,5000.,1500.,2700.,
						6000.,5000.,6000.,6000.,
						500.,900.,800.,4000.,
						4000.,4000.,4000.,4000.],
					28:[1000.,20000.,10000.,8000.,
						8000.,10000.,10000.,10000.,
						200.,2000.,1000.,8000.,
						10000.,10000.,10000.,10000.],
					32:[1000.,50000.,20000.,16000.,
						18000.,20000.,20000.,25000.,
						3000.,6000.,4000.,12000.,
						20000.,20000.,20000.,20000.],
					95:[0.,500.,800.,100.,
						700.,0.,1000.,400.,
						0.,100.,0.,100.,
						0.,0.,0.,0.],
					97:[0.,0.,0.,0.,
						0.,0.,0.,0.,
						0.,0.,0.,0.,
						0.,0.,0.,0.],
					159:[1000.,700.,1200.,500.,
						8000.,9000.,10000.,700.,
						10000.,8000.,5000.,8000.,
						0.,0.,0.,0.],
					160:[0.,100.,0.,0.,
						5000.,5000.,5000.,0.,
						4000.,4000.,1600.,3000.,
						0.,0.,0.,0.],
					161:[1000.,6000.,3500.,3000.,
						2200.,2000.,2200.,4000.,
						2000.,750.,400.,750.,
						0.,0.,0.,0.],
					1597:[1000.,500.,800.,500.,
						8000.,8000.,10000.,700.,
						8000.,8000.,8000.,8000.,
						0.,0.,0.,0.],
					171:[1000.,12000.,12000.,6000.,
						700.,600.,700.,5000.,
						250.,150.,0.,0.,
						0.,0.,0.,0.],
					172:[1000.,3500.,1800.,2000.,
						10000.,12000.,12000.,1500.,
						25000.,20000.,12000.,25000.,
						0.,0.,0.,0.]

						}
tableCosmicThresh[30]=tableCosmicThresh[28]
tableCosmicThresh[31]=tableCosmicThresh[32]


fracSPEThresh8 = {1450:0,1500:0,1550:4,1600:7,1650:9,1700:12}
fracSPEThresh9 = {1450:0,1500:5.5,1550:7.5,1600:10,1650:13,1700:16}
fracSPEThresh10 = {1450:15,1500:15,1550:23,1600:30,1650:40,1700:55}
fracSPEThresh11 = {1450:20,1500:22,1550:25,1600:40,1650:55,1700:75}

#def takeClosest(num,collection):
#   return min(collection,key=lambda x:abs(x-num))

#key = [key for key, value in tableHV.items() if value[0]==1350][0]
def getCosmicThresh(runNum,channel):
	if runNum in tableCosmicThresh:
		return tableCosmicThresh[runNum][channel]
	elif runNum in specCosThresh:
		if "ET" in tubeSpecies[channel]:
			return specCosThresh[runNum][0]
		elif "878" in tubeSpecies[channel]:
			return specCosThresh[runNum][1]
		elif "7725" in tubeSpecies[channel]:
			return specCosThresh[runNum][2]
	else:
		return 500 