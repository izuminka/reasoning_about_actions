

(define (problem BW-rand-8)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 - block)
(:init
(handempty)
(on b1 b7)
(ontable b2)
(on b3 b6)
(on b4 b2)
(on b5 b3)
(ontable b6)
(on b7 b4)
(on b8 b5)
(clear b1)
(clear b8)
)
(:goal
(and
(on b1 b2)
(on b2 b3)
(on b4 b6)
(on b6 b1))
)
)


