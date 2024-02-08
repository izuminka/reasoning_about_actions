occurs(action_walk(shed,location1,bob),1).
occurs(action_walk(location1,location2,bob),2).
occurs(action_walk(location2,location3,bob),3).
occurs(action_walk(location3,location4,bob),4).
occurs(action_pickup_spanner(location4,spanner4,bob),5).
occurs(action_walk(location4,gate,bob),6).
occurs(action_tighten_nut(gate,spanner4,bob,nut1),7).
