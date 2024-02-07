% I have the following types:
object(O) :- location(O).
object(O) :- locatable(O).
locatable(M) :- man(M).
locatable(N) :- nut(N).
locatable(S) :- spanner(S).

% I have the following predicates:
pfluent(at(L, Loc)) :- locatable(L), location(Loc).
pfluent(carrying(M, S)) :- man(M), spanner(S).
pfluent(useable(S)) :- spanner(S).
pfluent(link(L1, L2)) :- location(L1), location(L2), L1!=L2.
pfluent(tightened(N)) :- nut(N).
pfluent(loose(N)) :- nut(N).

% I have the following actions and restrictions:
action(action_walk(Start, End, M)) :- location(Start), location(End), Start!=End, man(M).
cond(cond_exec_walk(Start, End, M)) :- location(Start), location(End), Start!=End, man(M).
exec(action_walk(Start, End, M), cond_exec_walk(Start, End, M)) :- location(Start), location(End), Start!=End, man(M).
cond(cond_causes_walk(Start, End, M)) :- location(Start), location(End), Start!=End, man(M).

action(action_pick_up_spanner(Loc, S, M)) :- location(Loc), spanner(S), man(M).
cond(cond_exec_pick_up_spanner(Loc, S, M)) :- location(Loc), spanner(S), man(M).
exec(action_pick_up_spanner(Loc, S, M), cond_exec_pick_up_spanner(Loc, S, M)) :- location(Loc), spanner(S), man(M).
cond(cond_causes_pick_up_spanner(Loc, S, M)) :- location(Loc), spanner(S), man(M).

action(action_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).
cond(cond_exec_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).
exec(action_tighten_nut(Loc, S, M, N), cond_exec_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).
cond(cond_causes_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).

% Action Walk
member(at(M, Start), cond_exec_walk(Start, End, M)) :- location(Start), location(End), Start!=End, man(M).
member(link(Start, End), cond_exec_walk(Start, End, M)) :- location(Start), location(End), Start!=End, man(M).

causes(action_walk(Start, End, M), -at(M, Start), cond_causes_walk(Start, End, M)) :- location(Start), location(End), Start!=End, man(M).
causes(action_walk(Start, End, M), at(M, End), cond_causes_walk(Start, End, M)) :- location(Start), location(End), Start!=End, man(M).

% Action Pickup Spanner
member(at(M, Loc), cond_exec_pick_up_spanner(Loc, S, M)) :- location(Loc), spanner(S), man(M).
member(at(S, Loc), cond_exec_pick_up_spanner(Loc, S, M)) :- location(Loc), spanner(S), man(M).

causes(action_pick_up_spanner(Loc, S, M), -at(S, Loc), cond_causes_pick_up_spanner(Loc, S, M)) :- location(Loc), spanner(S), man(M).
causes(action_pick_up_spanner(Loc, S, M), carrying(M, S), cond_causes_pick_up_spanner(Loc, S, M)) :- location(Loc), spanner(S), man(M).

% Action Tighten Nut
member(at(M, Loc), cond_exec_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).
member(at(N, Loc), cond_exec_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).
member(carrying(M, S), cond_exec_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).
member(useable(S), cond_exec_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).
member(loose(N), cond_exec_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).

causes(action_tighten_nut(Loc, S, M, N), -loose(N), cond_causes_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).
causes(action_tighten_nut(Loc, S, M, N), -useable(S), cond_causes_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).
causes(action_tighten_nut(Loc, S, M, N), tightened(N), cond_causes_tighten_nut(Loc, S, M, N)) :- location(Loc), spanner(S), man(M), nut(N).