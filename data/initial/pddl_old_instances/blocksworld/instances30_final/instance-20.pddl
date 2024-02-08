

(define (problem BW-rand-9)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 - block)
(:init
(handempty)
(on b1 b2)
(ontable b2)
(on b3 b5)
(on b4 b8)
(on b5 b9)
(on b6 b3)
(on b7 b4)
(ontable b8)
(ontable b9)
(clear b1)
(clear b6)
(clear b7)
)
(:goal
(and
(on b3 b8)
(on b5 b2)
(on b6 b9)
(on b7 b3)
(on b8 b4))
)
)


