

(define (problem BW-rand-7)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 - block)
(:init
(handempty)
(ontable b1)
(on b2 b4)
(on b3 b2)
(on b4 b7)
(on b5 b1)
(ontable b6)
(on b7 b5)
(clear b3)
(clear b6)
)
(:goal
(and
(on b1 b6)
(on b3 b4)
(on b4 b7)
(on b5 b2)
(on b6 b3)
(on b7 b5))
)
)


