(walk driver2 s1 p3-1)
(walk driver2 p3-1 s3)
(board-truck driver2 truck1 s3)
(drive-truck truck1 s3 s0 driver2)
(walk driver1 s2 p1-2)
(walk driver1 p1-2 s1)
(walk driver1 s1 p1-4)
(walk driver1 p1-4 s4)
(load-truck package5 truck1 s0)
(load-truck package4 truck1 s0)
(drive-truck truck1 s0 s2 driver2)
(unload-truck package5 truck1 s2)
(unload-truck package4 truck1 s2)
(load-truck package3 truck1 s2)
(drive-truck truck1 s2 s1 driver2)
(unload-truck package3 truck1 s1)
(load-truck package1 truck1 s1)
(drive-truck truck1 s1 s0 driver2)
(unload-truck package1 truck1 s0)
(drive-truck truck1 s0 s3 driver2)
; cost = 20 (unit cost)