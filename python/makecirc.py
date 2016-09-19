import subprocess
import sys
from lxml import etree
from numpy import pi, sin, cos, linspace

import config as defaults


E = etree.Element

def makexml(name, nsl):
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    ns = {"xsi": xsi}
    attr = {"{%s}noNamespaceSchemaLocation" % xsi: nsl}
    t = E(name, attrib=attr, nsmap=ns)
    return t

def printxml(t, fn):
    etree.ElementTree(t).write(fn, pretty_print=True, encoding='UTF-8', xml_declaration=True) 

def makenet(base, length, lanes, 
        speedLimit=defaults.SPEED_LIMIT, 
        path=""):

    name = "%s-%dm%dl" % (base, length, lanes)

    nodfn = "%s.nod.xml" % name
    edgfn = "%s.edg.xml" % name
    typfn = "%s.typ.xml" % name
    cfgfn = "%s.netccfg" % name
    netfn = "%s.net.xml" % name

    r = length/pi
    edgelen = length/4.

    x = makexml("nodes", "http://sumo.dlr.de/xsd/nodes_file.xsd")
    x.append(E("node", id="bottom",x=repr(0), y=repr(-r)))
    x.append(E("node", id="right", x=repr(r), y=repr(0)))
    x.append(E("node", id="top",   x=repr(0), y=repr(r)))
    x.append(E("node", id="left",  x=repr(-r),y=repr(0)))
    printxml(x, path+nodfn)

    x = makexml("edges", "http://sumo.dlr.de/xsd/edges_file.xsd")
    x.append(E("edge", attrib={"id":"bottom", "from":"bottom","to":"right", "type":"edgeType", 
        "shape": " ".join(["%.2f,%.2f" % ( r*cos(t), r*sin(t) )
                for t in linspace(-pi/2,0,defaults.RESOLUTION)]),
        "length": repr(edgelen)}))
    x.append(E("edge", attrib={"id":"right",  "from":"right", "to":"top",   "type":"edgeType",
        "shape": " ".join(["%.2f,%.2f" % ( r*cos(t), r*sin(t) )
                for t in linspace(0,pi/2,defaults.RESOLUTION)]),
        "length": repr(edgelen)}))
    x.append(E("edge", attrib={"id":"top",    "from":"top",   "to":"left",  "type":"edgeType",
        "shape": " ".join(["%.2f,%.2f" % ( r*cos(t), r*sin(t) )
                for t in linspace(pi/2,pi,defaults.RESOLUTION)]),
        "length": repr(edgelen)}))
    x.append(E("edge", attrib={"id":"left",   "from":"left",  "to":"bottom","type":"edgeType",
        "shape": " ".join(["%.2f,%.2f" % ( r*cos(t), r*sin(t) )
                for t in linspace(pi,3*pi/2,defaults.RESOLUTION)]),
        "length": repr(edgelen)}))
    printxml(x, path+edgfn)

    x = makexml("types", "http://sumo.dlr.de/xsd/types_file.xsd")
    x.append(E("type", id="edgeType",  numLanes=repr(lanes), speed=repr(speedLimit)))
    printxml(x, path+typfn)

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
    printxml(x, path+cfgfn)

    # netconvert -c $(cfg) --output-file=$(net)
    retcode = subprocess.call(
        ['netconvert', "-c", path+cfgfn],
        stdout=sys.stdout, stderr=sys.stderr)

    return path+netfn

def makecirc(name, netfn=None, maxspeed=30, numcars=0, typelist=None, maxt=3000, mint=0, dataprefix="data/"):
    roufn = "%s.rou.xml" % name
    addfn = "%s.add.xml" % name
    cfgfn = "%s.sumo.cfg" % name
    guifn = "%s.gui.cfg" % name

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

    def inputs(name, net=None, rou=None, add=None, gui=None):
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
        if gui is not False:
            if gui is None:
                inp.append(E("gui-settings-file", value="%s.gui.xml" % name))
            else:
                inp.append(E("gui-settings-file", value=gui))
        return inp

    def outputs(name, prefix="data/"):
        t = E("output")
        outs = {"netstate": "dump", 
                "amitran":"output", 
                "lanechange":"output", 
                "emission":"output", }

        for (key, val) in outs.iteritems():
            fn = prefix+"%s.%s.xml" % (name, key)
            t.append(E("%s-%s" % (key, val), value=fn))
            outs[key] = fn
        return t, outs

    rts = {"top": "top left bottom right", 
           "left": "left bottom right top",
           "bottom": "bottom right top left",
           "right": "right top left bottom"}

    add = makexml("additional", "http://sumo.dlr.de/xsd/additional_file.xsd")
    for (rt, edge) in rts.items():
        add.append(E("route", id="route%s"%rt, edges=edge))
    add.append(rerouter("rerouterBottom", "bottom", "routebottom"))
    add.append(rerouter("rerouterTop", "top", "routetop"))
    printxml(add, addfn)

    if numcars > 0:
        routes = makexml("routes", "http://sumo.dlr.de/xsd/routes_file.xsd")
        routes.append(vtype("car", maxspeed))
        for rt in rts:
            routes.append(flow("car%s" % rt, numcars/len(rts), "car", "route%s" % rt, 
                            begin="0", period="1", departPos="free"))
        printxml(routes, roufn)
    elif typelist:
        routes = makexml("routes", "http://sumo.dlr.de/xsd/routes_file.xsd")
        for tp in typelist:
            routes.append(E("vType", id=tp))
        printxml(routes, roufn)
    else:
        roufn=False

    gui = E("viewsettings")
    gui.append(E("scheme", name="real world"))
    printxml(gui, guifn)

    cfg = makexml("configuration", "http://sumo.dlr.de/xsd/sumoConfiguration.xsd")
    cfg.append(inputs(name, net=netfn, add=addfn, rou=roufn, gui=guifn))
    t, outs = outputs(name, prefix=dataprefix)
    cfg.append(t)
    t = E("time")
    t.append(E("begin", value=repr(mint)))
    t.append(E("end", value=repr(maxt)))
    cfg.append(t)

    printxml(cfg, cfgfn)
    return cfgfn, outs

if __name__ == "__main__":
    base = "circtest"
    netfn = makenet(base, length=1000, lanes=3)
    cfgfn, outs = makecirc(base, netfn=netfn, speedlimit=30, typelist=["human", "robot"], maxt=3000)
    print cfgfn
