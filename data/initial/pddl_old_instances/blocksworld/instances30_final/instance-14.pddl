

(define (problem BW-rand-9)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 - block)
(:init
(handempty)
(on b1 b6)
(on b2 b1)
(on b3 b2)
(on b4 b7)
(on b5 b9)
(ontable b6)
(on b7 b5)
(on b8 b3)
(on b9 b8)
(clear b4)
)
(:goal
(and
(on b1 b7)
(on b2 b8)
(on b3 b4)
(on b4 b9)
(on b5 b1)
(on b6 b5)
(on b9 b6))
)
)


