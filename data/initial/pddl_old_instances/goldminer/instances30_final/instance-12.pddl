(define (problem typed-bomberman-rows5-cols2)
(:domain gold-miner-typed)
(:objects 
        f0-0f f0-1f 
        f1-0f f1-1f 
        f2-0f f2-1f 
        f3-0f f3-1f 
        f4-0f f4-1f  - LOC
)
(:init
(arm-empty)
(connected f0-0f f0-1f)
(connected f1-0f f1-1f)
(connected f2-0f f2-1f)
(connected f3-0f f3-1f)
(connected f4-0f f4-1f)
(connected f0-0f f1-0f)
(connected f0-1f f1-1f)
(connected f1-0f f2-0f)
(connected f1-1f f2-1f)
(connected f2-0f f3-0f)
(connected f2-1f f3-1f)
(connected f3-0f f4-0f)
(connected f3-1f f4-1f)
(connected f0-1f f0-0f)
(connected f1-1f f1-0f)
(connected f2-1f f2-0f)
(connected f3-1f f3-0f)
(connected f4-1f f4-0f)
(connected f1-0f f0-0f)
(connected f1-1f f0-1f)
(connected f2-0f f1-0f)
(connected f2-1f f1-1f)
(connected f3-0f f2-0f)
(connected f3-1f f2-1f)
(connected f4-0f f3-0f)
(connected f4-1f f3-1f)
(clear f0-0f)
(hard-rock-at f0-1f)
(robot-at f1-0f)
(clear f1-0f)
(hard-rock-at f1-1f)
(bomb-at f2-0f)
(laser-at f2-0f)
(clear f2-0f)
(gold-at f2-1f)
(soft-rock-at f2-1f)
(clear f3-0f)
(hard-rock-at f3-1f)
(clear f4-0f)
(soft-rock-at f4-1f)
)
(:goal
(holds-gold)
)
)