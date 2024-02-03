% I have the following types:
object(O) :- space(O).
space(O) :- space(O).
object(O) :- fuel(O).
fuel(O) :- fuel(O).
object(O) :- location(O).
location(O) :- location(O).
object(O) :- movable(O).
movable(O) :- movable(O).
movable(V) :- vehicle(V).
vehicle(V) :- vehicle(V).
movable(C) :- cargo(C).
cargo(C) :- cargo(C).

% I have the following predicates:
pfluent(at(M, L)) :- movable(M), location(L).
pfluent(conn(L1, L2)) :- location(L1), location(L2), L1 != L2.
pfluent(has_fuel(L, F)) :- location(L), fuel(F).
pfluent(fuel_neighbor(F1, F2)) :- fuel(F1), fuel(F2), F1 != F2.
pfluent(member(C, V)) :- cargo(C), vehicle(V).
pfluent(has_space(V, S)) :- vehicle(V), space(S).
pfluent(space_neighbor(S1, S2)) :- space(S1), space(S2), S1 != S2.

% I have the following actions and restrictions:
action(action_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.
cond(cond_exec_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.
exec(action_move(V, L1, L2, F1, F2), cond_exec_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.
cond(cond_causes_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.

action(action_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
cond(cond_exec_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
exec(action_load(C, V, L, S1, S2), cond_exec_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
cond(cond_causes_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.

action(action_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
cond(cond_exec_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
exec(action_unload(C, V, L, S1, S2), cond_exec_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
cond(cond_causes_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.

% Action Move preconditions and effects:
member(at(V, L1), cond_exec_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.
member(conn(L1, L2), cond_exec_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.
member(has_fuel(L1, F1), cond_exec_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.
member(fuel_neighbor(F1, F2), cond_exec_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.

causes(action_move(V, L1, L2, F1, F2), -at(V, L1), cond_causes_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.
causes(action_move(V, L1, L2, F1, F2), at(V, L2), cond_causes_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.
causes(action_move(V, L1, L2, F1, F2), -has_fuel(L1, F1), cond_causes_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.
causes(action_move(V, L1, L2, F1, F2), has_fuel(L1, F2), cond_causes_move(V, L1, L2, F1, F2)) :- vehicle(V), location(L1), location(L2), L1 != L2, fuel(F1), fuel(F2), F1 != F2.

% Action Load preconditions and effects:
member(at(C, L), cond_exec_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
member(at(V, L), cond_exec_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
member(has_space(V, S1), cond_exec_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
member(space_neighbor(S1, S2), cond_exec_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.

causes(action_load(C, V, L, S1, S2), -at(C, L), cond_causes_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
causes(action_load(C, V, L, S1, S2), member(C, V), cond_causes_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
causes(action_load(C, V, L, S1, S2), -has_space(V, S1), cond_causes_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
causes(action_load(C, V, L, S1, S2), has_space(V, S2), cond_causes_load(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.

% Action Unload preconditions and effects:
member(member(C, V), cond_exec_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
member(at(V, L), cond_exec_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
member(has_space(V, S1), cond_exec_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
member(space_neighbor(S1, S2), cond_exec_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.

causes(action_unload(C, V, L, S1, S2), -member(C, V), cond_causes_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
causes(action_unload(C, V, L, S1, S2), at(C, L), cond_causes_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
causes(action_unload(C, V, L, S1, S2), -has_space(V, S1), cond_causes_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.
causes(action_unload(C, V, L, S1, S2), has_space(V, S2), cond_causes_unload(C, V, L, S1, S2)) :- cargo(C), vehicle(V), location(L), space(S1), space(S2), S1 != S2.