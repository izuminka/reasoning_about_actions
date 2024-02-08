


(define (problem strips-mystery-l5-f6-s6-v1-c2)
(:domain mystery-strips)
(:objects f0 f1 f2 f3 f4 f5 f6 - fuel
          s0 s1 s2 s3 s4 s5 s6 - space
          l0 l1 l2 l3 l4 - location
          v0 - vehicle
          c0 c1 - cargo)
(:init
(fuel-neighbor f0 f1)
(fuel-neighbor f1 f2)
(fuel-neighbor f2 f3)
(fuel-neighbor f3 f4)
(fuel-neighbor f4 f5)
(fuel-neighbor f5 f6)
(space-neighbor s0 s1)
(space-neighbor s1 s2)
(space-neighbor s2 s3)
(space-neighbor s3 s4)
(space-neighbor s4 s5)
(space-neighbor s5 s6)
(conn l0 l1)
(conn l1 l0)
(conn l1 l2)
(conn l2 l1)
(conn l2 l3)
(conn l3 l2)
(conn l3 l4)
(conn l4 l3)
(conn l4 l0)
(conn l0 l4)
(has-fuel l0 f6)
(has-fuel l1 f4)
(has-fuel l2 f2)
(has-fuel l3 f6)
(has-fuel l4 f3)
(has-space  v0 s4)
(at v0 l1)
(at c0 l4)
(at c1 l1)
)
(:goal
(and
(at c0 l1)
(at c1 l0)
)
)
)


