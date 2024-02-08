


(define (problem strips-mystery-l7-f9-s2-v3-c4)
(:domain mystery-strips)
(:objects f0 f1 f2 f3 f4 f5 f6 f7 f8 f9 - fuel
          s0 s1 s2 - space
          l0 l1 l2 l3 l4 l5 l6 - location
          v0 v1 v2 - vehicle
          c0 c1 c2 c3 - cargo)
(:init
(fuel-neighbor f0 f1)
(fuel-neighbor f1 f2)
(fuel-neighbor f2 f3)
(fuel-neighbor f3 f4)
(fuel-neighbor f4 f5)
(fuel-neighbor f5 f6)
(fuel-neighbor f6 f7)
(fuel-neighbor f7 f8)
(fuel-neighbor f8 f9)
(space-neighbor s0 s1)
(space-neighbor s1 s2)
(conn l0 l1)
(conn l1 l0)
(conn l1 l2)
(conn l2 l1)
(conn l2 l3)
(conn l3 l2)
(conn l3 l4)
(conn l4 l3)
(conn l4 l5)
(conn l5 l4)
(conn l5 l6)
(conn l6 l5)
(conn l6 l0)
(conn l0 l6)
(has-fuel l0 f8)
(has-fuel l1 f6)
(has-fuel l2 f8)
(has-fuel l3 f8)
(has-fuel l4 f6)
(has-fuel l5 f4)
(has-fuel l6 f2)
(has-space  v0 s1)
(has-space  v1 s1)
(has-space  v2 s1)
(at v0 l3)
(at v1 l4)
(at v2 l6)
(at c0 l4)
(at c1 l2)
(at c2 l3)
(at c3 l2)
)
(:goal
(and
(at c0 l3)
(at c1 l6)
(at c2 l2)
(at c3 l1)
)
)
)

