(define (problem depot-6-7-3-13-13-2) (:domain depots)
(:objects
	depot0 depot1 depot2 depot3 depot4 depot5 - Depot
	distributor0 distributor1 distributor2 distributor3 distributor4 distributor5 distributor6 - Distributor
	truck0 truck1 truck2 - Truck
	pallet0 pallet1 pallet2 pallet3 pallet4 pallet5 pallet6 pallet7 pallet8 pallet9 pallet10 pallet11 pallet12 - Pallet
	crate0 crate1 - Crate
	hoist0 hoist1 hoist2 hoist3 hoist4 hoist5 hoist6 hoist7 hoist8 hoist9 hoist10 hoist11 hoist12 - Hoist)
(:init
	(at pallet0 depot0)
	(clear crate1)
	(at pallet1 depot1)
	(clear pallet1)
	(at pallet2 depot2)
	(clear crate0)
	(at pallet3 depot3)
	(clear pallet3)
	(at pallet4 depot4)
	(clear pallet4)
	(at pallet5 depot5)
	(clear pallet5)
	(at pallet6 distributor0)
	(clear pallet6)
	(at pallet7 distributor1)
	(clear pallet7)
	(at pallet8 distributor2)
	(clear pallet8)
	(at pallet9 distributor3)
	(clear pallet9)
	(at pallet10 distributor4)
	(clear pallet10)
	(at pallet11 distributor5)
	(clear pallet11)
	(at pallet12 distributor6)
	(clear pallet12)
	(at truck0 depot2)
	(at truck1 depot0)
	(at truck2 depot5)
	(at hoist0 depot0)
	(available hoist0)
	(at hoist1 depot1)
	(available hoist1)
	(at hoist2 depot2)
	(available hoist2)
	(at hoist3 depot3)
	(available hoist3)
	(at hoist4 depot4)
	(available hoist4)
	(at hoist5 depot5)
	(available hoist5)
	(at hoist6 distributor0)
	(available hoist6)
	(at hoist7 distributor1)
	(available hoist7)
	(at hoist8 distributor2)
	(available hoist8)
	(at hoist9 distributor3)
	(available hoist9)
	(at hoist10 distributor4)
	(available hoist10)
	(at hoist11 distributor5)
	(available hoist11)
	(at hoist12 distributor6)
	(available hoist12)
	(at crate0 depot2)
	(on crate0 pallet2)
	(at crate1 depot0)
	(on crate1 pallet0)
)

(:goal (and
		(on crate0 pallet2)
		(on crate1 pallet6)
	)
))