(walk driver1 s0 p0-3)
(walk driver1 p0-3 s3)
(board-truck driver1 truck1 s3)
(drive-truck truck1 s3 s2 driver1)
(load-truck package1 truck1 s2)
(drive-truck truck1 s2 s3 driver1)
(unload-truck package1 truck1 s3)
(drive-truck truck1 s3 s1 driver1)
(disembark-truck driver1 truck1 s1)
(walk driver1 s1 p0-1)
(walk driver1 p0-1 s0)
(walk driver3 s2 p0-2)
(walk driver3 p0-2 s0)
; cost = 13 (unit cost)
