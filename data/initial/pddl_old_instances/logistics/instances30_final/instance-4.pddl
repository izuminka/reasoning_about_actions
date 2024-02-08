(define (problem logistics-c2-s2-p3-a2)
(:domain logistics-strips)
(:objects
 a0 a1 - airplane
 t0 t1 - truck
 c0 c1 - city
 l0-1 l1-1 - location
 l0-0 l1-0 - airport
 p0 p1 p2 - package)

(:init
    (in-city l0-0 c0)
    (in-city l0-1 c0)
    (in-city l1-0 c1)
    (in-city l1-1 c1)
    (at t0 l0-0)
    (at t1 l1-0)
    (at p0 l0-0)
    (at p1 l1-1)
    (at p2 l0-1)
    (at a0 l1-0)
    (at a1 l0-0)
)(:goal
    (and
        (at p0 l0-1)
        (at p1 l0-0)
        (at p2 l1-1)
    )
)
)