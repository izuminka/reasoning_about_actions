

(define (problem BW-rand-2)
(:domain BLOCKS)
(:objects b1 b2 - block)
(:init
(handempty)
(on b1 b2)
(ontable b2)
(clear b1)
)
(:goal
(and
(on b2 b1))
)
)


