import random
import copy

import config as defaults
from loopsim import LoopSim
from agent_types import basicHumanParams as humanParams, \
    basicIDMParams as IDMParams, basicACCParams as ACCParams, \
    basicGapFillerParams as gapFillerParams, \
    basicFillGapMidpointParams as fillGapMidpointParams, \
    basicMidpointParams as midpointParams


if __name__ == "__main__":
    globalLaneSpread = 0

    hParams = humanParams
    hParams["laneSpread"] = globalLaneSpread
    hParams["tau"] = 2
    hParams["speedDev"] = 0.2
    hParams["speedFactor"] = 1.1
    hParams["minGap"] = 1

    hParams1 = copy.copy(humanParams)
    hParams1["name"] = "human1"
    hParams1["laneSpread"] = 1
    hParams1["tau"] = 2
    hParams1["speedDev"] = 0.4
    hParams1["speedFactor"] = 1.2
    hParams1["count"] = 0

    mParams = midpointParams
    mParams["laneSpread"] = globalLaneSpread
    # mParams["tau"] = 0.1

    gParams = fillGapMidpointParams
    gParams["laneSpread"] = globalLaneSpread
    # gParams["tau"] = 0.1

    aParams = ACCParams
    aParams["laneSpread"] = globalLaneSpread
    # aParams["tau"] = 0.1

    ###############
    # Option ranges
    ###############

    numLanes = 1
    totVehicles = 11

    '''
    sigmaValues = [0.5, 0.9]
    numRobotsValues = [1,5,11,22]
    numRuns = 3
    robotTypes = (mParams, gParams, aParams)
    '''

    sigmaValues = [0.5]
    numRobotsValues = [0, 1]
    numRuns = 1
    robotTypes = [gParams]

    # WARNING SUMO can't really handle more than 2 fps, probably due to limitations of underlying car following models
    # TODO(cathywu) develop our own high resolution car following models?
    fps = 2
    simStepLength = 1./fps
    simTime = 100
    simSteps = int(simTime/simStepLength)
    sim = LoopSim("loopsim", length=230, numLanes=numLanes, simStepLength=simStepLength)

    for sigma in sigmaValues:
        for numRobots in numRobotsValues:
            for rParams in robotTypes:
                hParams["sigma"] = sigma
                hParams["count"] = (totVehicles-numRobots)
                rParams["count"] = numRobots

                if defaults.RANDOM_SEED:
                    print ">>> Setting random seed to ", defaults.RANDOM_SEED
                    random.seed(defaults.RANDOM_SEED)

                for run in range(numRuns):
                    opts = {
                        "paramsList" : [hParams, hParams1, rParams],
                        "simSteps"   : simSteps,
                        "tag"        : "Sugiyama-sigma=%03f-run=%d" % (sigma, run),
                    }

                    print "***"
                    print "sigma =", sigma, "numRobots = ", numRobots, 
                    print "robot type =", rParams["name"], "run = ", run
                    print "***"
                    speedRange = (0, 30)
                    sim.simulate(opts, sumo='sumo', speedRange=speedRange, sublane=False)
                    # sim.simulate(opts, sumo='sumo-gui', speedRange=speedRange, sublane=False)
                    sim.plot(show=False, save=True, speedRange=speedRange).close("all")
                if numRobots == 0:
                    break
