


(define (problem strips-mystery-l4-f5-s5-v3-c2)
(:domain mystery-strips)
(:objects f0 f1 f2 f3 f4 f5 - fuel
          s0 s1 s2 s3 s4 s5 - space
          l0 l1 l2 l3 - location
          v0 v1 v2 - vehicle
          c0 c1 - cargo)
(:init
(fuel-neighbor f0 f1)
(fuel-neighbor f1 f2)
(fuel-neighbor f2 f3)
(fuel-neighbor f3 f4)
(fuel-neighbor f4 f5)
(space-neighbor s0 s1)
(space-neighbor s1 s2)
(space-neighbor s2 s3)
(space-neighbor s3 s4)
(space-neighbor s4 s5)
(conn l0 l1)
(conn l1 l0)
(conn l1 l2)
(conn l2 l1)
(conn l2 l3)
(conn l3 l2)
(conn l3 l0)
(conn l0 l3)
(has-fuel l0 f4)
(has-fuel l1 f5)
(has-fuel l2 f1)
(has-fuel l3 f3)
(has-space  v0 s3)
(has-space  v1 s5)
(has-space  v2 s3)
(at v0 l2)
(at v1 l2)
(at v2 l3)
(at c0 l3)
(at c1 l2)
)
(:goal
(and
(at c0 l1)
(at c1 l0)
)
)
)


