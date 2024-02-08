


(define (problem strips-mystery-l5-f6-s8-v4-c1)
(:domain mystery-strips)
(:objects f0 f1 f2 f3 f4 f5 f6 - fuel
          s0 s1 s2 s3 s4 s5 s6 s7 s8 - space
          l0 l1 l2 l3 l4 - location
          v0 v1 v2 v3 - vehicle
          c0 - cargo)
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
(space-neighbor s6 s7)
(space-neighbor s7 s8)
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
(has-fuel l2 f4)
(has-fuel l3 f5)
(has-fuel l4 f2)
(has-space  v0 s3)
(has-space  v1 s2)
(has-space  v2 s5)
(has-space  v3 s2)
(at v0 l3)
(at v1 l4)
(at v2 l3)
(at v3 l2)
(at c0 l4)
)
(:goal
(and
(at c0 l2)
)
)
)


