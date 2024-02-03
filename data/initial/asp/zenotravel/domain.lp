% I have the following types:
object(O) :- aircraft(O).
aircraft(O) :- aircraft(O).
object(O) :- person(O).
person(O) :- person(O).
object(O) :- city(O).
city(O) :- city(O).
flevel(F) :- flevel(F).

% I have the following predicates:
pfluent(at(O, C)) :- object(O), city(C).
pfluent(member(P, A)) :- person(P), aircraft(A).
pfluent(fuel_level(A, F)) :- aircraft(A), flevel(F).
pfluent(next_flevel(F1, F2)) :- flevel(F1), flevel(F2), F1!=F2.

% I have the following actions and restrictions:
action(action_board(P, A, C)) :- person(P), aircraft(A), city(C).
cond(cond_exec_board(P, A, C)) :- person(P), aircraft(A), city(C).
exec(action_board(P, A, C), cond_exec_board(P, A, C)) :- person(P), aircraft(A), city(C).
cond(cond_causes_board(P, A, C)) :- person(P), aircraft(A), city(C).

action(action_debark(P, A, C)) :- person(P), aircraft(A), city(C).
cond(cond_exec_debark(P, A, C)) :- person(P), aircraft(A), city(C).
exec(action_debark(P, A, C), cond_exec_debark(P, A, C)) :- person(P), aircraft(A), city(C).
cond(cond_causes_debark(P, A, C)) :- person(P), aircraft(A), city(C).

action(action_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.
cond(cond_exec_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.
exec(action_fly(A, C1, F1, C2, F2), cond_exec_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.
cond(cond_causes_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.

action(action_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
cond(cond_exec_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
exec(action_zoom(A, C1, C2, F1, F2, F3), cond_exec_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
cond(cond_causes_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.

action(action_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.
cond(cond_exec_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.
exec(action_refuel(A, C, F1, F2), cond_exec_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.
cond(cond_causes_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.

% Preconditions and Effects:
member(at(P, C), cond_exec_board(P, A, C)) :- person(P), aircraft(A), city(C).
member(at(A, C), cond_exec_board(P, A, C)) :- person(P), aircraft(A), city(C).

member(member(P, A), cond_exec_debark(P, A, C)) :- person(P), aircraft(A), city(C).
member(at(A, C), cond_exec_debark(P, A, C)) :- person(P), aircraft(A), city(C).

member(at(A, C1), cond_exec_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.
member(fuel_level(A, F1), cond_exec_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.
member(next_flevel(F2, F1), cond_exec_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.

member(at(A, C1), cond_exec_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
member(fuel_level(A, F1), cond_exec_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
member(next_flevel(F2, F1), cond_exec_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
member(next_flevel(F3, F2), cond_exec_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.

member(at(A, C), cond_exec_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.
member(fuel_level(A, F1), cond_exec_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.
member(next_flevel(F2, F1), cond_exec_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.