(define (problem logistics-c2-s4-p6-a1)
(:domain logistics-strips)
(:objects
 a0 - airplane
 t0 t1 - truck
 c0 c1 - city
 l0-1 l0-2 l0-3 l1-1 l1-2 l1-3 - location
 l0-0 l1-0 - airport
 p0 p1 p2 p3 p4 p5 - package)

(:init
    (in-city l0-0 c0)
    (in-city l0-1 c0)
    (in-city l0-2 c0)
    (in-city l0-3 c0)
    (in-city l1-0 c1)
    (in-city l1-1 c1)
    (in-city l1-2 c1)
    (in-city l1-3 c1)
    (at t0 l0-1)
    (at t1 l1-3)
    (at p0 l1-3)
    (at p1 l1-0)
    (at p2 l1-1)
    (at p3 l0-2)
    (at p4 l0-2)
    (at p5 l0-1)
    (at a0 l1-0)
)(:goal
    (and
        (at p0 l0-1)
        (at p1 l1-1)
        (at p2 l1-1)
        (at p3 l1-1)
        (at p4 l1-0)
        (at p5 l1-3)
    )
)
)