#
# Copyright (C) 2016 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#

import sys, os, Ice, traceback, time

from PySide import *
from genericworker import *

ROBOCOMP = ''
try:
	ROBOCOMP = os.environ['ROBOCOMP']
except:
	print '$ROBOCOMP environment variable not set, using the default value /opt/robocomp'
	ROBOCOMP = '/opt/robocomp'
if len(ROBOCOMP)<1:
	print 'genericworker.py: ROBOCOMP environment variable not set! Exiting.'
	sys.exit()


preStr = "-I"+ROBOCOMP+"/interfaces/ --all "+ROBOCOMP+"/interfaces/"
Ice.loadSlice(preStr+"GotoPoint.ice")
from RoboCompGotoPoint import *
Ice.loadSlice(preStr+"DifferentialRobot.ice")
from RoboCompDifferentialRobot import *


import networkx as nx
g = nx.Graph()

import matplotlib.pyplot as plt
#nx.draw_networkx_nodes(g,postitions)


class SpecificWorker(GenericWorker):
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		self.timer.timeout.connect(self.compute)
		self.Period = 1
		self.readGraph()
		self.timer.start(self.Period)
		self.stateMachine = { 0: self.initState,
		  1: self.Objetivos,
		  2: self.Targets,
		  3: 3
		  }
		self.State = 0
		

	def setParams(self, params):
		#try:
		#	par = params["InnerModelPath"]
		#	innermodel_path=par.value
		#	innermodel = InnerModel(innermodel_path)
		#except:
		#	traceback.print_exc()
		#	print "Error reading config params"
		return True

	@QtCore.Slot()
	def compute(self):
		print 'SpecificWorker.compute...'
		#try:
		#	self.differentialrobot_proxy.setSpeedBase(100, 0)
		#except Ice.Exception, e:
		#	traceback.print_exc()
		#	print e
		
		self.stateMachine[self.State]()
		
		
		return True
	      
	def readGraph(self):
	  self.posiciones = {}
	  with open("src/puntos.txt","r") as f:
	    for line in f:
	      l=line.strip("\n").split()
	      if l[0]=="N":
		g.add_node(l[1], x=float(l[2]),y=float(l[3]),name="")
		self.posiciones[l[1]] = (float(l[2]),float(l[3]))
	      else:
		g.add_edge(l[1], l[2])
		
	  #print posiciones
 	  #img = plt.imread("plano.png")
	  #plt.imshow(img, extent = [-12284,25600,-3840,9023])
	  #nx.draw_networkx(g, self.posiciones)
	  #plt.show()
	  
	def nodoCercano(self):
	  bState = TBaseState()
	  bState = self.differentialrobot_proxy.getBaseState()
	  r = (bState.x , bState.z)
	  dist = lambda r,n: (r[0]-n[0])**2+(r[1]-n[1])**2
	  #funcion que devuele el nodo mas cercano al robot
	  return  sorted(list (( n[0] ,dist(n[1],r)) for n in self.posiciones.items() ), key=lambda s: s[1])[0][0]



	def initState(self):
	  print 'SpecificWorker.initState...'
	  self.NodoAct = self.nodoCercano()
	  self.ruta = [66,67]
	  self.State += 1
	def Objetivos(self):
	  if len(self.ruta) == 0:
	    self.State = 0 
	    return None
	  print 'SpecificWorker.Objetivos...'
	  self.NodoAct = self.nodoCercano()
	  self.NodoAct = 71
	  self.camino = nx.shortest_path(g,source=str(self.NodoAct), target=str(self.ruta[0]));
	  self.ruta.pop(0)
	  self.NodoAct = 54
	  print self.ruta
	  print self.camino
	  self.State += 1
	  
	def Targets(self):
	  if len(self.camino) == 0:
	    self.State = 1 
	    return None
	  self.gotopoint_proxy.go("",)
	  return None # llamada a go con valores del nodo.
	  