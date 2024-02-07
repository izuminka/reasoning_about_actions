

(define (problem BW-rand-9)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 - block)
(:init
(handempty)
(on b1 b5)
(on b2 b1)
(ontable b3)
(on b4 b8)
(ontable b5)
(ontable b6)
(on b7 b3)
(on b8 b2)
(on b9 b7)
(clear b4)
(clear b6)
(clear b9)
)
(:goal
(and
(on b1 b9)
(on b2 b7)
(on b3 b5)
(on b5 b6)
(on b7 b8)
(on b8 b1))
)
)


