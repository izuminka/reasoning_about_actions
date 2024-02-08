(define (problem logistics-c3-s2-p5-a2)
(:domain logistics-strips)
(:objects
 a0 a1 - airplane
 t0 t1 t2 t3 - truck
 c0 c1 c2 - city
 l0-1 l1-1 l2-1 - location
 l0-0 l1-0 l2-0 - airport
 p0 p1 p2 p3 p4 - package)

(:init
    (in-city l0-0 c0)
    (in-city l0-1 c0)
    (in-city l1-0 c1)
    (in-city l1-1 c1)
    (in-city l2-0 c2)
    (in-city l2-1 c2)
    (at t0 l0-1)
    (at t1 l1-1)
    (at t2 l2-0)
    (at t3 l1-0)
    (at p0 l2-1)
    (at p1 l1-1)
    (at p2 l0-1)
    (at p3 l0-0)
    (at p4 l0-0)
    (at a0 l0-0)
    (at a1 l2-0)
)(:goal
    (and
        (at p0 l2-0)
        (at p1 l1-0)
        (at p2 l2-1)
        (at p3 l1-0)
        (at p4 l1-1)
    )
)
)