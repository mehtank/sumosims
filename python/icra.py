import random

import config as defaults
from loopsim import LoopSim
from agent_types import basicHumanParams as humanParams, \
    basicIDMParams as IDMParams, basicACCParams as ACCParams, \
    basicGapFillerParams as gapFillerParams, \
    basicFillGapMidpointParams as fillGapMidpointParams, \
    basicMidpointParams as midpointParams


if __name__ == "__main__":
    vTypeParams = humanParams
    vTypeParams["laneSpread"] = 0
    vTypeParams["tau"] = 0.5
    vTypeParams["speedDev"] = 0.1
    vTypeParams["speedFactor"] = 1

    mParams = midpointParams
    mParams["laneSpread"] = 0

    gParams = fillGapMidpointParams
    gParams["laneSpread"] = 0

    aParams = ACCParams
    aParams["laneSpread"] = 0

    ###############
    # Option ranges
    ###############

    numLanes = 2
    totVehicles = 22

    '''
    sigmaValues = [0.5, 0.9]
    numRobotsValues = [1,5,11,22]
    numRuns = 3
    robotTypes = (mParams, gParams, aParams)
    '''

    sigmaValues = [0.9]
    numRobotsValues = [0, 1]
    numRuns = 1
    robotTypes = [gParams]

    fps = 24
    simStepLength = 1./fps
    simTime = 100
    simSteps = int(simTime/simStepLength)
    sim = LoopSim("loopsim", length=230, numLanes=numLanes, simStepLength=simStepLength)

    for sigma in sigmaValues:
        for numRobots in numRobotsValues:
            for rParams in robotTypes:
                vTypeParams["sigma"] = sigma
                vTypeParams["count"] = (totVehicles-numRobots) 
                rParams["count"] = numRobots 

                if defaults.RANDOM_SEED:
                    print ">>> Setting random seed to ", defaults.RANDOM_SEED
                    random.seed(defaults.RANDOM_SEED)

                for run in range(numRuns):
                    opts = {
                        "paramsList" : [vTypeParams, rParams],
                        "simSteps"   : simSteps,
                        "tag"        : "Sugiyama-sigma=%03f-run=%d" % (sigma, run),
                    }

                    print "***"
                    print "sigma =", sigma, "numRobots = ", numRobots, 
                    print "robot type =", rParams["name"], "run = ", run
                    print "***"
                    speedRange = (0,30)
                    sim.simulate(opts, sumo='sumo-gui', speedRange=speedRange, sublane=False)
                    sim.plot(show=False, save=True, speedRange=speedRange).close("all")
                if numRobots == 0:
                    break
