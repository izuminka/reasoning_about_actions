


(define (problem strips-mystery-l4-f2-s3-v7-c4)
(:domain mystery-strips)
(:objects f0 f1 f2 - fuel
          s0 s1 s2 s3 - space
          l0 l1 l2 l3 - location
          v0 v1 v2 v3 v4 v5 v6 - vehicle
          c0 c1 c2 c3 - cargo)
(:init
(fuel-neighbor f0 f1)
(fuel-neighbor f1 f2)
(space-neighbor s0 s1)
(space-neighbor s1 s2)
(space-neighbor s2 s3)
(conn l0 l1)
(conn l1 l0)
(conn l1 l2)
(conn l2 l1)
(conn l2 l3)
(conn l3 l2)
(conn l3 l0)
(conn l0 l3)
(has-fuel l0 f2)
(has-fuel l1 f2)
(has-fuel l2 f2)
(has-fuel l3 f2)
(has-space  v0 s2)
(has-space  v1 s2)
(has-space  v2 s2)
(has-space  v3 s3)
(has-space  v4 s3)
(has-space  v5 s2)
(has-space  v6 s1)
(at v0 l0)
(at v1 l3)
(at v2 l0)
(at v3 l0)
(at v4 l0)
(at v5 l3)
(at v6 l3)
(at c0 l0)
(at c1 l2)
(at c2 l1)
(at c3 l3)
)
(:goal
(and
(at c0 l2)
(at c1 l1)
(at c2 l1)
(at c3 l2)
)
)
)


