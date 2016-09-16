import random
import itertools

import config as defaults
from loopsim import LoopSim
from agent_types import basicHumanParams as humanParams, \
    basicIDMParams as IDMParams, basicACCParams as ACCParams, \
    basicGapFillerParams as gapFillerParams, \
    basicFillGapMidpointParams as fillGapMidpointParams, \
    basicMidpointParams as midpointParams


if __name__ == "__main__":
    numLanes = 1

    sim = LoopSim("loopsim", length=230, numLanes=numLanes, simStepLength=0.5)

    vTypeParams = humanParams
    vTypeParams["laneSpread"] = True
    vTypeParams["tau"] = 0.5
    vTypeParams["speedDev"] = 0.0
    vTypeParams["speedFactor"] = 1

    mParams = midpointParams
    mParams["laneSpread"] = True

    aParams = ACCParams
    aParams["laneSpread"] = True

    for sigma in (0.5, 0.9):
        vTypeParams["sigma"] = sigma

        vTypeParams["count"] = 22
        if defaults.RANDOM_SEED:
            print "Setting random seed to ", defaults.RANDOM_SEED
            random.seed(defaults.RANDOM_SEED)

        for run in range(3):
            opts = {
                "paramsList" : [vTypeParams],
                "simSteps"   : 500,
                "tag"        : "Sugiyama-sigma=%03f-run=%d" % (sigma, run),
            }

            sim.simulate(opts)
            sim.plot(show=False, save=True, speedRange=(0,30), fuelRange=(0, 40)).close("all")

        for numRobots, rParams in itertools.product(\
                (1, 5, 11, 22), \
                (mParams, aParams)):

            vTypeParams["count"] = (22-numRobots) 
            rParams["count"] = numRobots 

            if defaults.RANDOM_SEED:
                print ">>> Setting random seed to ", defaults.RANDOM_SEED
                random.seed(defaults.RANDOM_SEED)

            for run in range(3):
                opts = {
                    "paramsList" : [vTypeParams, rParams],
                    "simSteps"   : 500,
                    "tag"        : "Sugiyama-sigma=%03f-run=%d" % (sigma, run),
                }

                print "***"
                print "sigma =", sigma, "numRobots = ", numRobots, 
                print "robot type =", rParams["name"], "run = ", run
                print "***"
                sim.simulate(opts)
                sim.plot(show=False, save=True, speedRange=(0,30), fuelRange=(0, 40)).close("all")
