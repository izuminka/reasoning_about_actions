

(define (problem BW-rand-2)
(:domain BLOCKS)
(:objects b1 b2 - block)
(:init
(handempty)
(ontable b1)
(ontable b2)
(clear b1)
(clear b2)
)
(:goal
(and
(on b1 b2))
)
)


