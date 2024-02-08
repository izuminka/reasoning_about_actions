(define (problem logistics-c1-s2-p4-a5)
(:domain logistics-strips)
(:objects
 a0 a1 a2 a3 a4 - airplane
 t0 - truck
 c0 - city
 l0-1 - location
 l0-0 - airport
 p0 p1 p2 p3 - package)

(:init
    (in-city l0-0 c0)
    (in-city l0-1 c0)
    (at t0 l0-1)
    (at p0 l0-1)
    (at p1 l0-0)
    (at p2 l0-0)
    (at p3 l0-0)
    (at a0 l0-0)
    (at a1 l0-0)
    (at a2 l0-0)
    (at a3 l0-0)
    (at a4 l0-0)
)(:goal
    (and
        (at p0 l0-1)
        (at p1 l0-1)
        (at p2 l0-0)
        (at p3 l0-0)
    )
)
)