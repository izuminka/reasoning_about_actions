


(define (problem strips-mystery-l3-f1-s1-v4-c2)
(:domain mystery-strips)
(:objects f0 f1 - fuel
          s0 s1 - space
          l0 l1 l2 - location
          v0 v1 v2 v3 - vehicle
          c0 c1 - cargo)
(:init
(fuel-neighbor f0 f1)
(space-neighbor s0 s1)
(conn l0 l1)
(conn l1 l0)
(conn l1 l2)
(conn l2 l1)
(conn l2 l0)
(conn l0 l2)
(has-fuel l0 f1)
(has-fuel l1 f1)
(has-fuel l2 f1)
(has-space  v0 s1)
(has-space  v1 s1)
(has-space  v2 s1)
(has-space  v3 s1)
(at v0 l1)
(at v1 l1)
(at v2 l0)
(at v3 l1)
(at c0 l2)
(at c1 l1)
)
(:goal
(and
(at c0 l0)
(at c1 l2)
)
)
)


