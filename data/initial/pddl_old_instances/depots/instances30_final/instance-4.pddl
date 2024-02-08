(define (problem depot-1-1-1-6-2-2) (:domain depots)
(:objects
	depot0 - Depot
	distributor0 - Distributor
	truck0 - Truck
	pallet0 pallet1 pallet2 pallet3 pallet4 pallet5 - Pallet
	crate0 crate1 - Crate
	hoist0 hoist1 - Hoist)
(:init
	(at pallet0 depot0)
	(clear pallet0)
	(at pallet1 distributor0)
	(clear crate0)
	(at pallet2 distributor0)
	(clear pallet2)
	(at pallet3 depot0)
	(clear crate1)
	(at pallet4 distributor0)
	(clear pallet4)
	(at pallet5 distributor0)
	(clear pallet5)
	(at truck0 depot0)
	(at hoist0 depot0)
	(available hoist0)
	(at hoist1 distributor0)
	(available hoist1)
	(at crate0 distributor0)
	(on crate0 pallet1)
	(at crate1 depot0)
	(on crate1 pallet3)
)

(:goal (and
		(on crate0 pallet3)
	)
))
