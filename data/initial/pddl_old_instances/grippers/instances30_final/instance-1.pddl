(define (problem gripper-7-4-3)
(:domain gripper-strips)
(:objects robot1 robot2 robot3 robot4 robot5 robot6 robot7 - robot
rgripper1 lgripper1 rgripper2 lgripper2 rgripper3 lgripper3 rgripper4 lgripper4 rgripper5 lgripper5 rgripper6 lgripper6 rgripper7 lgripper7 - gripper
room1 room2 room3 room4 - room
ball1 ball2 ball3 - object)
(:init
(at-robby robot1 room3)
(free robot1 rgripper1)
(free robot1 lgripper1)
(at-robby robot2 room1)
(free robot2 rgripper2)
(free robot2 lgripper2)
(at-robby robot3 room3)
(free robot3 rgripper3)
(free robot3 lgripper3)
(at-robby robot4 room4)
(free robot4 rgripper4)
(free robot4 lgripper4)
(at-robby robot5 room2)
(free robot5 rgripper5)
(free robot5 lgripper5)
(at-robby robot6 room2)
(free robot6 rgripper6)
(free robot6 lgripper6)
(at-robby robot7 room2)
(free robot7 rgripper7)
(free robot7 lgripper7)
(at ball1 room3)
(at ball2 room3)
(at ball3 room1)
)
(:goal
(and
(at ball1 room3)
(at ball2 room4)
(at ball3 room2)
)
)
)