import random

import traci


def randomChangeLaneFn((idx, car), sim, step):
    li = car["lane"]
    if random.random() > .99:
        traci.vehicle.changeLane(car["id"], 1-li, 1000)

def ACCFnBuilder(follow_sec = 3.0, max_speed = 26.8, gain = 0.1):
    """
    Basic adaptive cruise control (ACC) controller
    :param follow_sec:
    :param max_speed: 26.8 m/s = 60 mph
    :param gain:
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

        if step < 250:
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
            new_speed = min(curr_speed + gain * delta, max_speed)
            traci.vehicle.slowDown(vehID, new_speed, 1000) # 2.5 sec
            # print curr_speed, new_speed, front_speed, delta, front_dist, follow_dist
        elif follow_dist > front_dist:
            # slow down
            new_speed = max(curr_speed + gain * delta, 0)
            traci.vehicle.slowDown(vehID, new_speed, 1000) # 2.5 sec
        # print curr_speed, new_speed, front_speed, delta, front_dist, follow_dist
        # print (front_vID, front_dist), (back_vID, back_dist)

    return ACCFn
