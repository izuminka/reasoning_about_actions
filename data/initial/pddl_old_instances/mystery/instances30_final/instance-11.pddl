


(define (problem strips-mystery-l8-f4-s7-v7-c3)
(:domain mystery-strips)
(:objects f0 f1 f2 f3 f4 - fuel
          s0 s1 s2 s3 s4 s5 s6 s7 - space
          l0 l1 l2 l3 l4 l5 l6 l7 - location
          v0 v1 v2 v3 v4 v5 v6 - vehicle
          c0 c1 c2 - cargo)
(:init
(fuel-neighbor f0 f1)
(fuel-neighbor f1 f2)
(fuel-neighbor f2 f3)
(fuel-neighbor f3 f4)
(space-neighbor s0 s1)
(space-neighbor s1 s2)
(space-neighbor s2 s3)
(space-neighbor s3 s4)
(space-neighbor s4 s5)
(space-neighbor s5 s6)
(space-neighbor s6 s7)
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
(conn l6 l7)
(conn l7 l6)
(conn l7 l0)
(conn l0 l7)
(has-fuel l0 f2)
(has-fuel l1 f4)
(has-fuel l2 f2)
(has-fuel l3 f2)
(has-fuel l4 f1)
(has-fuel l5 f3)
(has-fuel l6 f0)
(has-fuel l7 f4)
(has-space  v0 s3)
(has-space  v1 s5)
(has-space  v2 s4)
(has-space  v3 s4)
(has-space  v4 s3)
(has-space  v5 s7)
(has-space  v6 s3)
(at v0 l5)
(at v1 l0)
(at v2 l3)
(at v3 l1)
(at v4 l3)
(at v5 l5)
(at v6 l5)
(at c0 l1)
(at c1 l3)
(at c2 l5)
)
(:goal
(and
(at c0 l4)
(at c1 l2)
(at c2 l2)
)
)
)


