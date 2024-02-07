

(define (problem BW-rand-8)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 - block)
(:init
(handempty)
(ontable b1)
(on b2 b1)
(ontable b3)
(on b4 b8)
(on b5 b4)
(on b6 b7)
(on b7 b3)
(on b8 b2)
(clear b5)
(clear b6)
)
(:goal
(and
(on b1 b8)
(on b3 b6)
(on b5 b4)
(on b6 b7))
)
)


