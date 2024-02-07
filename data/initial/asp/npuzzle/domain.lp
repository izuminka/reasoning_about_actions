% I have the following predicates:
pfluent(at(T, P)) :- tile(T), position(P).
pfluent(neighbor(P1, P2)) :- position(P1), position(P2), P1 != P2.
pfluent(empty(P)) :- position(P).

% I have the following actions and restrictions:
action(action_move(T, Src, Dest)) :- tile(T), position(Src), position(Dest), Src != Dest.
cond(cond_exec_move(T, Src, Dest)) :- tile(T), position(Src), position(Dest), Src != Dest.
exec(action_move(T, Src, Dest), cond_exec_move(T, Src, Dest)) :- tile(T), position(Src), position(Dest), Src != Dest.
cond(cond_causes_move(T, Src, Dest)) :- tile(T), position(Src), position(Dest), Src != Dest.

member(neighbor(Src, Dest), cond_exec_move(T, Src, Dest)) :- tile(T), position(Src), position(Dest), Src != Dest.
member(at(T, Src), cond_exec_move(T, Src, Dest)) :- tile(T), position(Src), position(Dest), Src != Dest.
member(empty(Dest), cond_exec_move(T, Src, Dest)) :- tile(T), position(Src), position(Dest), Src != Dest.

causes(action_move(T, Src, Dest), at(T, Dest), cond_causes_move(T, Src, Dest)) :- tile(T), position(Src), position(Dest), Src != Dest.
causes(action_move(T, Src, Dest), empty(Src), cond_causes_move(T, Src, Dest)) :- tile(T), position(Src), position(Dest), Src != Dest.
causes(action_move(T, Src, Dest), -at(T, Src), cond_causes_move(T, Src, Dest)) :- tile(T), position(Src), position(Dest), Src != Dest.
causes(action_move(T, Src, Dest), -empty(Dest), cond_causes_move(T, Src, Dest)) :- tile(T), position(Src), position(Dest), Src != Dest.