(walk driver1 s0 p0-2)
(walk driver1 p0-2 s2)
(board-truck driver1 truck5 s2)
(drive-truck truck5 s2 s0 driver1)
(load-truck package2 truck5 s0)
(drive-truck truck5 s0 s1 driver1)
(load-truck package1 truck5 s1)
(drive-truck truck5 s1 s2 driver1)
(unload-truck package2 truck5 s2)
(unload-truck package1 truck5 s2)
(drive-truck truck5 s2 s1 driver1)
(disembark-truck driver1 truck5 s1)
(walk driver1 s1 p1-2)
(walk driver1 p1-2 s2)
(board-truck driver1 truck3 s2)
(drive-truck truck3 s2 s0 driver1)
(disembark-truck driver1 truck3 s0)
; cost = 17 (unit cost)
