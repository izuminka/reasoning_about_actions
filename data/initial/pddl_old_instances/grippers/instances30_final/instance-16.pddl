(define (problem gripper-1-3-8)
(:domain gripper-strips)
(:objects robot1 - robot
rgripper1 lgripper1 - gripper
room1 room2 room3 - room
ball1 ball2 ball3 ball4 ball5 ball6 ball7 ball8 - object)
(:init
(at-robby robot1 room2)
(free robot1 rgripper1)
(free robot1 lgripper1)
(at ball1 room3)
(at ball2 room3)
(at ball3 room3)
(at ball4 room3)
(at ball5 room2)
(at ball6 room1)
(at ball7 room1)
(at ball8 room1)
)
(:goal
(and
(at ball1 room2)
(at ball2 room3)
(at ball3 room3)
(at ball4 room1)
(at ball5 room1)
(at ball6 room1)
(at ball7 room1)
(at ball8 room3)
)
)
)
