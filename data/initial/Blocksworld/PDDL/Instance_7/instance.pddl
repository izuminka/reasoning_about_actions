

(define (problem BW-rand-9)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 - block)
(:init
(handempty)
(ontable b1)
(on b2 b3)
(on b3 b5)
(on b4 b2)
(on b5 b9)
(ontable b6)
(on b7 b4)
(ontable b8)
(on b9 b6)
(clear b1)
(clear b7)
(clear b8)
)
(:goal
(and
(on b1 b6)
(on b2 b3)
(on b4 b7)
(on b6 b9)
(on b8 b4)
(on b9 b8))
)
)


