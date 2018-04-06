#!/usr/bin/env python
import os, sys, re
import ROOT
import os
from array import array
import cfg
import util as u 
import subprocess
#from ROOT import kBlack,kRed,kGreen,kOrange,kBlue,kPink,kYellow,kGray,kMagenta,kSpring,kAzure,kTeal
ROOT.gROOT.SetBatch(ROOT.kTRUE)

if len(sys.argv) < 2:
	sys.exit('Please provide a run number') 

else:
	runNum = str(sys.argv[1])

oneChan=-1
if len(sys.argv)>=3:
	oneChan=int(sys.argv[2])

measureCosmic= ((int(runNum) < 66 or int(runNum)>70)) and runNum != "115" and runNum != "114"
if int(runNum) == 156 or int(runNum) == 157:
	measureCosmic=False
if int(runNum) >= 193: measureCosmic=False
if int(runNum)==425: measureCosmic=True
write=False
bfield=True
tableName = "tables/table_run%s_3p8T.csv"%runNum
if int(runNum)>115:
	bfield = False
	tableName="tables/table_run%s_0T.csv"%runNum


useNarrowRange=True or measureCosmic
vetoOtherChannels=True and not measureCosmic

u.makeDirRecursive("plots/Run"+runNum+"/measure")
# if not os.path.exists("plots/Run"+runNum):
# 	os.mkdir("plots/Run"+runNum)
# if not os.path.exists("plots/Run"+runNum+"/measure"):
# 	os.mkdir("plots/Run"+runNum+"/measure")

u.defineColors()

t=u.getTrees(runNum)
print "N entries:",t.GetEntries()
startTime=t.GetMinimum("event_time_b0")
endTime=t.GetMaximum("event_time_b0")
runDuration = endTime - startTime
#if runNum=="425": runDuration= 9*3600

types = ["ET","R878","R7725"]
variables= ["height","area","duration"]#,"delay","dtstart"]
if measureCosmic: variables=["height","area","duration"]
cosvar=["Pulse height [mV]","Pulse area [pVs]","Pulse duration [ns]"]
nbins= [[[60,60,60],[60,60,60]], #height
		[[30,30,30],[40,40,40],[40,40,40],[40,40,40]], #area
		[[50,50,50]],#duration
		[[50,50,50]],[[50,50,50]]]
minx=  [[[0,0,0],[0,0,0]],#height
		[[0,0,0],[0,0,0],[0,0,0],[0,0,0]],#area
		[[0,0,0]],#duration
		[[0,0,0]],[[0,0,0]]]
maxx=  [[[60,60,60],[300,300,300]], #height
		[[300,300,300],[800,800,800],[1500,1500,1500],[5000,5000,5000]], #area
		[[100,100,100]], #duration
		[[500,500,500]],[[500,500,500]]]


if measureCosmic:
	nbins= [[[40,40,40],[50,50,50],[50,50,50]], #height
		[[30,30,30],[30,30,30],[30,30,30],[30,30,30],[30,30,30],[30,30,30]], #area
		[[50,50,50]]]#duration
	minx=  [[[0,0,0],[0,0,0],[0,0,0]],#height
			[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],#area
			#[[0,0,0],[0,0,0],[1000,1000,1000],[4000,5000,4000],[2000,2000,2000],[0,0,0]],#area
			[[0,0,0]]]#duration
	maxx=  [[[200,200,200],[500,500,500],[1260,1260,1260]], #height
			[[8000,5000,5000],[20000,10000,10000],[50000,30000,20000],[180000,90000,120000],[60000,60000,60000],[4000,2500,2500]], #area
			#[[8000,5000,5000],[20000,10000,10000],[50000,30000,30000],[180000,100000,120000],[60000,60000,60000],[4000,2500,2500]], #area
			[[250,250,250]]] #duration


##species summary plots
# for itube,tubetype in enumerate(types):
# 	for ivar,var in enumerate(variables):
# 		hists=[]
# 		legs=[]
# 		for i,spec in enumerate(cfg.tubeSpecies):			
# 			if spec != tubetype: continue
# 			if i==0 or i==13: continue
# 			leg = cosvar[ivar]+", Ch "+str(i)
# 			title = ";Pulse area [pVs];Events"
# 			if "height" in var: title = ";Pulse height [mV];Events"	
# 			if "duration" in var: title = ";Pulse Duration [ns];Events"	
# 			name = "Run "+runNum+" "+leg
# 			selection = "chan=="+str(i)

# 			hist = u.getHist(t,name,title,selection,var,nbins[ivar][itube],minx[ivar][itube],maxx[ivar][itube]) 
# 			u.cosmeticTH1(hist,i)

# 			hists.append(hist)
# 			legs.append(leg)


# 		filename = "plots/Run%s/Run%s_SPE_%s_%s.pdf" % (runNum, runNum, var, tubetype)
# 		u.printTH1s(hists,legs,filename)


##per channel look
## plot first pulse, afterpulses, and cleaned afterpulses
selNames =["First pulses","Afterpulses","Cleaned afterpulses"]
sels= ["ipulse==0","ipulse>0","ipulse>0&&quiet&&delay>20"] ## have to define cosmic selection channel by channel in loop

if measureCosmic:
	selNames = ["All pulses","Vertical cosmics","Cosmics without saturation"]
	sels= ["ipulse==0","ipulse==0&&vert","ipulse==0&&(vert)&&height<1245"]



colIndices= [6,11,9] ## define colors based on channel map

additionalSels=[ [["","",""]] for x in range(32)]

R7725HV= 1600
if int(runNum) in cfg.tableHV: 
	R7725HV = cfg.tableHV[int(runNum)][2]

if not measureCosmic:
	#additionalSels[5].append(["duration<30","duration<30&&height<15","height<15"])
	additionalSels[8].append(["","height>%0.1f"%cfg.fracSPEThresh8[R7725HV],"height>%0.1f"%cfg.fracSPEThresh8[R7725HV]])
	additionalSels[9].append(["","height>%0.1f"%cfg.fracSPEThresh9[R7725HV],"height>%0.1f"%cfg.fracSPEThresh9[R7725HV]])
	additionalSels[10].append(["","height>%0.1f"%cfg.fracSPEThresh10[R7725HV],"height>%0.1f"%cfg.fracSPEThresh10[R7725HV]])
	additionalSels[11].append(["","height>%0.1f"%cfg.fracSPEThresh11[R7725HV],"height>%0.1f"%cfg.fracSPEThresh11[R7725HV]])

measureZoom= [0 for x in range(16)]
if not measureCosmic:
	measureZoom[10]=2
	measureZoom[11]=2
	if R7725HV>1600:
		measureZoom[10]=3
		measureZoom[11]=3

if int(runNum) == 24:
	measureZoom[11] = 0
	measureZoom[9] = 0
	measureZoom[8] = 5
	measureZoom[6] = 1
	measureZoom[5] = 1
	measureZoom[4] = 1
	measureZoom[1] = 1

if int(runNum) == 25:
	measureZoom[11] = 2
	measureZoom[8] = 5
	measureZoom[7] = 2
	measureZoom[6] = 4
	measureZoom[5] = 4
	measureZoom[4] = 4
	measureZoom[3] = 1
	measureZoom[1] = 3

if int(runNum) == 28:
	measureZoom[11] = 3
	measureZoom[10] = 4
	measureZoom[9] = 1
	measureZoom[8] = 1
	measureZoom[7] = 3
	measureZoom[6] = 3
	measureZoom[5] = 3
	measureZoom[4] = 4
	measureZoom[3] = 2
	measureZoom[1] = 3

if int(runNum) == 32:
	measureZoom[1] = 4
	measureZoom[3] = 4


if int(runNum) == 95:
	measureZoom[9] = 5
	measureZoom[6] = 1
	measureZoom[3]=5

if int(runNum) == 97:
	measureZoom[1]=5
	measureZoom[3]=5
	measureZoom[7]=5

if int(runNum) == 156:
	measureZoom[8]=2
	measureZoom[9]=1
	measureZoom[10]=2
	measureZoom[11]=2
if int(runNum) == 157:
	measureZoom[8]=2

if int(runNum) == 159:
	measureZoom[1]=0
	measureZoom[3]=5
	measureZoom[4]=4
	measureZoom[5]=4
	measureZoom[6]=4
	measureZoom[8]=3
	measureZoom[9]=4
	measureZoom[10]=2
	measureZoom[11]=4

if int(runNum) == 160:
	measureZoom[1]=5
	measureZoom[2]=5
	measureZoom[3]=5
	measureZoom[4]=2
	measureZoom[5]=2
	measureZoom[6]=2
	measureZoom[7]=5
	measureZoom[8]=4
	measureZoom[9]=2
	measureZoom[11]=2

if int(runNum) == 161:
	measureZoom[1]=1
	measureZoom[3]=1
	measureZoom[4]=1
	measureZoom[5]=1
	measureZoom[6]=1
	measureZoom[7]=1
	measureZoom[8]=2
	measureZoom[9]=1


if int(runNum) == 171:
	measureZoom[1]=4
	measureZoom[2]=2
	measureZoom[3]=2
	measureZoom[5]=0
	measureZoom[6]=5
	measureZoom[7]=4
	measureZoom[9]=5
	measureZoom[10]=5
	measureZoom[11]=5

if int(runNum) == 172:
	measureZoom[1]=1
	measureZoom[2]=1
	measureZoom[3]=1
	measureZoom[4]=4
	measureZoom[5]=4
	measureZoom[6]=3
	measureZoom[7]=1
	measureZoom[8]=3
	measureZoom[9]=3
	measureZoom[10]=4
	measureZoom[11]=3

if int(runNum) == 193:
	measureZoom[8]=2
	measureZoom[9]=1
	measureZoom[10]=1
	measureZoom[11]=1
if int(runNum) == 194:
	measureZoom[8]=2
	measureZoom[9]=1
	measureZoom[10]=2
	measureZoom[11]=2
if int(runNum) == 195:
	measureZoom[8]=2
	measureZoom[9]=1
	measureZoom[10]=2
	measureZoom[11]=2

if int(runNum) == 196:
	measureZoom[1]=1
	measureZoom[2]=1
	measureZoom[7]=1
	measureZoom[8]=3
	measureZoom[9]=1
	measureZoom[10]=3
	measureZoom[11]=3

if int(runNum) == 197:
	measureZoom[1]=1
	measureZoom[2]=1
	measureZoom[7]=1
	measureZoom[8]=3
	measureZoom[9]=1
	measureZoom[10]=3
	measureZoom[11]=3

measureSels =[0 for x in range(16)]
if not measureCosmic:
	measureSels[8]=1
	measureSels[9]=1
	measureSels[10]=1
	measureSels[11]=1

#topChannels= [2,3,6,7,10,11]
slices = [[0,24,8],[1,25,9],[6,16,12],[7,17,13],[2,22,4],[3,23,5]]

#if write:
#	table = open("tableSPE.csv","a")
for ichan in range(32):
	if oneChan!=-1 and ichan!=oneChan: continue
	#if measureCosmic and ichan>=12: continue
	if ichan==15: continue
	if cfg.tubeSpecies[ichan] =="veto": continue
	#if ichan!=6: continue
	#if ichan<8 or ichan>11: continue
	for ivar,var in enumerate(variables):
		#if measureCosmic and ivar!=1: continue

		title = ("Run %i, Channel %i, %i V;" % (int(runNum),ichan,cfg.tableHV[int(runNum)][u.getTubeType(ichan)])) + cosvar[ivar]+";Pulses" 

		for iad,addSel in enumerate(additionalSels[ichan]):
			for izoom,zoom in enumerate(nbins[ivar]):
				measureIteration=False
				if write and var == "area" and measureZoom[ichan]==izoom and measureSels[ichan]==iad: measureIteration = True
				#if izoom!=3: continue
				hists=[]
				legs=[]
				for isel,sel in enumerate(sels):
					thissel = sel
					if "vert" in thissel:
						for sli in slices:
							if ichan in sli:
								vertSel=""
								for ics in sli:
									if ics != ichan:
										if vertSel != "": vertSel=vertSel+"&&"
										vertSel = vertSel + "Sum$(area>%.f&&chan==%i)>0" % (cfg.getCosmicThresh(int(runNum),ics),ics)
								thissel= thissel.replace("vert",vertSel)
								break


					selection = "chan==%i&&%s" % (ichan,thissel)
					vetoSel=""
					if vetoOtherChannels:
						for iveto in range(16):
							if iveto != ichan and iveto != 13:
								vetoSel = vetoSel + "&&max_%i<5" % iveto

					if addSel[ivar] != "": selection = selection + "&&" +addSel[ivar] 
					#print selection
					itube = u.getTubeType(ichan)

					name = "Run%s_chan%i_%s_%s_zoom%i" % (runNum,ichan,var,u.cutToString(selection),izoom+1)
					hist = u.getHist(t,name,title,selection+vetoSel,var,nbins[ivar][izoom][itube],minx[ivar][izoom][itube],maxx[ivar][izoom][itube]) 

					u.cosmeticTH1(hist,colIndices[isel])
					hists.append(hist)
					legs.append(selNames[isel])

				filename = "plots/Run%s/Run%s_SPE_%s_%s_zoom%i.pdf" % (runNum, runNum, var, u.cutToString(selection),izoom+1)
				if measureCosmic: filename = filename.replace("SPE","cosmic")
				if not useNarrowRange: filename = filename.replace(".pdf","fullrange.pdf")
				if vetoOtherChannels: filename = filename.replace(".pdf","_vetoOtherChan.pdf")
				filename= filename.replace("_heightlt1245","").replace("chan","ch").replace("Sumarea","SumA").replace("ipulse","ip")

				#if int(runNum)==28 and izoom+1<3 and ichan != 8 and ichan !=9: continue
				thresh=0
				#print "Measure iteration is ",measureIteration
				if measureCosmic: 
					thresh=cfg.getCosmicThresh(int(runNum),ichan)
				mean,err,rate = u.printTH1s(hists,legs,filename,runDuration,"area" in var,measureCosmic,False,thresh,useNarrowRange,True)
				if int(runNum)==70: u.printTH1s(hists,legs,filename,runDuration,False,measureCosmic,False,thresh,useNarrowRange,True)
				#or int(runNum)==172
				if measureIteration:
					u.copyPlot(runNum,ichan,filename,bfield,True,measureCosmic)
				
				u.copyPlot(runNum,ichan,filename,bfield,False,measureCosmic) 
				
				HV=0
				if "ET" in cfg.tubeSpecies[ichan]: HV = 1600
				if "878" in cfg.tubeSpecies[ichan]: HV = 1450
				if "7725" in cfg.tubeSpecies[ichan]: HV = 1600
				if int(runNum) in cfg.tableHV: 
					if "ET" in cfg.tubeSpecies[ichan]:HV = cfg.tableHV[int(runNum)][0]
					if "878" in cfg.tubeSpecies[ichan]: HV = cfg.tableHV[int(runNum)][1]
					if "7725" in cfg.tubeSpecies[ichan]: HV = cfg.tableHV[int(runNum)][2]


				if measureIteration:
					u.replaceTableRow(tableName,runNum,ichan,HV,mean,err,rate)
					

					#table.write(",".join([runNum,str(ichan),str(HV),str(round(mean,1)),str(round(err,2)),str(round(rate,4))+"\n"]))
				#	measureFilename = filename.replace("Run%s/"%runNum,"Run%s/measure/"%runNum)
				#	subprocess.call(["cp", filename, measureFilename])
				#	subprocess.call(["cp", filename.replace(".pdf","_log.pdf"), measureFilename.replace(".pdf","_log.pdf")])










