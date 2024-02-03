% I have the following types:
object(P) :- place(P).
place(P) :- place(P).

% I have the following predicates:
pfluent(connected(P1, P2)) :- place(P1), place(P2), P1 != P2.
pfluent(at_robot(P)) :- place(P).
pfluent(visited(P)) :- place(P).

% I have the following actions and restrictions:
action(action_move(P1, P2)) :- place(P1), place(P2), P1 != P2.
cond(cond_exec_move(P1, P2)) :- place(P1), place(P2), P1 != P2.
exec(action_move(P1, P2), cond_exec_move(P1, P2)) :- place(P1), place(P2), P1 != P2.
cond(cond_causes_move(P1, P2)) :- place(P1), place(P2), P1 != P2.

member(at_robot(P1), cond_exec_move(P1, P2)) :- place(P1), place(P2), P1 != P2.
member(connected(P1, P2), cond_exec_move(P1, P2)) :- place(P1), place(P2), P1 != P2.

causes(action_move(P1, P2), -at_robot(P1), cond_causes_move(P1, P2)) :- place(P1), place(P2), P1 != P2.
causes(action_move(P1, P2), at_robot(P2), cond_causes_move(P1, P2)) :- place(P1), place(P2), P1 != P2.
causes(action_move(P1, P2), visited(P2), cond_causes_move(P1, P2)) :- place(P1), place(P2), P1 != P2.