

(define (problem BW-rand-8)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 - block)
(:init
(handempty)
(on b1 b6)
(on b2 b5)
(on b3 b8)
(on b4 b1)
(ontable b5)
(on b6 b7)
(ontable b7)
(ontable b8)
(clear b2)
(clear b3)
(clear b4)
)
(:goal
(and
(on b1 b3)
(on b2 b4)
(on b3 b7)
(on b5 b1)
(on b6 b8)
(on b7 b2)
(on b8 b5))
)
)


