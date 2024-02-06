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
member(clear(B), cond_exec_pick_up(B)) :- block(B).
member(ontable(B), cond_exec_pick_up(B)) :- block(B).
member(handempty, cond_exec_pick_up(B)) :- block(B).
% Action Pick up effects
causes(action_pick_up(B), -ontable(B), cond_causes_pick_up(B)) :- block(B).
causes(action_pick_up(B), -clear(B), cond_causes_pick_up(B)) :- block(B).
causes(action_pick_up(B), -handempty, cond_causes_pick_up(B)) :- block(B).
causes(action_pick_up(B), holding(B), cond_causes_pick_up(B)) :- block(B).
% Action Put down preconditions
member(holding(B), cond_exec_put_down(B)) :- block(B).
% Action Put down effects
causes(action_put_down(B), -holding(B), cond_causes_put_down(B)) :- block(B).
causes(action_put_down(B), clear(B), cond_causes_put_down(B)) :- block(B).
causes(action_put_down(B), handempty, cond_causes_put_down(B)) :- block(B).
causes(action_put_down(B), ontable(B), cond_causes_put_down(B)) :- block(B).
% Action Stack preconditions
member(holding(B1), cond_exec_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
member(clear(B2), cond_exec_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
% Action Stack effects
causes(action_stack(B1, B2), -holding(B1), cond_causes_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_stack(B1, B2), -clear(B2), cond_causes_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_stack(B1, B2), clear(B1), cond_causes_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_stack(B1, B2), handempty, cond_causes_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_stack(B1, B2), on(B1, B2), cond_causes_stack(B1, B2)) :- block(B1), block(B2), B1 != B2.
% Action Unstack preconditions
member(on(B1, B2), cond_exec_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
member(clear(B1), cond_exec_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
member(handempty, cond_exec_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
% Action Unstack effects
causes(action_unstack(B1, B2), holding(B1), cond_causes_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_unstack(B1, B2), clear(B2), cond_causes_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_unstack(B1, B2), -clear(B1), cond_causes_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_unstack(B1, B2), -handempty, cond_causes_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
causes(action_unstack(B1, B2), -on(B1, B2), cond_causes_unstack(B1, B2)) :- block(B1), block(B2), B1 != B2.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#include <incmode>.
 
fluent(X) :- pfluent(X). 

literal(X) :- fluent(X). 
literal(-X) :- fluent(X).

literal(X) :- dfluent(X). 
literal(-X) :- dfluent(X). 

contrary(X, -X) :- fluent(X). 
contrary(-X, X) :- fluent(X). 

initially(X) :- init(X). 

h(X, 1)   :- initially(X), literal(X). 
h(-X, 1)  :- fluent(X), not init(X). 

max(I) :- I = #max {J : occurs(_, J)}. 
  
#program step(t).

time(t). 

% {occurs(A, t) : action(A)} 1.  

h(X, t) :- define(X, Y), 
	formula(Y, and), 
	#count{Z : member(Z, Y), not h(Z, t)} == 0. 

h(X, t) :- define(X, Y), 
	formula(Y, or), 
	#count{Z : member(Z, Y), h(Z, t)} > 0. 

not_exec(A, t):- action(A), occurs(A, t), not executable(A, t). 

executable(A, t) :-  action(A), 
	     exec(A, S), 
	     #count{Z : literal(Z), member(Z, S), not h(Z, t)} == 0. 

h(X, t) :- action(A), occurs(A, t-1),
         executable(A, t-1),
	     causes(A, X, true). 

h(X, t) :- action(A), occurs(A, t-1),
         executable(A, t-1),
	     causes(A, X, Y),
	     literal(Y), h(Y, t). 

h(X, t) :- action(A), occurs(A, t-1),
         executable(A, t-1),
	     causes(A, X, S),
	     #count{Z : literal(Z), member(Z, S), not h(Z, t)} == 0. 

h(X, t) :- time(t), h(X, t-1), contrary(X, Y), not h(Y, t).  

stop(t) :- occurs(A,t), not_exec(A, t). 

stop(t) :- max(J), t == J+1. 

#program check(t).

:- query(t), not stop(t). 
 
#show.
% #show stop/1.
% #show occurs/2.
#show not_exec/2.
% #show h(X, J) : h(X, J), fluent(X), stop(J).
#show h(-X, J) : h(-X, J), fluent(X), stop(J).
% #show time/1.
% #show max/1.
