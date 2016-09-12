net = $(PROJ).net.xml
.PHONY: net

sumo:	$(net)
	sumo -c $(PROJ).sumo.cfg

gui:	$(net)
	sumo-gui -c $(PROJ).sumo.cfg

net:	$(net)

$(net):
	netconvert --node-files=$(PROJ).nod.xml --edge-files=$(PROJ).edg.xml --output-file=$(PROJ).net.xml

clean:
	rm *.net.xml
