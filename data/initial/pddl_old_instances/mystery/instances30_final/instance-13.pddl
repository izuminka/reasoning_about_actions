


(define (problem strips-mystery-l6-f3-s5-v7-c2)
(:domain mystery-strips)
(:objects f0 f1 f2 f3 - fuel
          s0 s1 s2 s3 s4 s5 - space
          l0 l1 l2 l3 l4 l5 - location
          v0 v1 v2 v3 v4 v5 v6 - vehicle
          c0 c1 - cargo)
(:init
(fuel-neighbor f0 f1)
(fuel-neighbor f1 f2)
(fuel-neighbor f2 f3)
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
(conn l3 l4)
(conn l4 l3)
(conn l4 l5)
(conn l5 l4)
(conn l5 l0)
(conn l0 l5)
(has-fuel l0 f2)
(has-fuel l1 f0)
(has-fuel l2 f3)
(has-fuel l3 f2)
(has-fuel l4 f0)
(has-fuel l5 f0)
(has-space  v0 s4)
(has-space  v1 s1)
(has-space  v2 s1)
(has-space  v3 s5)
(has-space  v4 s5)
(has-space  v5 s3)
(has-space  v6 s3)
(at v0 l3)
(at v1 l2)
(at v2 l5)
(at v3 l1)
(at v4 l1)
(at v5 l0)
(at v6 l0)
(at c0 l0)
(at c1 l0)
)
(:goal
(and
(at c0 l5)
(at c1 l5)
)
)
)


