(board-truck driver1 truck1 s0)
(load-truck package1 truck1 s0)
(drive-truck truck1 s0 s2 driver1)
(load-truck package2 truck1 s2)
(unload-truck package1 truck1 s2)
(drive-truck truck1 s2 s1 driver1)
(disembark-truck driver1 truck1 s1)
(board-truck driver1 truck3 s1)
(drive-truck truck3 s1 s0 driver1)
(unload-truck package2 truck1 s1)
; cost = 10 (unit cost)