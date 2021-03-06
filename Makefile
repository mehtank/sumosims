typ = $(PROJ).typ.xml
net = $(PROJ).net.xml
cfg = $(PROJ).netccfg
rou = $(PROJ).rou.xml
nod = $(PROJ).nod.xml
edg = $(PROJ).edg.xml
.PHONY: net clean sumo gui

sumo:	$(net)
	sumo -c $(PROJ).sumo.cfg --no-step-log

gui:	$(net)
	sumo-gui -c $(PROJ).sumo.cfg

net:	$(net)

$(net):	$(nod) $(edg) $(typ) $(cfg)
ifeq ("$(wildcard $(cfg))","") 
	netconvert --node-files=$(nod) --edge-files=$(edg) --output-file=$(net)
else
	netconvert -c $(cfg) --output-file=$(net)
endif

clean:
	rm *.net.xml
