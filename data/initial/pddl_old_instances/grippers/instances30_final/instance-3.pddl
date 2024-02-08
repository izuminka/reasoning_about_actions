(define (problem gripper-2-8-3)
(:domain gripper-strips)
(:objects robot1 robot2 - robot
rgripper1 lgripper1 rgripper2 lgripper2 - gripper
room1 room2 room3 room4 room5 room6 room7 room8 - room
ball1 ball2 ball3 - object)
(:init
(at-robby robot1 room8)
(free robot1 rgripper1)
(free robot1 lgripper1)
(at-robby robot2 room2)
(free robot2 rgripper2)
(free robot2 lgripper2)
(at ball1 room6)
(at ball2 room2)
(at ball3 room6)
)
(:goal
(and
(at ball1 room8)
(at ball2 room7)
(at ball3 room8)
)
)
)
