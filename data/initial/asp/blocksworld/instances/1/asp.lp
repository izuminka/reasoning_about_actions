% GENERAL -------------------- 

nfluent(neg(X)) :- pfluent(X).
fluent(X) :- pfluent(X).
fluent(X) :- nfluent(X).

%General support for actions and exec
holds(F, T+1) :- time(T), action(A), fluent(F), cond(C), causes(A,F,C), occurs(A,T), all_holds(C,T).
not_all_holds(C,T) :- time(T), cond(C), fluent(P), in (P, C), not holds(P,T).
all_holds(C,T) :- time(T), cond(C), not not_all_holds(C,T).
executable(A,T) :- time(T), action(A), cond(C), exec(A,C), all_holds(C,T).
:- time(T), action(A), occurs(A,T), not executable(A,T).
holds(F, T+1) :- holds(F,T), not holds(neg(F), T+1), pfluent(F), time(T).
holds(neg(F), T+1) :- holds(neg(F),T), not holds(F, T+1), pfluent(F), time(T).

% Time iteration for indefinite time
% init and goal definitions
time(0..30).
not_exit(T) :- time(T), goal(F), fluent(F), not holds(F,T).  % Goal is not true in time T, if there is a goal F and it is not true in T.
exit(T) :- time(T), not not_exit(T).
done_time(T) :- time(T), exit(T).
1 { occurs(A,T) : action(A) } 1:- time(T), not done_time(T).
exit :- time(T), exit(T).
:- not exit.

#minimize{1,A, T:occurs(A, T)}.

holds(C,0) :- init(C).

% Output
#show occurs/2.


% DOMAIN  --------------------

% I have the following types:
object(B) :- block(B).
block(B) :- block(B).

% I have the following predicates:
pfluent(on(B1, B2)) :- block(B1), block(B2), B1 != B2.
pfluent(ontable(B)) :- block(B).
pfluent(clear(B)) :- block(B).
pfluent(handempty).
pfluent(holding(B)) :- block(B).

% I have the following actions and restrictions:
action(action_pick_up(B)) :- block(B).
cond(cond_exec_pick_up(B)) :- block(B).
exec(action_pick_up(B), cond_exec_pick_up(B)) :- block(B).
cond(cond_causes_pick_up(B)) :- block(B).

action(action_put_down(B)) :- block(B).
cond(cond_exec_put_down(B)) :- block(B).
exec(action_put_down(B), cond_exec_put_down(B)) :- block(B).
cond(cond_causes_put_down(B)) :- block(B).

action(action_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
cond(cond_exec_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
exec(action_stack(B1, B2), cond_exec_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
cond(cond_causes_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.

action(action_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
cond(cond_exec_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
exec(action_unstack(B1, B2), cond_exec_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
cond(cond_causes_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.

% Action Pick up preconditions
in(clear(B), cond_exec_pick_up(B)) :- block(B).
in(ontable(B), cond_exec_pick_up(B)) :- block(B).
in(handempty, cond_exec_pick_up(B)) :- block(B).

% Action Pick up effects
causes(action_pick_up(B), neg(ontable(B)), cond_causes_pick_up(B)) :- block(B).
causes(action_pick_up(B), neg(clear(B)), cond_causes_pick_up(B)) :- block(B).
causes(action_pick_up(B), neg(handempty), cond_causes_pick_up(B)) :- block(B).
causes(action_pick_up(B), holding(B), cond_causes_pick_up(B)) :- block(B).

% Action Put down preconditions
in(holding(B), cond_exec_put_down(B)) :- block(B).

% Action Put down effects
causes(action_put_down(B), neg(holding(B)), cond_causes_put_down(B)) :- block(B).
causes(action_put_down(B), clear(B), cond_causes_put_down(B)) :- block(B).
causes(action_put_down(B), handempty, cond_causes_put_down(B)) :- block(B).
causes(action_put_down(B), ontable(B), cond_causes_put_down(B)) :- block(B).

% Action Stack preconditions
in(holding(B1), cond_exec_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
in(clear(B2), cond_exec_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.

% Action Stack effects
causes(action_stack(B1, B2), neg(holding(B1)), cond_causes_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_stack(B1, B2), neg(clear(B2)), cond_causes_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_stack(B1, B2), clear(B1), cond_causes_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_stack(B1, B2), handempty, cond_causes_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_stack(B1, B2), on(B1, B2), cond_causes_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.

% Action Unstack preconditions
in(on(B1, B2), cond_exec_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
in(clear(B1), cond_exec_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
in(handempty, cond_exec_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.

% Action Unstack effects
causes(action_unstack(B1, B2), holding(B1), cond_causes_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_unstack(B1, B2), clear(B2), cond_causes_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_unstack(B1, B2), neg(clear(B1)), cond_causes_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_unstack(B1, B2), neg(handempty), cond_causes_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_unstack(B1, B2), neg(on(B1, B2)), cond_causes_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.

%INIT/GOAL --------------------

% Objects:
block(b1; b2; b3; b4; b5; b6; b7; b8; b9).

% Initial State:
init(handempty;
on(b1, b9);
on(b2, b6);
on(b3, b2);
on(b4, b7);
ontable(b5);
on(b6, b8);
ontable(b7);
on(b8, b4);
ontable(b9);
clear(b1);
clear(b3);
clear(b5)).

% Goal State:
goal(on(b2, b6);
on(b3, b8);
on(b4, b1);
on(b5, b2);
on(b6, b9);
on(b7, b4);
on(b8, b7)).