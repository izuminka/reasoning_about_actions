

(define (problem BW-rand-9)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 - block)
(:init
(handempty)
(on b1 b7)
(on b2 b6)
(on b3 b4)
(ontable b4)
(ontable b5)
(on b6 b3)
(ontable b7)
(on b8 b1)
(on b9 b8)
(clear b2)
(clear b5)
(clear b9)
)
(:goal
(and
(on b1 b3)
(on b2 b8)
(on b3 b2)
(on b6 b7)
(on b7 b9)
(on b8 b4))
)
)


