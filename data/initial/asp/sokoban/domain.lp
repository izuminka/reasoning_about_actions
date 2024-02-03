% I have the following types:
loc(L) :- loc(L).
dir(D) :- dir(D).
box(B) :- box(B).

% I have the following predicates:
pfluent(at_robot(L)) :- loc(L).
pfluent(at(B, L)) :- box(B), loc(L).
pfluent(adjacent(L1, L2, D)) :- loc(L1), loc(L2), L1 != L2, dir(D).
pfluent(clear(L)) :- loc(L).

% I have the following actions and restrictions:
action(action_move(Start_loc, End_loc, Dir)) :- loc(Start_loc), loc(End_loc), Start_loc != End_loc, dir(Dir).
cond(cond_exec_move(Start_loc, End_loc, Dir)) :- loc(Start_loc), loc(End_loc), Start_loc != End_loc, dir(Dir).
exec(action_move(Start_loc, End_loc, Dir), cond_exec_move(Start_loc, End_loc, Dir)) :- loc(Start_loc), loc(End_loc), Start_loc != End_loc, dir(Dir).
cond(cond_causes_move(Start_loc, End_loc, Dir)) :- loc(Start_loc), loc(End_loc), Start_loc != End_loc, dir(Dir).

action(action_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
cond(cond_exec_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
exec(action_push(R_loc, B_loc, F_loc, Dir, B), cond_exec_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
cond(cond_causes_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).

% Action Move preconditions
member(clear(End_loc), cond_exec_move(Start_loc, End_loc, Dir)) :- loc(Start_loc), loc(End_loc), Start_loc != End_loc, dir(Dir).
member(at_robot(Start_loc), cond_exec_move(Start_loc, End_loc, Dir)) :- loc(Start_loc), loc(End_loc), Start_loc != End_loc, dir(Dir).
member(adjacent(Start_loc, End_loc, Dir), cond_exec_move(Start_loc, End_loc, Dir)) :- loc(Start_loc), loc(End_loc), Start_loc != End_loc, dir(Dir).

% Action Move effects
causes(action_move(Start_loc, End_loc, Dir), at_robot(End_loc), cond_causes_move(Start_loc, End_loc, Dir)) :- loc(Start_loc), loc(End_loc), Start_loc != End_loc, dir(Dir).
causes(action_move(Start_loc, End_loc, Dir), -at_robot(Start_loc), cond_causes_move(Start_loc, End_loc, Dir)) :- loc(Start_loc), loc(End_loc), Start_loc != End_loc, dir(Dir).

% Action Push preconditions
member(at_robot(R_loc), cond_exec_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
member(at(B, B_loc), cond_exec_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
member(clear(F_loc), cond_exec_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
member(adjacent(R_loc, B_loc, Dir), cond_exec_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
member(adjacent(B_loc, F_loc, Dir), cond_exec_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).

% Action Push effects
causes(action_push(R_loc, B_loc, F_loc, Dir, B), at_robot(B_loc), cond_causes_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
causes(action_push(R_loc, B_loc, F_loc, Dir, B), at(B, F_loc), cond_causes_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
causes(action_push(R_loc, B_loc, F_loc, Dir, B), clear(B_loc), cond_causes_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
causes(action_push(R_loc, B_loc, F_loc, Dir, B), -at_robot(R_loc), cond_causes_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
causes(action_push(R_loc, B_loc, F_loc, Dir, B), -at(B, B_loc), cond_causes_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).
causes(action_push(R_loc, B_loc, F_loc, Dir, B), -clear(F_loc), cond_causes_push(R_loc, B_loc, F_loc, Dir, B)) :- loc(R_loc), loc(B_loc), R_loc != B_loc, loc(F_loc), B_loc != F_loc, R_loc != F_loc, dir(Dir), box(B).