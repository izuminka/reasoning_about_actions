

(define (problem BW-rand-9)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 - block)
(:init
(handempty)
(ontable b1)
(ontable b2)
(ontable b3)
(on b4 b6)
(on b5 b9)
(on b6 b3)
(on b7 b1)
(ontable b8)
(on b9 b8)
(clear b2)
(clear b4)
(clear b5)
(clear b7)
)
(:goal
(and
(on b3 b2)
(on b5 b8)
(on b8 b6)
(on b9 b7))
)
)


