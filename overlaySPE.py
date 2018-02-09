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

runs = ["159","1597"]#["156","195"] #["70","156"]#
	
runNames= ["v6","v7"]#["3.8 T","0 T"]#
	
vetoOtherChannels=True

runString = "Run"+runs[0]+"_"+runs[1]
if not os.path.exists("plots/"+runString):
	os.mkdir("plots/"+runString)
if not os.path.exists("plots/"+runString+"/measure"):
	os.mkdir("plots/"+runString+"/measure")

u.defineColors()
trees=[]
runDurations=[]
for irun in runs:
	t=u.getTrees(irun)
	trees.append(t)
	print "N entries:",t.GetEntries()
	startTime=t.GetMinimum("event_time")
	endTime=t.GetMaximum("event_time")
	runDuration = endTime - startTime
	runDurations.append(runDuration)

types = ["ET","R878","R7725"]
variables= ["height","area","duration"]
cosvar=["Pulse height [mV]","Pulse area [pVs]","Pulse duration [ns]"]
nbins= [[[60,60,60],[60,60,60]], #height
		[[40,40,40],[40,40,40],[40,40,40]], #area
		[[50,50,50]]]#duration
minx=  [[[0,0,0],[0,0,0]],#height
		[[0,0,0],[0,0,0],[0,0,0]],#area
		[[0,0,0]]]#duration
maxx=  [[[60,60,60],[300,300,300]], #height
		[[300,300,300],[2000,2000,2000],[5000,5000,5000]], #area
		[[100,100,100]]] #duration


colIndices= [6,11,9]

sels=["ipulse==0","ipulse>0&&quiet&&delay>20"]

for ichan in range(16):
	if ichan==0 or ichan==13: continue
	#if ichan<8 or ichan>11: continue
	for ivar,var in enumerate(variables):

		title = ("Channel %i;" % ichan) + cosvar[ivar]+";% of Pulses" 

		for izoom,zoom in enumerate(nbins[ivar]):
			#if izoom!=3: continue
			
			for isel,sel in enumerate(sels):
				hists=[]
				legs=[]
				thissel = sel

				selection = "chan==%i&&%s" % (ichan,thissel)
				vetoSel=""
				if vetoOtherChannels:
					for iveto in range(16):
						if iveto != ichan and iveto != 13:
							vetoSel = vetoSel + "&&max_%i<5" % iveto

				#if addSel[ivar] != "": selection = selection + "&&" +addSel[ivar] 
				#print selection
				itube = u.getTubeType(ichan)

				for irun,run in enumerate(runs):
					name = "Run%s_chan%i_%s_%s_zoom%i" % (run,ichan,var,u.cutToString(selection),izoom+1)
					hist = u.getHist(trees[irun],name,title,selection+vetoSel,var,nbins[ivar][izoom][itube],minx[ivar][izoom][itube],maxx[ivar][izoom][itube]) 
					integral = hist.Integral(1,hist.GetNbinsX())
					if integral>0: hist.Scale(100./integral)
					u.cosmeticTH1(hist,colIndices[irun])
					hists.append(hist)
					legs.append(runNames[irun])

				filename = "plots/%s/Runs%s_%s_SPEcompare_%s_%s_zoom%i.pdf" % (runString,runs[0],runs[1], var, u.cutToString(selection),izoom+1)
				
				if vetoOtherChannels: filename = filename.replace(".pdf","_vetoOtherChan.pdf")

				thresh=0
				mean,err,rate = u.printTH1s(hists,legs,filename,runDuration,False,False,False,thresh,False)
