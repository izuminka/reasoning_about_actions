% I have the following types:
object(P) :- passenger(P).
passenger(P) :- passenger(P).
object(F) :- floor(F).
floor(F) :- floor(F).

% I have the following predicates:
pfluent(origmember(P, F)) :- passenger(P), floor(F).
pfluent(destmember(P, F)) :- passenger(P), floor(F).
pfluent(above(F1, F2)) :- floor(F1), floor(F2), F1 != F2.
pfluent(boarded(P)) :- passenger(P).
pfluent(not_boarded(P)) :- passenger(P).
pfluent(served(P)) :- passenger(P).
pfluent(not_served(P)) :- passenger(P).
pfluent(lift_at(F)) :- floor(F).

% I have the following actions and restrictions:
action(action_board(F, P)) :- floor(F), passenger(P).
cond(cond_exec_board(F, P)) :- floor(F), passenger(P).
exec(action_board(F, P), cond_exec_board(F, P)) :- floor(F), passenger(P).
cond(cond_causes_board(F, P)) :- floor(F), passenger(P).

action(action_depart(F, P)) :- floor(F), passenger(P).
cond(cond_exec_depart(F, P)) :- floor(F), passenger(P).
exec(action_depart(F, P), cond_exec_depart(F, P)) :- floor(F), passenger(P).
cond(cond_causes_depart(F, P)) :- floor(F), passenger(P).

action(action_up(F1, F2)) :- floor(F1), floor(F2), F1 != F2.
cond(cond_exec_up(F1, F2)) :- floor(F1), floor(F2), F1 != F2.
exec(action_up(F1, F2), cond_exec_up(F1, F2)) :- floor(F1), floor(F2), F1 != F2.
cond(cond_causes_up(F1, F2)) :- floor(F1), floor(F2), F1 != F2.

action(action_down(F1, F2)) :- floor(F1), floor(F2), F1 != F2.
cond(cond_exec_down(F1, F2)) :- floor(F1), floor(F2), F1 != F2.
exec(action_down(F1, F2), cond_exec_down(F1, F2)) :- floor(F1), floor(F2), F1 != F2.
cond(cond_causes_down(F1, F2)) :- floor(F1), floor(F2), F1 != F2.

member(lift_at(F), cond_exec_board(F, P)) :- floor(F), passenger(P).
member(origmember(P, F), cond_exec_board(F, P)) :- floor(F), passenger(P).

causes(action_board(F, P), boarded(P), cond_causes_board(F, P)) :- floor(F), passenger(P).

member(lift_at(F), cond_exec_depart(F, P)) :- floor(F), passenger(P).
member(destmember(P, F), cond_exec_depart(F, P)) :- floor(F), passenger(P).
member(boarded(P), cond_exec_depart(F, P)) :- floor(F), passenger(P).

causes(action_depart(F, P), -boarded(P), cond_causes_depart(F, P)) :- floor(F), passenger(P).
causes(action_depart(F, P), served(P), cond_causes_depart(F, P)) :- floor(F), passenger(P).

member(lift_at(F1), cond_exec_up(F1, F2)) :- floor(F1), floor(F2), F1 != F2.
member(above(F1, F2), cond_exec_up(F1, F2)) :- floor(F1), floor(F2), F1 != F2.

causes(action_up(F1, F2), -lift_at(F1), cond_causes_up(F1, F2)) :- floor(F1), floor(F2), F1 != F2.
causes(action_up(F1, F2), lift_at(F2), cond_causes_up(F1, F2)) :- floor(F1), floor(F2), F1 != F2.

member(lift_at(F1), cond_exec_down(F1, F2)) :- floor(F1), floor(F2), F1 != F2.
member(above(F2, F1), cond_exec_down(F1, F2)) :- floor(F1), floor(F2), F1 != F2.

causes(action_down(F1, F2), -lift_at(F1), cond_causes_down(F1, F2)) :- floor(F1), floor(F2), F1 != F2.
causes(action_down(F1, F2), lift_at(F2), cond_causes_down(F1, F2)) :- floor(F1), floor(F2), F1 != F2.