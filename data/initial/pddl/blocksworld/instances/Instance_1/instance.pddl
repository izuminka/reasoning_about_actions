

(define (problem BW-rand-7)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 - block)
(:init
(handempty)
(ontable b1)
(ontable b2)
(on b3 b7)
(on b4 b1)
(on b5 b4)
(ontable b6)
(on b7 b6)
(clear b2)
(clear b3)
(clear b5)
)
(:goal
(and
(on b2 b6)
(on b3 b2)
(on b4 b7)
(on b5 b1)
(on b6 b5)
(on b7 b3))
)
)


