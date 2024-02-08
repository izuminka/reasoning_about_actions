(define (problem logistics-c2-s3-p3-a4)
(:domain logistics-strips)
(:objects
 a0 a1 a2 a3 - airplane
 t0 t1 t2 - truck
 c0 c1 - city
 l0-1 l0-2 l1-1 l1-2 - location
 l0-0 l1-0 - airport
 p0 p1 p2 - package)

(:init
    (in-city l0-0 c0)
    (in-city l0-1 c0)
    (in-city l0-2 c0)
    (in-city l1-0 c1)
    (in-city l1-1 c1)
    (in-city l1-2 c1)
    (at t0 l0-1)
    (at t1 l1-1)
    (at t2 l1-1)
    (at p0 l1-2)
    (at p1 l0-0)
    (at p2 l1-0)
    (at a0 l1-0)
    (at a1 l1-0)
    (at a2 l1-0)
    (at a3 l1-0)
)(:goal
    (and
        (at p0 l1-1)
        (at p1 l1-2)
        (at p2 l0-1)
    )
)
)