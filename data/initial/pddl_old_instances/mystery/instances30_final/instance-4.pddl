


(define (problem strips-mystery-l2-f5-s8-v8-c3)
(:domain mystery-strips)
(:objects f0 f1 f2 f3 f4 f5 - fuel
          s0 s1 s2 s3 s4 s5 s6 s7 s8 - space
          l0 l1 - location
          v0 v1 v2 v3 v4 v5 v6 v7 - vehicle
          c0 c1 c2 - cargo)
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
(space-neighbor s5 s6)
(space-neighbor s6 s7)
(space-neighbor s7 s8)
(conn l0 l1)
(conn l1 l0)
(has-fuel l0 f2)
(has-fuel l1 f1)
(has-space  v0 s1)
(has-space  v1 s4)
(has-space  v2 s5)
(has-space  v3 s5)
(has-space  v4 s6)
(has-space  v5 s1)
(has-space  v6 s1)
(has-space  v7 s5)
(at v0 l0)
(at v1 l0)
(at v2 l1)
(at v3 l1)
(at v4 l1)
(at v5 l0)
(at v6 l1)
(at v7 l1)
(at c0 l0)
(at c1 l0)
(at c2 l1)
)
(:goal
(and
(at c0 l0)
(at c1 l1)
(at c2 l0)
)
)
)


