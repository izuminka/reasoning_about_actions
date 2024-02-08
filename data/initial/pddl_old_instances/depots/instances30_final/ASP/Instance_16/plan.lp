occurs(action_drive(truck0,distributor1,depot1),1).
occurs(action_lift(hoist1,crate1,pallet1,depot1),2).
occurs(action_load(hoist1,crate1,truck0,depot1),3).
occurs(action_drive(truck0,depot1,depot2),4).
occurs(action_lift(hoist2,crate0,pallet2,depot2),5).
occurs(action_load(hoist2,crate0,truck0,depot2),6).
occurs(action_unload(hoist2,crate1,truck0,depot2),7).
occurs(action_drop(hoist2,crate1,pallet2,depot2),8).
