(define (problem logistics-c3-s2-p6-a1)
(:domain logistics-strips)
(:objects
 a0 - airplane
 t0 t1 t2 - truck
 c0 c1 c2 - city
 l0-1 l1-1 l2-1 - location
 l0-0 l1-0 l2-0 - airport
 p0 p1 p2 p3 p4 p5 - package)

(:init
    (in-city l0-0 c0)
    (in-city l0-1 c0)
    (in-city l1-0 c1)
    (in-city l1-1 c1)
    (in-city l2-0 c2)
    (in-city l2-1 c2)
    (at t0 l0-0)
    (at t1 l1-1)
    (at t2 l2-0)
    (at p0 l1-0)
    (at p1 l0-1)
    (at p2 l1-1)
    (at p3 l2-0)
    (at p4 l0-0)
    (at p5 l1-0)
    (at a0 l2-0)
)(:goal
    (and
        (at p0 l2-0)
        (at p1 l1-1)
        (at p2 l2-0)
        (at p3 l1-1)
        (at p4 l1-1)
        (at p5 l0-1)
    )
)
)