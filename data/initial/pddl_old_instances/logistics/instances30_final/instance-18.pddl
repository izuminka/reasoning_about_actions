(define (problem logistics-c1-s3-p4-a0)
(:domain logistics-strips)
(:objects
 t0 t1 t2 - truck
 c0 - city
 l0-1 l0-2 - location
 l0-0 - airport
 p0 p1 p2 p3 - package)

(:init
    (in-city l0-0 c0)
    (in-city l0-1 c0)
    (in-city l0-2 c0)
    (at t0 l0-2)
    (at t1 l0-0)
    (at t2 l0-1)
    (at p0 l0-1)
    (at p1 l0-0)
    (at p2 l0-1)
    (at p3 l0-1)
)(:goal
    (and
        (at p0 l0-0)
        (at p1 l0-1)
        (at p2 l0-2)
        (at p3 l0-1)
    )
)
)