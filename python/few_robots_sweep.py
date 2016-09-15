import copy
import random

from carfns import SwitchVTypeFn, changeFasterLaneBuilder
from loopsim import LoopSim
from agent_types import basicHumanParams as humanParams, \
    basicIDMParams as IDMParams, basicACCParams as ACCParams, \
    basicGapFillerParams as gapFillerParams, \
    basicFillGapMidpointParams as fillGapMidpointParams,\
    basicMidpointParams as midpointParams
import config as defaults


# this is the main entry point of this script
if __name__ == "__main__":
    # This sweep demonstrates that our ACC implementation is about as good as
    # IDM in the loop setting
    simStepLength = 0.5
    numLanes = 2
    length = 1000
    simSteps = 500

    nRobotss = [40, 60]
    vtypes = ["idm", "acc", "midpoint", "gapfiller", "fillgapmidpoint"]

    humanParams["count"] = 50
    changeFasterLane = changeFasterLaneBuilder()
    hybridParams = copy.copy(humanParams)
    hybridParams["name"] = "hybrid"

    # for nRobots in range(1, 22, 3):
    for nRobots in nRobotss:
        for vtype in vtypes:
            # Sweep through each type

            # reset the random seed so that the first half of the sim is held constant per nRobots
            if defaults.RANDOM_SEED:
                print "Setting random seed to ", defaults.RANDOM_SEED
                random.seed(defaults.RANDOM_SEED)

            hybridParams["count"] = nRobots
            hybridParams["function"] = SwitchVTypeFn(vtype, 0.5,
                                                     initCarFn=changeFasterLane)

            opts = {
                "paramsList" : [humanParams, IDMParams, ACCParams,
                                gapFillerParams, fillGapMidpointParams,
                                hybridParams, midpointParams],
                "simSteps"   : simSteps,
                "tag"        : "few-%s-sweep" % vtype,
            }

            sim = LoopSim("loopsim", length=length, numLanes=numLanes,
                          simStepLength=simStepLength)

            sim.simulate(opts)
            sim.plot(show=True, save=True)
