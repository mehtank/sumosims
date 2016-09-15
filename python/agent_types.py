from carfns import randomChangeLaneFn, ACCFnBuilder, changeFasterLaneBuilder, MidpointFnBuilder, SwitchVTypeFn
import config as defaults

changeFasterLane = changeFasterLaneBuilder()
# changeFasterLane = changeFasterLaneBuilder(likelihood=1, speedThreshold=2)
basicHumanParams = {
    "name"        : "human",
    "count"       :  0,
    "maxSpeed"    :  defaults.MAX_SPEED,
    "accel"       :   2.6,
    "decel"       :   4.5,
    # "function"    : randomChangeLaneFn,
    "function"  : changeFasterLane,
    "laneSpread"  : 0,
    "speedFactor" : 1.1,
    "speedDev"    : 0.5,
    "sigma"       : 0.75,
    "tau"         : 3, # http://www.croberts.com/respon.htm
    # "laneChangeModel": 'LC2013',
}

basicACCParams = {
    "name"        : "acc",
    "count"       :  0,
    "maxSpeed"    :  defaults.MAX_SPEED,
    "accel"       :   4,
    "decel"       :   6,
    # "function"    : MidpointFnBuilder(max_speed=40, gain=0.1, beta=0.9, duration=250, bias=1.0, ratio=0.25),
    "function"    : ACCFnBuilder(follow_sec=1.0, max_speed=defaults.MAX_SPEED, gain=0.1, beta=0.9),
    "laneSpread"  : 0,
    "tau"         : 0.5,
}

basicRobotParams = {
    "name"        : "robot",
    "count"       :  0,
    "maxSpeed"    :  defaults.MAX_SPEED,
    "accel"       :   4,
    "decel"       :   6,
    "function"    : MidpointFnBuilder(max_speed=40, gain=0.1, beta=0.9, duration=250, bias=1.0, ratio=0.25),
    "laneSpread"  : 0,
    "tau"         : 0.5,
}
