

(define (problem BW-rand-4)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 - block)
(:init
(handempty)
(on b1 b4)
(ontable b2)
(on b3 b2)
(on b4 b3)
(clear b1)
)
(:goal
(and
(on b3 b1)
(on b4 b3))
)
)


