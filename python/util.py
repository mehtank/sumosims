
import traci

import config as c


def headway(curr_vehID, allCars, length):
    """
    Computes the distance between curr_vehicle and the closest vehicle in front and behind it.
    WARNING: specialized for loop road

    :param curr_position: position from start
    :param curr_vehicle: vehicleID
    :param vehicles: list of vehicleIDs
    :param lane: laneID
    :param length: length of loop road (perimeter)
    :return: (distance to vehicle in front, distance to vehicle behind)
    """
    pos = allCars[curr_vehID]["x"]
    lane = allCars[curr_vehID]["lane"]

    dists = dict([(v, (c["x"] - pos) % length) \
                  for (v, c) in allCars.iteritems() \
                    if v != curr_vehID and c["lane"] == lane])
    mn = min(dists, key=dists.get)
    mx = max(dists, key=dists.get)

    return ((mn, dists[mn]), (mx, dists[mx]))


