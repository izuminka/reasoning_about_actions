% I have the following types:
object(O) :- aircraft(O).
object(O) :- person(O).
object(O) :- city(O).
object(O) :- flevel(O).

% I have the following predicates:
pfluent(at(P, C)) :- person(P), city(C).
pfluent(at(A, C)) :- aircraft(A), city(C).
pfluent(in(P, A)) :- person(P), aircraft(A).
pfluent(fuel_level(A, F)) :- aircraft(A), flevel(F).
pfluent(next(F1, F2)) :- flevel(F1), flevel(F2), F1!=F2.

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

causes(action_board(P, A, C), -at(P, C), cond_causes_board(P, A, C)) :- person(P), aircraft(A), city(C).
causes(action_board(P, A, C), in(P, A), cond_causes_board(P, A, C)) :- person(P), aircraft(A), city(C).

member(in(P, A), cond_exec_debark(P, A, C)) :- person(P), aircraft(A), city(C).
member(at(A, C), cond_exec_debark(P, A, C)) :- person(P), aircraft(A), city(C).

causes(action_debark(P, A, C), -in(P, A), cond_causes_debark(P, A, C)) :- person(P), aircraft(A), city(C).
causes(action_debark(P, A, C), at(P, A), cond_causes_debark(P, A, C)) :- person(P), aircraft(A), city(C).

member(at(A, C1), cond_exec_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.
member(fuel_level(A, F1), cond_exec_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.
member(next(F2, F1), cond_exec_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.

causes(action_fly(A, C1, F1, C2, F2), -at(A, C1), cond_causes_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.
causes(action_fly(A, C1, F1, C2, F2), at(A, C2), cond_causes_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.
causes(action_fly(A, C1, F1, C2, F2), -fuel_level(A, F1), cond_causes_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.
causes(action_fly(A, C1, F1, C2, F2), fuel_level(A, F2), cond_causes_fly(A, C1, F1, C2, F2)) :- aircraft(A), city(C1), flevel(F1), city(C2), C1 != C2, flevel(F2), F1!=F2.

member(at(A, C1), cond_exec_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
member(fuel_level(A, F1), cond_exec_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
member(next(F2, F1), cond_exec_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
member(next(F3, F2), cond_exec_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.

causes(action_zoom(A, C1, C2, F1, F2, F3), -at(A, C1), cond_causes_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
causes(action_zoom(A, C1, C2, F1, F2, F3), at(A, C2), cond_causes_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
causes(action_zoom(A, C1, C2, F1, F2, F3), -fuel_level(A, F1), cond_causes_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.
causes(action_zoom(A, C1, C2, F1, F2, F3), fuel_level(A, F3), cond_causes_zoom(A, C1, C2, F1, F2, F3)) :- aircraft(A), city(C1), city(C2), C1 != C2, flevel(F1), flevel(F2), F1!=F2, flevel(F3), F1!=F3, F2!=F3.

member(at(A, C), cond_exec_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.
member(fuel_level(A, F1), cond_exec_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.
member(next(F1, F2), cond_exec_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.

causes(action_refuel(A, C, F1, F2), fuel_level(A, F2), cond_causes_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.
causes(action_refuel(A, C, F1, F2), -fuel_level(A, F1), cond_causes_refuel(A, C, F1, F2)) :- aircraft(A), city(C), flevel(F1), flevel(F2), F1!=F2.
