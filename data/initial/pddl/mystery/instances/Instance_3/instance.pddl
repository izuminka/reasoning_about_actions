


(define (problem strips-mystery-l2-f5-s2-v2-c11)
(:domain mystery-strips)
(:objects f0 f1 f2 f3 f4 f5 - fuel
          s0 s1 s2 - space
          l0 l1 - location
          v0 v1 - vehicle
          c0 c1 c2 c3 c4 c5 c6 c7 c8 c9 c10 - cargo)
(:init
(fuel-neighbor f0 f1)
(fuel-neighbor f1 f2)
(fuel-neighbor f2 f3)
(fuel-neighbor f3 f4)
(fuel-neighbor f4 f5)
(space-neighbor s0 s1)
(space-neighbor s1 s2)
(conn l0 l1)
(conn l1 l0)
(has-fuel l0 f4)
(has-fuel l1 f3)
(has-space  v0 s2)
(has-space  v1 s2)
(at v0 l1)
(at v1 l1)
(at c0 l0)
(at c1 l1)
(at c2 l0)
(at c3 l0)
(at c4 l0)
(at c5 l1)
(at c6 l0)
(at c7 l0)
(at c8 l1)
(at c9 l1)
(at c10 l1)
)
(:goal
(and
(at c0 l1)
(at c1 l1)
(at c2 l1)
(at c3 l1)
(at c4 l1)
(at c5 l0)
(at c6 l1)
(at c7 l1)
(at c8 l1)
(at c9 l0)
(at c10 l0)
)
)
)


