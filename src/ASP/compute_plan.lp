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
  
#program step(t).

time(t). 

 {occurs(A, t) : action(A)} 1.  

:- action(A), occurs(A, t), not executable(A, t). 

h(X, t) :- define(X, Y), 
	formula(Y, and), 
	#count{Z : member(Z, Y), literal(Z), not h(Z, t)} == 0. 

h(X, t) :- define(X, Y), 
	formula(Y, or), 
	#count{Z : member(Z, Y), literal(Z), h(Z, t)} > 0. 

executable(A, t) :-  action(A), 
	     exec(A, S), 
	     #count{Z : literal(Z), member(Z, S), not h(Z, t)} == 0. 

h(X, t) :- action(A), occurs(A, t-1),
	     causes(A, X, true). 

h(X, t) :- action(A), occurs(A, t-1),
	     causes(A, X, Y),
	     literal(Y), h(Y, t). 

h(X, t) :- action(A), occurs(A, t-1),
	     causes(A, X, S),
	     #count{Z : literal(Z), member(Z, S), not h(Z, t)} == 0. 

h(X, t) :- time(t), h(X, t-1), contrary(X, Y), not h(Y, t).  

#program check(t).

:- query(t), goal(X), not h(X, t). 

#show. 
#show occurs/2.
#show h(X, t) : h(X, t), fluent(X).
#show time/1.

#show action/1.