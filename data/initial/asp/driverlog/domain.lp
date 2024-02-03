% I have the following types:
object(O) :- location(O).
location(O) :- location(O).
object(O) :- locatable(O).
locatable(O) :- locatable(O).
locatable(O) :- driver(O).
driver(O) :- driver(O).
locatable(O) :- truck(O).
truck(O) :- truck(O).
locatable(O) :- obj(O).
obj(O) :- obj(O).

% I have the following predicates:
pfluent(at(L, Loc)) :- locatable(L), location(Loc).
pfluent(member(O, T)) :- obj(O), truck(T).
pfluent(driving(D, T)) :- driver(D), truck(T).
pfluent(link(L1, L2)) :- location(L1), location(L2), L1 != L2.
pfluent(path(L1, L2)) :- location(L1), location(L2), L1 != L2.
pfluent(empty(T)) :- truck(T).

% I have the following actions and restrictions:
action(action_load_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).
cond(cond_exec_load_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).
exec(action_load_truck(Obj, Truck, Loc), cond_exec_load_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).
cond(cond_causes_load_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).

action(action_unload_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).
cond(cond_exec_unload_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).
exec(action_unload_truck(Obj, Truck, Loc), cond_exec_unload_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).
cond(cond_causes_unload_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).

action(action_board_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
cond(cond_exec_board_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
exec(action_board_truck(Driver, Truck, Loc), cond_exec_board_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
cond(cond_causes_board_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).

action(action_disembark_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
cond(cond_exec_disembark_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
exec(action_disembark_truck(Driver, Truck, Loc), cond_exec_disembark_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
cond(cond_causes_disembark_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).

action(action_drive_truck(Truck, Loc_From, Loc_To, Driver)) :- truck(Truck), location(Loc_From), location(Loc_To), Loc_From != Loc_To, driver(Driver).
cond(cond_exec_drive_truck(Truck, Loc_From, Loc_To, Driver)) :- truck(Truck), location(Loc_From), location(Loc_To), Loc_From != Loc_To, driver(Driver).
exec(action_drive_truck(Truck, Loc_From, Loc_To, Driver), cond_exec_drive_truck(Truck, Loc_From, Loc_To, Driver)) :- truck(Truck), location(Loc_From), location(Loc_To), Loc_From != Loc_To, driver(Driver).
cond(cond_causes_drive_truck(Truck, Loc_From, Loc_To, Driver)) :- truck(Truck), location(Loc_From), location(Loc_To), Loc_From != Loc_To, driver(Driver).

action(action_walk(Driver, Loc_From, Loc_To)) :- driver(Driver), location(Loc_From), location(Loc_To), Loc_From != Loc_To.
cond(cond_exec_walk(Driver, Loc_From, Loc_To)) :- driver(Driver), location(Loc_From), location(Loc_To), Loc_From != Loc_To.
exec(action_walk(Driver, Loc_From, Loc_To), cond_exec_walk(Driver, Loc_From, Loc_To)) :- driver(Driver), location(Loc_From), location(Loc_To), Loc_From != Loc_To.
cond(cond_causes_walk(Driver, Loc_From, Loc_To)) :- driver(Driver), location(Loc_From), location(Loc_To), Loc_From != Loc_To.

% Action Load a truck preconditions
member(at(Truck, Loc), cond_exec_load_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).
member(at(Obj, Loc), cond_exec_load_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).

% Action Load a truck effects
causes(action_load_truck(Obj, Truck, Loc), -at(Obj, Loc), cond_causes_load_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).
causes(action_load_truck(Obj, Truck, Loc), member(Obj, Truck), cond_causes_load_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).

% Action Unload a truck preconditions
member(at(Truck, Loc), cond_exec_unload_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).
member(member(Obj, Truck), cond_exec_unload_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).

% Action Unload a truck effects
causes(action_unload_truck(Obj, Truck, Loc), -member(Obj, Truck), cond_causes_unload_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).
causes(action_unload_truck(Obj, Truck, Loc), at(Obj, Loc), cond_causes_unload_truck(Obj, Truck, Loc)) :- obj(Obj), truck(Truck), location(Loc).

% Action Board a truck preconditions
member(at(Driver, Loc), cond_exec_board_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
member(at(Truck, Loc), cond_exec_board_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
member(empty(Truck), cond_exec_board_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).

% Action Board a truck effects
causes(action_board_truck(Driver, Truck, Loc), driving(Driver, Truck), cond_causes_board_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
causes(action_board_truck(Driver, Truck, Loc), -empty(Truck), cond_causes_board_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
causes(action_board_truck(Driver, Truck, Loc), -at(Driver, Loc), cond_causes_board_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).

% Action Disembark a truck preconditions
member(at(Truck, Loc), cond_exec_disembark_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
member(driving(Driver, Truck), cond_exec_disembark_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).

% Action Disembark a truck effects
causes(action_disembark_truck(Driver, Truck, Loc), -driving(Driver, Truck), cond_causes_disembark_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
causes(action_disembark_truck(Driver, Truck, Loc), at(Driver, Loc), cond_causes_disembark_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).
causes(action_disembark_truck(Driver, Truck, Loc), empty(Truck), cond_causes_disembark_truck(Driver, Truck, Loc)) :- driver(Driver), truck(Truck), location(Loc).

% Action Drive a truck preconditions
member(at(Truck, Loc_From), cond_exec_drive_truck(Truck, Loc_From, Loc_To, Driver)) :- truck(Truck), location(Loc_From), location(Loc_To), Loc_From != Loc_To, driver(Driver).
member(driving(Driver, Truck), cond_exec_drive_truck(Truck, Loc_From, Loc_To, Driver)) :- truck(Truck), location(Loc_From), location(Loc_To), Loc_From != Loc_To, driver(Driver).
member(link(Loc_From, Loc_To), cond_exec_drive_truck(Truck, Loc_From, Loc_To, Driver)) :- truck(Truck), location(Loc_From), location(Loc_To), Loc_From != Loc_To, driver(Driver).

% Action Drive a truck effects
causes(action_drive_truck(Truck, Loc_From, Loc_To, Driver), -at(Truck, Loc_From), cond_causes_drive_truck(Truck, Loc_From, Loc_To, Driver)) :- truck(Truck), location(Loc_From), location(Loc_To), Loc_From != Loc_To, driver(Driver).
causes(action_drive_truck(Truck, Loc_From, Loc_To, Driver), at(Truck, Loc_To), cond_causes_drive_truck(Truck, Loc_From, Loc_To, Driver)) :- truck(Truck), location(Loc_From), location(Loc_To), Loc_From != Loc_To, driver(Driver).

% Action Walk preconditions
member(at(Driver, Loc_From), cond_exec_walk(Driver, Loc_From, Loc_To)) :- driver(Driver), location(Loc_From), location(Loc_To), Loc_From != Loc_To.
member(path(Loc_From, Loc_To), cond_exec_walk(Driver, Loc_From, Loc_To)) :- driver(Driver), location(Loc_From), location(Loc_To), Loc_From != Loc_To.

% Action Walk effects
causes(action_walk(Driver, Loc_From, Loc_To), -at(Driver, Loc_From), cond_causes_walk(Driver, Loc_From, Loc_To)) :- driver(Driver), location(Loc_From), location(Loc_To), Loc_From != Loc_To.
causes(action_walk(Driver, Loc_From, Loc_To), at(Driver, Loc_To), cond_causes_walk(Driver, Loc_From, Loc_To)) :- driver(Driver), location(Loc_From), location(Loc_To), Loc_From != Loc_To.