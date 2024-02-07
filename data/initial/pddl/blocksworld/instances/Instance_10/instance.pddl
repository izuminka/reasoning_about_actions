

(define (problem BW-rand-8)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 - block)
(:init
(handempty)
(ontable b1)
(on b2 b4)
(on b3 b8)
(ontable b4)
(ontable b5)
(on b6 b3)
(on b7 b1)
(on b8 b5)
(clear b2)
(clear b6)
(clear b7)
)
(:goal
(and
(on b1 b2)
(on b2 b7)
(on b3 b5)
(on b5 b6)
(on b6 b8)
(on b7 b4)
(on b8 b1))
)
)


