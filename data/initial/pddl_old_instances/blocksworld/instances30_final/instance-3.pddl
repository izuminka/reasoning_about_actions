

(define (problem BW-rand-9)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 - block)
(:init
(handempty)
(on b1 b7)
(on b2 b9)
(on b3 b8)
(ontable b4)
(ontable b5)
(ontable b6)
(on b7 b4)
(on b8 b5)
(ontable b9)
(clear b1)
(clear b2)
(clear b3)
(clear b6)
)
(:goal
(and
(on b1 b7)
(on b3 b9)
(on b4 b3)
(on b5 b2)
(on b6 b8)
(on b7 b6)
(on b9 b1))
)
)


