from lxml import etree


E = etree.Element

def makexml(name, nsl):
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    ns = {"xsi": xsi}
    attr = {"{%s}noNamespaceSchemaLocation" % xsi: nsl}
    t = E(name, attrib=attr, nsmap=ns)
    return t

def printxml(t, fn):
    etree.ElementTree(t).write(fn, pretty_print=True, encoding='UTF-8', xml_declaration=True) 

def makenet(base, length, lanes, maxSpeed=40):
    import subprocess
    import sys

    name = "%s-%dm-%dl" % (base, length, lanes)

    nodfn = "%s.nod.xml" % name
    edgfn = "%s.edg.xml" % name
    typfn = "%s.typ.xml" % name
    cfgfn = "%s.netccfg" % name
    netfn = "%s.net.xml" % name
    l4 = length/4.

    x = makexml("nodes", "http://sumo.dlr.de/xsd/nodes_file.xsd")
    x.append(E("node", id="bottom-left", x=repr(0), y=repr(0)))
    x.append(E("node", id="bottom-right", x=repr(l4), y=repr(0)))
    x.append(E("node", id="top-right", x=repr(l4), y=repr(l4)))
    x.append(E("node", id="top-left", x=repr(0), y=repr(l4)))
    printxml(x, nodfn)

    x = makexml("edges", "http://sumo.dlr.de/xsd/edges_file.xsd")
    x.append(E("edge", attrib={"id":"bottom", "from":"bottom-left",  "to":"bottom-right", "type":"edgeType"}))
    x.append(E("edge", attrib={"id":"right",  "from":"bottom-right", "to":"top-right",    "type":"edgeType"}))
    x.append(E("edge", attrib={"id":"top",    "from":"top-right",    "to":"top-left",     "type":"edgeType"}))
    x.append(E("edge", attrib={"id":"left",   "from":"top-left",     "to":"bottom-left",  "type":"edgeType"}))
    printxml(x, edgfn)

    x = makexml("types", "http://sumo.dlr.de/xsd/types_file.xsd")
    x.append(E("type", id="edgeType",  numLanes=repr(lanes), speed=repr(maxSpeed)))
    printxml(x, typfn)

    x = makexml("configuration", "http://sumo.dlr.de/xsd/netconvertConfiguration.xsd")
    t = E("input")
    t.append(E("node-files", value=nodfn))
    t.append(E("edge-files", value=edgfn))
    t.append(E("type-files", value=typfn))
    x.append(t)
    t = E("output")
    t.append(E("output-file", value=netfn))
    x.append(t)
    t = E("processing")
    t.append(E("no-internal-links", value="true"))
    t.append(E("no-turnarounds", value="true"))
    x.append(t)
    printxml(x, cfgfn)

    # netconvert -c $(cfg) --output-file=$(net)
    retcode = subprocess.call(
        ['netconvert', "-c", cfgfn],
        stdout=sys.stdout, stderr=sys.stderr)

    return netfn

def makecirc(name, netfn=None, maxspeed=30, numcars=100, maxt=3000, mint=0, dataprefix="data/"):
    roufn = "%s.rou.xml" % name
    addfn = "%s.add.xml" % name
    cfgfn = "%s.sumo.cfg" % name

    def rerouter(name, frm, to):
        t = E("rerouter", id=name, edges=frm)
        i = E("interval", begin="0", end="100000")
        i.append(E("routeProbReroute", id=to))
        t.append(i)
        return t

    def vtype(name, maxSpeed=30, accel=1.5, decel=4.5, length=5, **kwargs):
        return E("vType", accel=repr(accel), decel=repr(decel), id=name, length=repr(length), maxSpeed=repr(maxSpeed), **kwargs)

    def flow(name, number, vtype, route, **kwargs):
        return E("flow", id=name, number=repr(number), route=route, type=vtype, **kwargs)

    def inputs(name, net=None, rou=None, add=None):
        inp = E("input")
        if net is not False:
            if net is None:
                inp.append(E("net-file", value="%s.net.xml" % name))
            else:
                inp.append(E("net-file", value=net))
        if rou is not False:
            if rou is None:
                inp.append(E("route-files", value="%s.rou.xml" % name))
            else:
                inp.append(E("route-files", value=rou))
        if add is not False:
            if add is None:
                inp.append(E("additional-files", value="%s.add.xml" % name))
            else:
                inp.append(E("additional-files", value=add))
        return inp

    def outputs(name, prefix="data/"):
        inp = E("output")
        inp.append(E("netstate-dump", value=prefix+"%s.netstate.xml" % name))
        inp.append(E("amitran-output", value=prefix+"%s.amitran.xml" % name))
        inp.append(E("lanechange-output", value=prefix+"%s.lanechange.xml" % name))
        return inp

    rts = {"Top": "top left bottom right", 
           "Left": "top left bottom right",
           "Bottom": "bottom right top left",
           "Right": "bottom right top left"}

    add = makexml("additional", "http://sumo.dlr.de/xsd/additional_file.xsd")
    for (rt, edge) in rts.items():
        add.append(E("route", id="route%s"%rt, edges=edge))
    add.append(rerouter("rerouterBottom", "bottom", "routeRight"))
    add.append(rerouter("rerouterTop", "top", "routeLeft"))
    printxml(add, addfn)

    routes = makexml("routes", "http://sumo.dlr.de/xsd/routes_file.xsd")
    routes.append(vtype("car", maxspeed))
    for rt in rts:
        routes.append(flow("car%s" % rt, numcars/len(rts), "car", "route%s" % rt, 
                        begin="0", period="1", departPos="free"))
    printxml(routes, roufn)

    cfg = makexml("configuration", "http://sumo.dlr.de/xsd/sumoConfiguration.xsd")
    cfg.append(inputs(name, net=netfn, add=addfn, rou=roufn))
    cfg.append(outputs(name, prefix=dataprefix))
    t = E("time")
    t.append(E("begin", value=repr(mint)))
    t.append(E("end", value=repr(maxt)))
    cfg.append(t)

    printxml(cfg, cfgfn)
    return cfgfn

if __name__ == "__main__":
    base = "circtest"
    netfn = makenet(base, length=1000, lanes=3)
    cfgfn = makecirc(base, netfn=netfn, maxspeed=30, numcars=100, maxt=3000)
    print cfgfn
