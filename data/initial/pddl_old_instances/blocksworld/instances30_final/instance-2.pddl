

(define (problem BW-rand-7)
(:domain BLOCKS)
(:objects b1 b2 b3 b4 b5 b6 b7 - block)
(:init
(handempty)
(ontable b1)
(on b2 b6)
(ontable b3)
(on b4 b3)
(on b5 b7)
(ontable b6)
(on b7 b1)
(clear b2)
(clear b4)
(clear b5)
)
(:goal
(and
(on b1 b2)
(on b2 b5)
(on b4 b7)
(on b5 b3)
(on b6 b1)
(on b7 b6))
)
)


