import copy

from carfns import randomChangeLaneFn, ACCFnBuilder, changeFasterLaneBuilder,\
    MidpointFnBuilder, SwitchVTypeFn, FillGapFnBuilder, FillGapMidpointFnBuilder
import config as defaults

# changeFasterLane = changeFasterLaneBuilder()
changeFasterLane = changeFasterLaneBuilder(likelihood_mult=0.5, speedThreshold=2)
basicHumanParams = {
    "name"        : "human",
    "shape"       : "passenger",
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

basicRobotParams = {
    "name"        : "robot",
    "shape"       : "evehicle",
    "count"       :  0,
    "maxSpeed"    :  defaults.MAX_SPEED,
    "accel"       :   4,
    "decel"       :   6,
    "laneSpread"  : 0,
    "tau"         : 0.5,
}

# In the literature, the IDM model is used as adaptive cruise control
basicIDMParams = copy.copy(basicRobotParams)
basicIDMParams["name"] = "idm"
basicIDMParams["carFollowModel"] = "IDM"

basicACCParams = copy.copy(basicRobotParams)
basicACCParams["name"] = "acc"
basicACCParams["function"] = ACCFnBuilder(follow_sec=1.0,
                                          max_speed=defaults.MAX_SPEED,
                                          gain=0.1, beta=0.9)

basicGapFillerParams = copy.copy(basicRobotParams)
basicGapFillerParams["name"] = "gapfiller"
basicGapFillerParams["function"] = FillGapFnBuilder(duration=250)

basicFillGapMidpointParams = copy.copy(basicRobotParams)
basicFillGapMidpointParams["name"] = "fillgapmidpoint"
basicFillGapMidpointParams["function"] = \
    FillGapMidpointFnBuilder(max_speed=40, gain=0.1, beta=0.9, duration=250,
                             bias=1.0, ratio=0.25, gap_threshold=10)

basicMidpointParams = copy.copy(basicRobotParams)
basicMidpointParams["name"] = "midpoint"
basicMidpointParams["function"] = MidpointFnBuilder(max_speed=40, gain=0.1,
                                                    beta=0.9, duration=250,
                                                    bias=1.0, ratio=0.25)
