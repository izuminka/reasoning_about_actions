(board-truck driver1 truck2 s1)
(drive-truck truck2 s1 s2 driver1)
(disembark-truck driver1 truck2 s2)
(walk driver1 s2 p0-2)
(walk driver1 p0-2 s0)
(board-truck driver1 truck1 s0)
(drive-truck truck1 s0 s3 driver1)
(load-truck package4 truck1 s3)
(load-truck package2 truck1 s3)
(drive-truck truck1 s3 s2 driver1)
(unload-truck package4 truck1 s2)
(load-truck package3 truck1 s2)
(unload-truck package2 truck1 s2)
(drive-truck truck1 s2 s1 driver1)
(unload-truck package3 truck1 s1)
(load-truck package1 truck1 s1)
(drive-truck truck1 s1 s0 driver1)
(unload-truck package1 truck1 s0)
(drive-truck truck1 s0 s3 driver1)
(walk driver2 s2 p0-2)
(walk driver2 p0-2 s0)
; cost = 21 (unit cost)
