(load-truck package4 truck1 s0)
(load-truck package1 truck2 s1)
(walk driver1 s2 p2-0)
(walk driver1 p2-0 s0)
(board-truck driver1 truck1 s0)
(drive-truck truck1 s0 s1 driver1)
(disembark-truck driver1 truck1 s1)
(board-truck driver1 truck2 s1)
(unload-truck package4 truck1 s1)
(drive-truck truck2 s1 s2 driver1)
(load-truck package3 truck2 s2)
(drive-truck truck2 s2 s0 driver1)
(unload-truck package3 truck2 s0)
(unload-truck package1 truck2 s0)
(drive-truck truck2 s0 s2 driver1)
(disembark-truck driver1 truck2 s2)
(walk driver1 s2 p2-0)
(walk driver1 p2-0 s0)
(walk driver2 s2 p2-0)
(walk driver2 p2-0 s0)
; cost = 20 (unit cost)