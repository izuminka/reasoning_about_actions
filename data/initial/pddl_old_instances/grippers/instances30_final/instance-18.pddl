(define (problem gripper-9-5-4)
(:domain gripper-strips)
(:objects robot1 robot2 robot3 robot4 robot5 robot6 robot7 robot8 robot9 - robot
rgripper1 lgripper1 rgripper2 lgripper2 rgripper3 lgripper3 rgripper4 lgripper4 rgripper5 lgripper5 rgripper6 lgripper6 rgripper7 lgripper7 rgripper8 lgripper8 rgripper9 lgripper9 - gripper
room1 room2 room3 room4 room5 - room
ball1 ball2 ball3 ball4 - object)
(:init
(at-robby robot1 room4)
(free robot1 rgripper1)
(free robot1 lgripper1)
(at-robby robot2 room5)
(free robot2 rgripper2)
(free robot2 lgripper2)
(at-robby robot3 room4)
(free robot3 rgripper3)
(free robot3 lgripper3)
(at-robby robot4 room4)
(free robot4 rgripper4)
(free robot4 lgripper4)
(at-robby robot5 room3)
(free robot5 rgripper5)
(free robot5 lgripper5)
(at-robby robot6 room2)
(free robot6 rgripper6)
(free robot6 lgripper6)
(at-robby robot7 room2)
(free robot7 rgripper7)
(free robot7 lgripper7)
(at-robby robot8 room2)
(free robot8 rgripper8)
(free robot8 lgripper8)
(at-robby robot9 room5)
(free robot9 rgripper9)
(free robot9 lgripper9)
(at ball1 room5)
(at ball2 room1)
(at ball3 room3)
(at ball4 room4)
)
(:goal
(and
(at ball1 room5)
(at ball2 room1)
(at ball3 room3)
(at ball4 room5)
)
)
)
