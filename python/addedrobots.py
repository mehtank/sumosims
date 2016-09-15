# Make sure $SUMO_HOME/tools is in $PYTHONPATH
import traci


# this is the main entry point of this script
if __name__ == "__main__":
    import random
    import copy

    from loopsim import LoopSim
    from carfns import randomChangeLaneFn, ACCFnBuilder, changeFasterLaneBuilder, MidpointFnBuilder, SwitchFn
    import config as defaults


    humanParams = {
            "name"        : "human",
            "count"       :  30,
            "maxSpeed"    :  40,
            "accel"       :   2.6,
            "decel"       :   4.5,
            # "function"    : randomChangeLaneFn,
            # "function"    : changeFasterLaneBuilder(),
            "laneSpread"  : 0,
            "speedFactor" : 1.0,
            "speedDev"    : 0.1,
            "sigma"       : 0.5,
            "tau"         : 3, # http://www.croberts.com/respon.htm
            "laneChangeModel": 'LC2013',
            }

    robotParams = {
        "name"        : "robot",
        "maxSpeed"    :  40,
        "accel"       :   2.6,
        "decel"       :   4.5,
        "function"    : ACCFnBuilder(follow_sec=1.0, max_speed=40, gain=0.1, beta=0.9),
        "laneSpread"  : 0,
        "tau"         : 0.5,
    }

    random.seed(23434)

    for i in range(15):
        hp = copy.copy(humanParams)
        rp = copy.copy(robotParams)
        rp["count"] = i

        opts = {
                "paramsList" : [hp, rp],
                "simSteps"   : 500,
                "tag"        : "+%02drobots" % i
                }

        defaults.SIM_STEP_LENGTH = 0.5
        sim = LoopSim("loopsim", length=1000, numLanes=2)
        sim.simulate(opts)
        sim.plot(show=False, save=True)
