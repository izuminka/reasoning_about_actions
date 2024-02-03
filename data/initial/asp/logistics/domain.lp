% I have the following types:
vehicle(V) :- truck(V).
truck(V) :- truck(V).
vehicle(V) :- airplane(V).
airplane(V) :- airplane(V).
physobj(P) :- package(P).
package(P) :- package(P).
physobj(P) :- vehicle(P).
place(P) :- airport(P).
airport(P) :- airport(P).
place(P) :- location(P).
location(P) :- location(P).
object(O) :- city(O).
city(O) :- city(O).
object(O) :- place(O).
object(O) :- physobj(O).

% I have the following predicates:
pfluent(in_city(P, C)) :- place(P), city(C).
pfluent(at(PH, P)) :- physobj(PH), place(P).
pfluent(member(P, V)) :- package(P), vehicle(V).

% I have the following actions and restrictions:
action(action_load_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).
cond(cond_exec_load_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).
exec(action_load_truck(Pkg, Truck, Loc), cond_exec_load_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).
cond(cond_causes_load_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).

action(action_load_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).
cond(cond_exec_load_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).
exec(action_load_airplane(Pkg, Airplane, Loc), cond_exec_load_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).
cond(cond_causes_load_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).

action(action_unload_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).
cond(cond_exec_unload_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).
exec(action_unload_truck(Pkg, Truck, Loc), cond_exec_unload_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).
cond(cond_causes_unload_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).

action(action_unload_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).
cond(cond_exec_unload_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).
exec(action_unload_airplane(Pkg, Airplane, Loc), cond_exec_unload_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).
cond(cond_causes_unload_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).

action(action_drive_truck(Truck, Loc_From, Loc_To, City)) :- truck(Truck), place(Loc_From), place(Loc_To), Loc_From!=Loc_To, city(City).
cond(cond_exec_drive_truck(Truck, Loc_From, Loc_To, City)) :- truck(Truck), place(Loc_From), place(Loc_To), Loc_From!=Loc_To, city(City).
exec(action_drive_truck(Truck, Loc_From, Loc_To, City), cond_exec_drive_truck(Truck, Loc_From, Loc_To, City)) :- truck(Truck), place(Loc_From), place(Loc_To), Loc_From!=Loc_To, city(City).
cond(cond_causes_drive_truck(Truck, Loc_From, Loc_To, City)) :- truck(Truck), place(Loc_From), place(Loc_To), Loc_From!=Loc_To, city(City).

action(action_fly_airplane(Airplane, Airport_From, Airport_To)) :- airplane(Airplane), airport(Airport_From), airport(Airport_To), Airport_From!=Airport_To.
cond(cond_exec_fly_airplane(Airplane, Airport_From, Airport_To)) :- airplane(Airplane), airport(Airport_From), airport(Airport_To), Airport_From!=Airport_To.
exec(action_fly_airplane(Airplane, Airport_From, Airport_To), cond_exec_fly_airplane(Airplane, Airport_From, Airport_To)) :- airplane(Airplane), airport(Airport_From), airport(Airport_To), Airport_From!=Airport_To.
cond(cond_causes_fly_airplane(Airplane, Airport_From, Airport_To)) :- airplane(Airplane), airport(Airport_From), airport(Airport_To), Airport_From!=Airport_To.

% Action Load a truck preconditions:
member(at(Truck, Loc), cond_exec_load_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).
member(at(Pkg, Loc), cond_exec_load_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).

% Action Load a truck effects:
causes(action_load_truck(Pkg, Truck, Loc), -at(Pkg, Loc), cond_causes_load_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).
causes(action_load_truck(Pkg, Truck, Loc), member(Pkg, Truck), cond_causes_load_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).

% Action Load an airplane preconditions:
member(at(Airplane, Loc), cond_exec_load_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).
member(at(Pkg, Loc), cond_exec_load_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).

% Action Load an airplane effects:
causes(action_load_airplane(Pkg, Airplane, Loc), -at(Pkg, Loc), cond_causes_load_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).
causes(action_load_airplane(Pkg, Airplane, Loc), member(Pkg, Airplane), cond_causes_load_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).

% Action Unload a truck preconditions:
member(at(Truck, Loc), cond_exec_unload_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).
member(member(Pkg, Truck), cond_exec_unload_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).

% Action Unload a truck effects:
causes(action_unload_truck(Pkg, Truck, Loc), -member(Pkg, Truck), cond_causes_unload_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).
causes(action_unload_truck(Pkg, Truck, Loc), at(Pkg, Loc), cond_causes_unload_truck(Pkg, Truck, Loc)) :- package(Pkg), truck(Truck), place(Loc).

% Action Unload an airplane preconditions:
member(at(Airplane, Loc), cond_exec_unload_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).
member(member(Pkg, Airplane), cond_exec_unload_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).

% Action Unload an airplane effects:
causes(action_unload_airplane(Pkg, Airplane, Loc), -member(Pkg, Airplane), cond_causes_unload_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).
causes(action_unload_airplane(Pkg, Airplane, Loc), at(Pkg, Loc), cond_causes_unload_airplane(Pkg, Airplane, Loc)) :- package(Pkg), airplane(Airplane), place(Loc).

% Action Drive a truck preconditions:
member(at(Truck, Loc_From), cond_exec_drive_truck(Truck, Loc_From, Loc_To, City)) :- truck(Truck), place(Loc_From), place(Loc_To), Loc_From!=Loc_To, city(City).
member(in_city(Loc_From, City), cond_exec_drive_truck(Truck, Loc_From, Loc_To, City)) :- truck(Truck), place(Loc_From), place(Loc_To), Loc_From!=Loc_To, city(City).
member(in_city(Loc_To, City), cond_exec_drive_truck(Truck, Loc_From, Loc_To, City)) :- truck(Truck), place(Loc_From), place(Loc_To), Loc_From!=Loc_To, city(City).

% Action Drive a truck effects:
causes(action_drive_truck(Truck, Loc_From, Loc_To, City), -at(Truck, Loc_From), cond_causes_drive_truck(Truck, Loc_From, Loc_To, City)) :- truck(Truck), place(Loc_From), place(Loc_To), Loc_From!=Loc_To, city(City).
causes(action_drive_truck(Truck, Loc_From, Loc_To, City), at(Truck, Loc_To), cond_causes_drive_truck(Truck, Loc_From, Loc_To, City)) :- truck(Truck), place(Loc_From), place(Loc_To), Loc_From!=Loc_To, city(City).

% Action Fly an airplane preconditions:
member(at(Airplane, Airport_From), cond_exec_fly_airplane(Airplane, Airport_From, Airport_To)) :- airplane(Airplane), airport(Airport_From), airport(Airport_To), Airport_From!=Airport_To.

% Action Fly an airplane effects:
causes(action_fly_airplane(Airplane, Airport_From, Airport_To), -at(Airplane, Airport_From), cond_causes_fly_airplane(Airplane, Airport_From, Airport_To)) :- airplane(Airplane), airport(Airport_From), airport(Airport_To), Airport_From!=Airport_To.
causes(action_fly_airplane(Airplane, Airport_From, Airport_To), at(Airplane, Airport_To), cond_causes_fly_airplane(Airplane, Airport_From, Airport_To)) :- airplane(Airplane), airport(Airport_From), airport(Airport_To), Airport_From!=Airport_To.