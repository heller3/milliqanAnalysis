#!/usr/bin/env python
import os, sys, re
import ROOT
import os
from array import array
import math
import glob
import cfg
import util as u 
import subprocess

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetLabelFont(42,"xyz")
ROOT.gStyle.SetLabelSize(0.05,"xyz")
#ROOT.gStyle.SetTitleFont(42)
ROOT.gStyle.SetTitleFont(42,"xyz")
ROOT.gStyle.SetTitleFont(42,"t")
#ROOT.gStyle.SetTitleSize(0.05)
ROOT.gStyle.SetTitleSize(0.05,"xyz")
ROOT.gStyle.SetTitleSize(0.05,"t")
ROOT.gStyle.SetPadBottomMargin(0.14)
ROOT.gStyle.SetPadLeftMargin(0.14)
ROOT.gStyle.SetTitleOffset(1,'y')
ROOT.gStyle.SetLegendTextSize(0.04)
ROOT.gStyle.SetGridStyle(3)
ROOT.gStyle.SetGridColor(13)
#ROOT.gStyle.SetOptStat(1001101)

cosmicOnly=False

def defineColors():
	reds =[255./255.,31./255.,235./255.,111./255.,219./255.,151./255.,185./255.,194./255.,127./255.,98./255.,211./255.,69./255.,220./255.,72./255.,225./255.,145./255.,233./255.,125./255.,147./255.,110./255.,209./255.,44]
	greens=[255./255.,30./255.,205./255.,48./255.,106./255.,206./255.,32./255.,188./255.,128./255.,166./255.,134./255.,120./255.,132./255.,56./255.,161./255.,39./255.,232./255.,23./255.,173./255.,53./255.,45./255.,54]
	blues=[255./255.,30./255.,62./255.,139./255.,41./255.,230./255.,54./255.,130./255.,129./255.,71./255.,178./255.,179./255.,101./255.,150./255.,49./255.,139./255.,87./255.,22./255.,60./255.,21./255.,39./255.,23]

	global palette 
	global colors
	palette = []
	colors = []

	for icolor in range(len(reds)):
		palette.append(ROOT.TColor(2000+icolor,reds[icolor],greens[icolor],blues[icolor]))
		colors.append(2000+icolor)

	colors[9] = 419 #kGreen+3
	colors[2] = 2009
	colors[3] = 2013
	colors[12]= 2017



def main(chan):
	graphs_0,funcs_0 = getGraphs(False)
	graphs_3p8,funcs_3p8 = getGraphs(True)

	c = ROOT.TCanvas("csum%i"%chan,"")
	c.SetGrid()
	c.SetLogy()
	c.SetLogx()
	leg = ROOT.TLegend(0.53,0.14,0.9,0.39)
	mg = ROOT.TMultiGraph()
	mg.Add(graphs_0[chan])
	# graphs_3p8[chan].SetLineColor(6)
	# graphs_3p8[chan].SetMarkerColor(6)
	# funcs_3p8[chan].SetLineColor(6)
	mg.Add(graphs_3p8[chan])

	mg.Draw("AEPZ")
	funcs_0[chan].Draw("same")
	funcs_3p8[chan].Draw("same")

	filename = "fieldComp_chan%i.pdf"%chan
	c.Print(filename)

def getGraphs(bfield):
	tableName = "tables/table_run*_3p8T.csv"
	if not bfield:
		tableName="tables/table_run*_0T.csv"
	defineColors()
	v_run=[ [] for x in range(16)]
	v_SPE=[ [] for x in range(16)]
	v_SPE_err=[ [] for x in range(16)]
	v_HV=[ [] for x in range(16)]
	v_HV_err = [ [] for x in range(16)]
	v_log_SPE=[ [] for x in range(16)]
	v_log_SPE_err=[ [] for x in range(16)]
	v_log_HV=[ [] for x in range(16)]
	v_log_HV_err = [ [] for x in range(16)]

	tableList = glob.glob(tableName)
	for table in tableList:
		with open(table) as SPElist:
			for line in SPElist:
				run = int(line.split(",")[0])
				chan = int(line.split(",")[1])
				HV= int(line.split(",")[2])
				spe= float(line.split(",")[3])
				spe_err= float(line.split(",")[4])


				if cosmicOnly and math.log(HV) > 7.14: continue
				if not cosmicOnly and chan==3 and HV ==800: continue
				if (chan==1 or chan==3 or chan ==7) and HV==1500: continue
				if chan==1 and HV== 1350: continue
				if run==32: continue
				if chan==11 and bfield and HV < 800: continue
				if chan==9 and bfield and HV<= 600: continue
				if (chan==4 or chan==5 or chan==6) and (HV==1400 or HV==1425 or HV==1000): continue
				if chan==8 and run==172:continue
				v_run[chan].append(run)
				v_SPE[chan].append(spe)
				fracErr=0.15
				v_SPE_err[chan].append(1.5*fracErr*spe)
				if spe>0:
					v_log_SPE[chan].append(math.log(spe))
					logerr = 0.5*(math.log(spe*(1+fracErr))-math.log(spe*(1-fracErr)))
					v_log_SPE_err[chan].append(logerr)
				##hack to show 5 measurements of R878s at 1450.
				#if cfg.tubeSpecies[chan] != "R878":
				v_HV[chan].append(HV)
				v_HV_err[chan].append(1)
				if spe>0:
					v_log_HV[chan].append(math.log(HV))
					v_log_HV_err[chan].append(math.log(2))
		#	else:
		#		v_HV[chan].append(HV)
				#v_HV[chan].append(1440+5*len(v_HV[chan]))


	singleChanMode=False 
	thisChan=0



	graphs=[]
	loggraphs=[]
	shiftgraphs=[]
	funcs=[]
	shiftfuncs=[]
	mgraphs=[]
	legs=[]

	title =";High voltage [V];Pulse area [pVs]"
	for i in range(12):			
		if i==0 or i==13 or i==2 or (i==8 and bfield) or (i==10 and bfield) or i>11: 
			graphs.append(ROOT.TGraphErrors())
			loggraphs.append(ROOT.TGraphErrors())
			shiftgraphs.append(ROOT.TGraphErrors())
			funcs.append(ROOT.TF1())
			shiftfuncs.append(ROOT.TF1())
			mgraphs.append(ROOT.TMultiGraph())
			legs.append("")
			continue
		
		thiscolor=colors[i]
		if bfield: thiscolor=colors[6]

		legname = "Channel "+str(i)

		name = "channel"+str(i)

		title = legname+";High voltage [V];Pulse area [pVs]"
		print name
		print v_HV[i]
		print v_SPE[i]
		graph = ROOT.TGraphErrors(len(v_HV[i]),array("d",v_HV[i]),array("d",v_SPE[i]),array("d",v_HV_err[i]),array("d",v_SPE_err[i]))
		loggraph = ROOT.TGraphErrors(len(v_log_HV[i]),array("d",v_log_HV[i]),array("d",v_log_SPE[i]),array("d",v_log_HV_err[i]),array("d",v_log_SPE_err[i]))
		graph.SetLineColor(thiscolor)
		graph.SetLineStyle(2)
		graph.SetMarkerColor(thiscolor)
		graph.SetMarkerSize(1)
		graph.SetMarkerStyle(20)
		graph.SetLineWidth(2)	
		graph.SetTitle(title)

			# print v_log_SPE[i]
			# print v_log_HV[i]

		f1 =  ROOT.TF1("f1_%i"%i,"[0]+x*[1]+(x<7.14)*[2]",0,8,3)
		f1.SetParameter(0,-85)
		f1.SetParameter(1,13)
		f1.SetParameter(2,8)
		if chan<4 or chan==7:
			f1.SetParameter(0,-65)
			f1.SetParameter(1,9.5)
			f1.SetParameter(2,9)

		if not cosmicOnly: loggraph.Fit(f1,"R")
		f2 =  ROOT.TF1("f2_%i"%i,"exp([0]+log(x)*[1]+(log(x)<7.14)*[2])",0,2000,3)
		f2.SetParameter(0,f1.GetParameter(0))
		f2.SetParameter(1,f1.GetParameter(1))
		f2.SetParameter(2,f1.GetParameter(2))
		f2.SetLineColor(thiscolor)

		f3 =  ROOT.TF1("f3_%i"%i,"exp([0]+log(x)*[1])",0,2000,2)
		f3.SetParameter(0,f1.GetParameter(0))
		f3.SetParameter(1,f1.GetParameter(1))
		f3.SetLineColor(thiscolor)
		f3.SetLineStyle(9)


		v_SPE_shift =[]
		v_SPE_shift_err =[]
		v_HV_shift =[]
		v_HV_shift_err=[]

		for ip in range(len(v_HV[i])):
			v_HV_shift.append(v_HV[i][ip])
			v_HV_shift_err.append(v_HV_err[i][ip])

			if (math.log(v_HV[i][ip])<7.14):
				v_SPE_shift.append(v_SPE[i][ip]/math.exp(f1.GetParameter(2)))
				v_SPE_shift_err.append(0.1*v_SPE[i][ip]/math.exp(f1.GetParameter(2)))
				### include all of the non-shifted cosmics again as well, to get correct plotting range
				# v_HV_shift.append(v_HV[i][ip])
				# v_HV_shift_err.append(v_HV_err[i][ip])
				# v_SPE_shift.append(v_SPE[i][ip])
				# v_SPE_shift_err.append(v_SPE_err[i][ip])
			else: 
				v_SPE_shift.append(v_SPE[i][ip])
				v_SPE_shift_err.append(v_SPE_err[i][ip])

		shiftgraph = ROOT.TGraphErrors(len(v_HV_shift),array("d",v_HV_shift),array("d",v_SPE_shift),array("d",v_HV_shift_err),array("d",v_SPE_shift_err))
		shiftgraph.SetTitle(title)
		shiftgraph.SetLineColor(thiscolor)
		shiftgraph.SetLineStyle(2)
		shiftgraph.SetMarkerColor(thiscolor)
		shiftgraph.SetMarkerSize(1)
		shiftgraph.SetMarkerStyle(24)
		shiftgraphs.append(shiftgraph)
		graphs.append(graph)
		loggraphs.append(loggraph)
		funcs.append(f2)
		shiftfuncs.append(f3)

		canTitle = "B-field off"
		if bfield: canTitle = "B-field on"
		c = ROOT.TCanvas("c%i"%i,canTitle)
		c.SetGrid()
		c.SetLogy()
		c.SetLogx()
		if bfield:
			bstring = "3p8"
		else:
			bstring = "0"
		mg = ROOT.TMultiGraph("mg_chan%i_%s"%(i,bstring),"")
		mg.Add(shiftgraph)
		mg.Add(graph)
		mg.SetTitle(canTitle+";High voltage [V];Pulse area [pVs]")
		mgraphs.append(mg)

	return mgraphs,shiftfuncs


if __name__ == "__main__":
	main(int(sys.argv[1]))

