% I have the following types:
object(O) :- place(O).
place(O) :- place(O).
object(O) :- locatable(O).
locatable(O) :- locatable(O).
place(P) :- depot(P).
depot(P) :- depot(P).
place(P) :- distributor(P).
distributor(P) :- distributor(P).
locatable(T) :- truck(T).
truck(T) :- truck(T).
locatable(H) :- hoist(H).
hoist(H) :- hoist(H).
locatable(S) :- surface(S).
surface(S) :- surface(S).
surface(P) :- pallet(P).
pallet(P) :- pallet(P).
surface(C) :- crate(C).
crate(C) :- crate(C).

% I have the following predicates:
pfluent(at(L, P)) :- locatable(L), place(P).
pfluent(on(C, S)) :- crate(C), surface(S).
pfluent(member(C, T)) :- crate(C), truck(T).
pfluent(lifting(H, C)) :- hoist(H), crate(C).
pfluent(available(H)) :- hoist(H).
pfluent(clear(S)) :- surface(S).

% I have the following actions and restrictions:
action(action_drive(T, P_From, P_To)) :- truck(T), place(P_From), place(P_To), P_From != P_To.
cond(cond_exec_drive(T, P_From, P_To)) :- truck(T), place(P_From), place(P_To), P_From != P_To.
exec(action_drive(T, P_From, P_To), cond_exec_drive(T, P_From, P_To)) :- truck(T), place(P_From), place(P_To), P_From != P_To.
cond(cond_causes_drive(T, P_From, P_To)) :- truck(T), place(P_From), place(P_To), P_From != P_To.

action(action_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
cond(cond_exec_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
exec(action_lift(H, C, S, P), cond_exec_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
cond(cond_causes_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).

action(action_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
cond(cond_exec_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
exec(action_drop(H, C, S, P), cond_exec_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
cond(cond_causes_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).

action(action_load(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
cond(cond_exec_load(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
exec(action_load(H, C, T, P), cond_exec_load(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
cond(cond_causes_load(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).

action(action_unload(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
cond(cond_exec_unload(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
exec(action_unload(H, C, T, P), cond_exec_unload(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
cond(cond_causes_unload(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).

% Action Drive preconditions and effects:
member(at(T, P_From), cond_exec_drive(T, P_From, P_To)) :- truck(T), place(P_From), place(P_To), P_From != P_To.
causes(action_drive(T, P_From, P_To), -at(T, P_From), cond_causes_drive(T, P_From, P_To)) :- truck(T), place(P_From), place(P_To), P_From != P_To.
causes(action_drive(T, P_From, P_To), at(T, P_To), cond_causes_drive(T, P_From, P_To)) :- truck(T), place(P_From), place(P_To), P_From != P_To.

% Action Lift preconditions and effects:
member(at(H, P), cond_exec_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
member(available(H), cond_exec_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
member(at(C, P), cond_exec_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
member(on(C, S), cond_exec_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
member(clear(C), cond_exec_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).

causes(action_lift(H, C, S, P), -at(C, P), cond_causes_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
causes(action_lift(H, C, S, P), lifting(H, C), cond_causes_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
causes(action_lift(H, C, S, P), -clear(C), cond_causes_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
causes(action_lift(H, C, S, P), -available(H), cond_causes_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
causes(action_lift(H, C, S, P), clear(S), cond_causes_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
causes(action_lift(H, C, S, P), -on(C, S), cond_causes_lift(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).

% Action Drop preconditions and effects:
member(at(H, P), cond_exec_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
member(at(S, P), cond_exec_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
member(clear(S), cond_exec_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
member(lifting(H, C), cond_exec_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).

causes(action_drop(H, C, S, P), available(H), cond_causes_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
causes(action_drop(H, C, S, P), -lifting(H, C), cond_causes_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
causes(action_drop(H, C, S, P), at(C, P), cond_causes_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
causes(action_drop(H, C, S, P), -clear(S), cond_causes_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
causes(action_drop(H, C, S, P), clear(C), cond_causes_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).
causes(action_drop(H, C, S, P), on(C, S), cond_causes_drop(H, C, S, P)) :- hoist(H), crate(C), surface(S), place(P).

% Action Load preconditions and effects:
member(at(H, P), cond_exec_load(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
member(at(T, P), cond_exec_load(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
member(lifting(H, C), cond_exec_load(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).

causes(action_load(H, C, T, P), -lifting(H, C), cond_causes_load(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
causes(action_load(H, C, T, P), member(C, T), cond_causes_load(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
causes(action_load(H, C, T, P), available(H), cond_causes_load(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).

% Action Unload preconditions and effects:
member(at(H, P), cond_exec_unload(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
member(at(T, P), cond_exec_unload(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
member(available(H), cond_exec_unload(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
member(member(C, T), cond_exec_unload(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).

causes(action_unload(H, C, T, P), -member(C, T), cond_causes_unload(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
causes(action_unload(H, C, T, P), -available(H), cond_causes_unload(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).
causes(action_unload(H, C, T, P), lifting(H, C), cond_causes_unload(H, C, T, P)) :- hoist(H), crate(C), truck(T), place(P).