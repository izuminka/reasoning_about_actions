#include <incmode>.
 
fluent(X) :- pfluent(X). 

literal(X) :- fluent(X). 
literal(-X) :- fluent(X).

literal(X) :- dfluent(X). 
literal(-X) :- dfluent(X). 

contrary(X, -X) :- fluent(X). 
contrary(-X, X) :- fluent(X). 

curr(X) :- current_state(X).
h(X, 1)   :- curr(X), literal(X).
h(-X, 1)  :- fluent(X), not current_state(X).

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
#show not_exec/2. 
#show h(X, J) : h(X, J), fluent(X), stop(J).