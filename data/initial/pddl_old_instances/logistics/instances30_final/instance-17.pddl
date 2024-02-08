(define (problem logistics-c3-s4-p1-a5)
(:domain logistics-strips)
(:objects
 a0 a1 a2 a3 a4 - airplane
 t0 t1 t2 t3 - truck
 c0 c1 c2 - city
 l0-1 l0-2 l0-3 l1-1 l1-2 l1-3 l2-1 l2-2 l2-3 - location
 l0-0 l1-0 l2-0 - airport
 p0 - package)

(:init
    (in-city l0-0 c0)
    (in-city l0-1 c0)
    (in-city l0-2 c0)
    (in-city l0-3 c0)
    (in-city l1-0 c1)
    (in-city l1-1 c1)
    (in-city l1-2 c1)
    (in-city l1-3 c1)
    (in-city l2-0 c2)
    (in-city l2-1 c2)
    (in-city l2-2 c2)
    (in-city l2-3 c2)
    (at t0 l0-1)
    (at t1 l1-2)
    (at t2 l2-0)
    (at t3 l0-2)
    (at p0 l1-0)
    (at a0 l0-0)
    (at a1 l2-0)
    (at a2 l1-0)
    (at a3 l2-0)
    (at a4 l0-0)
)(:goal
    (and
        (at p0 l0-1)
    )
)
)