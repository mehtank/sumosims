
import traci

import config as c


def vehID_to_pos(vehID):
    return c.EDGESTARTS[traci.vehicle.getRoadID(vehID)] + \
           traci.vehicle.getLanePosition(vehID)


def headway(curr_vehID, vehicles, lane=0, length=1000):
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
    pos = vehID_to_pos(curr_vehID)
    dists = dict([(v, (vehID_to_pos(v) - pos) % length) \
                 for v in vehicles if traci.vehicle.getLaneIndex(v) == lane \
                 and v != curr_vehID])
    mn = min(dists, key=dists.get)
    mx = max(dists, key=dists.get)

    return ((mn, dists[mn]), (mx, dists[mx]))


