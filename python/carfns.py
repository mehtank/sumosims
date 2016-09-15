import random
from numpy import mean

import traci


def randomChangeLaneFn((idx, car), sim, step):
    li = car["lane"]
    if random.random() > .99:
        traci.vehicle.changeLane(car["id"], 1-li, 1000)

def changeFasterLaneBuilder(speedThreshold = 5, likelihood = 0.5, 
                            dxBack = 0, dxForward = 60, 
                            gapBack = 10, gapForward = 5):
    """
    Intelligent lane changer
    :param speedThreshold: minimum speed increase required
    :param likelihood: probability change will be requested if warranted
    :param dxBack: Farthest distance back car can see
    :param dxForward: Farthest distance forward car can see
    :param gapBack: Minimum required clearance behind car 
    :param gapForward: Minimum required clearance in front car 
    :return: carFn to input to a carParams
    """
    def carFn((idx, car), sim, step):
        if step < 250:
            return

        v = [0] * sim.numLanes
        for lane in range(sim.numLanes):
            if sim.getCars(idx, dxBack=gapBack, dxForward=gapForward, lane=lane):
                # cars too close, no lane changing allowed
                v[lane] = 0
                continue
            cars = sim.getCars(idx, dxBack=dxBack, dxForward=dxForward, lane=lane)
            if len(cars) > 0:
                v[lane] = mean([c["v"] for c in cars])
            else:
                v[lane] = traci.vehicle.getMaxSpeed(car["id"])
        maxv = max(v)
        maxl = v.index(maxv)
        myv = v[car["lane"]]

        if maxl != car["lane"] and \
           (maxv - myv) > speedThreshold and \
           random.random() < likelihood:
            traci.vehicle.changeLane(car["id"], maxl, 10000)
    return carFn

def ACCFnBuilder(follow_sec = 3.0, max_speed = 26.8, gain = 0.01, beta = 0.5):
    """
    Basic adaptive cruise control (ACC) controller
    :param follow_sec: number of seconds worth of following distance to keep from the front vehicle
    :param max_speed: 26.8 m/s = 60 mph
    :param gain: gain for tracking following distance
    :param beta: gain for tracking speed of front vehicle
    :return: ACCFn to input to a carParams
    """

    def ACCFn((idx, car), sim, step):
        """
        :param idx:
        :param car:
        :param sim:
        :param step:
        :return:
        """
        vehID = car["id"]

        # TODO(cathywu) Setting tau to any value seems to cause collisions
        # traci.vehicle.setTau(vehID, 0.01)

        if step < sim.simSteps/2:
            # changeFasterLaneBuilder()((idx, car), sim, step)
            return

        try:
            [back_car, front_car] = sim.getCars(idx, numBack=1, numForward=1, lane=car["lane"])
        except ValueError:
            # Not enough cars on lane
            return

        front_dist = (front_car["x"] - car["x"]) % sim.length
        back_dist = (car["x"] - back_car["x"]) % sim.length

        curr_speed = car["v"]
        front_speed = front_car["v"]
        follow_dist = front_speed*follow_sec
        delta = front_dist - follow_dist
        # print delta, curr_speed, front_speed, curr_speed-front_speed
        if follow_dist < front_dist and curr_speed < max_speed:
            # speed up
            new_speed = min(curr_speed + beta * (front_speed-curr_speed) + gain * delta, max_speed)
            traci.vehicle.slowDown(vehID, new_speed, 1000) # 2.5 sec
            print "t=%d, FASTER, %0.1f -> %0.1f (%0.1f) | d=%0.2f = %0.2f vs %0.2f" % \
                  (step, curr_speed, new_speed, front_speed, delta, front_dist, follow_dist)
        elif follow_dist > front_dist:
            # slow down
            new_speed = max(curr_speed + beta * (front_speed-curr_speed) + gain * delta, 0)
            traci.vehicle.slowDown(vehID, new_speed, 1000) # 2.5 sec
            print "t=%d, SLOWER, %0.1f -> %0.1f (%0.1f) | d=%0.2f = %0.2f vs %0.2f" % \
                  (step, curr_speed, new_speed, front_speed, delta, front_dist, follow_dist)

    return ACCFn

def MidpointFnBuilder(max_speed = 26.8, gain = 0.1, beta = 0.5, duration = 500, bias = 1.0, ratio = 0.5):
    """
    Basic adaptive cruise control (ACC) controller
    :param max_speed: 26.8 m/s = 60 mph
    :param gain: gain for tracking following distance
    :param beta: gain for tracking speed of front vehicle
    :param duration: duration for transitioning to new speed (ms)
    :param bias: additive speed bias term (m/s)
    :param ratio: ratio of distance between front and back vehicles to track
            as following distance (default is 0.5=midpoint)
    :return: MidpointFn as input to a carParams
    """

    def MidpointFn((idx, car), sim, step):
        """
        :param idx:
        :param car:
        :param sim:
        :param step:
        :return:
        """
        vehID = car["id"]

        try:
            [back_car, front_car] = sim.getCars(idx, numBack=1, numForward=1, lane=car["lane"])
        except ValueError:
            # Not enough cars on lane
            return

        front_dist = (front_car["x"] - car["x"]) % sim.length
        back_dist = (car["x"] - back_car["x"]) % sim.length

        curr_speed = car["v"]
        front_speed = front_car["v"]
        follow_dist = (front_dist + back_dist) * ratio
        delta = front_dist - follow_dist
        # print delta, curr_speed, front_speed, curr_speed-front_speed
        if follow_dist < front_dist and curr_speed < max_speed:
            # speed up
            new_speed = min(curr_speed + beta * (front_speed-curr_speed) + gain * delta + bias, max_speed)
            traci.vehicle.slowDown(vehID, new_speed, duration) # 2.5 sec
            print "t=%d, FASTER, %0.1f -> %0.1f (%0.1f) | d=%0.2f = %0.2f vs %0.2f" % \
                  (step, curr_speed, new_speed, front_speed, delta, front_dist, follow_dist)
        elif follow_dist > front_dist:
            # slow down
            new_speed = max(curr_speed + beta * (front_speed-curr_speed) + gain * delta + bias, 0)
            traci.vehicle.slowDown(vehID, new_speed, duration) # 2.5 sec
            print "t=%d, SLOWER, %0.1f -> %0.1f (%0.1f) | d=%0.2f = %0.2f vs %0.2f" % \
                  (step, curr_speed, new_speed, front_speed, delta, front_dist, follow_dist)

    return MidpointFn

def SwitchFn(car_type, switch_point, initCarFn=None):
    """
    Switches vehicle type from initialized to car_type.

    WARNING: can really only handle 1 switch, because after the switch, a
    different CarFn will be executed instead of the one returned here.

    :param car_type:
    :param switch_point:
    :return:
    """

    def CarFn((idx, car), sim, step):
        if initCarFn is not None:
            initCarFn((idx, car), sim, step)
        if step == int(float(sim.simSteps) * switch_point):
            traci.vehicle.setType(car["id"], car_type)

    return CarFn