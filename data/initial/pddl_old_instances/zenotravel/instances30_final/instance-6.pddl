(define (problem ZTRAVEL-8-2)
(:domain zeno-travel)
(:objects
	plane1 - aircraft
	plane2 - aircraft
	plane3 - aircraft
	plane4 - aircraft
	plane5 - aircraft
	plane6 - aircraft
	plane7 - aircraft
	plane8 - aircraft
	person1 - person
	person2 - person
	city0 - city
	city1 - city
	city2 - city
	city3 - city
	fl0 - flevel
	fl1 - flevel
	fl2 - flevel
	fl3 - flevel
	fl4 - flevel
	fl5 - flevel
	fl6 - flevel
	)
(:init
	(at plane1 city3)
	(fuel-level plane1 fl5)
	(at plane2 city1)
	(fuel-level plane2 fl3)
	(at plane3 city3)
	(fuel-level plane3 fl4)
	(at plane4 city2)
	(fuel-level plane4 fl5)
	(at plane5 city0)
	(fuel-level plane5 fl3)
	(at plane6 city0)
	(fuel-level plane6 fl0)
	(at plane7 city2)
	(fuel-level plane7 fl5)
	(at plane8 city2)
	(fuel-level plane8 fl6)
	(at person1 city2)
	(at person2 city3)
	(next fl0 fl1)
	(next fl1 fl2)
	(next fl2 fl3)
	(next fl3 fl4)
	(next fl4 fl5)
	(next fl5 fl6)
)
(:goal (and
	(at person1 city0)
	(at person2 city1)
	))

)