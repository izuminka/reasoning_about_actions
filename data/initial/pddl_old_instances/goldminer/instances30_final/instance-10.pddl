(define (problem typed-bomberman-rows2-cols2)
(:domain gold-miner-typed)
(:objects 
        f0-0f f0-1f 
        f1-0f f1-1f  - LOC
)
(:init
(arm-empty)
(connected f0-0f f0-1f)
(connected f1-0f f1-1f)
(connected f0-0f f1-0f)
(connected f0-1f f1-1f)
(connected f0-1f f0-0f)
(connected f1-1f f1-0f)
(connected f1-0f f0-0f)
(connected f1-1f f0-1f)
(robot-at f0-0f)
(clear f0-0f)
(gold-at f0-1f)
(soft-rock-at f0-1f)
(bomb-at f1-0f)
(laser-at f1-0f)
(clear f1-0f)
(hard-rock-at f1-1f)
)
(:goal
(holds-gold)
)
)