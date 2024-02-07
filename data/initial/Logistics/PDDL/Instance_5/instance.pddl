(define (problem logistics-c2-s5-p4-a2)
(:domain logistics-strips)
(:objects
 a0 a1 - airplane
 t0 t1 t2 - truck
 c0 c1 - city
 l0-1 l0-2 l0-3 l0-4 l1-1 l1-2 l1-3 l1-4 - location
 l0-0 l1-0 - airport
 p0 p1 p2 p3 - package)

(:init
    (in-city l0-0 c0)
    (in-city l0-1 c0)
    (in-city l0-2 c0)
    (in-city l0-3 c0)
    (in-city l0-4 c0)
    (in-city l1-0 c1)
    (in-city l1-1 c1)
    (in-city l1-2 c1)
    (in-city l1-3 c1)
    (in-city l1-4 c1)
    (at t0 l0-2)
    (at t1 l1-0)
    (at t2 l0-0)
    (at p0 l0-1)
    (at p1 l1-2)
    (at p2 l1-3)
    (at p3 l0-4)
    (at a0 l0-0)
    (at a1 l0-0)
)(:goal
    (and
        (at p0 l0-0)
        (at p1 l0-4)
        (at p2 l0-4)
        (at p3 l1-2)
    )
)
)