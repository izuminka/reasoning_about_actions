(define (problem gripper-1-9-1)
(:domain gripper-strips)
(:objects robot1 - robot
rgripper1 lgripper1 - gripper
room1 room2 room3 room4 room5 room6 room7 room8 room9 - room
ball1 - object)
(:init
(at-robby robot1 room7)
(free robot1 rgripper1)
(free robot1 lgripper1)
(at ball1 room9)
)
(:goal
(and
(at ball1 room6)
)
)
)
