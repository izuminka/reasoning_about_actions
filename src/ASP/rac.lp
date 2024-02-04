time(1..max). 

fluent(X) :- pfluent(X). 

literal(X) :- fluent(X). 
literal(-X) :- fluent(X). 
contrary(X, -X) :- fluent(X). 
contrary(-X, X) :- fluent(X). 

initially(X) :- init(X). 

h(X, 1)   :- initially(X), literal(X). 
h(-X, 1)  :- fluent(X), not init(X). 
  
 {occurs(A, T) : action(A)} 1 :-  time(T), T < max.  

:- time(T), action(A), occurs(A, T), not executable(A, T). 

h(X, T) :- time(T), define(X, Y), 
	formula(Y, and), 
	#count{Z : member(Z, Y), literal(Z), not h(Z, T)} == 0. 

h(X, T) :- time(T), define(X, Y), 
	formula(Y, or), 
	#count{Z : member(Z, Y), literal(Z), h(Z, T)} > 0. 

executable(A, T) :-  time(T), action(A), 
	     exec(A, S), 
	     #count{Z : literal(Z), member(Z, S), not h(Z, T)} == 0. 

h(X, T+1) :- action(A), occurs(A, T),
	     causes(A, X, true), 
	     time(T). 

h(X, T+1) :- action(A), occurs(A, T),
	     causes(A, X, Y),
	     literal(Y), h(Y, T),  
	     time(T). 

h(X, T+1) :- action(A), occurs(A, T),
	     causes(A, X, S),
	     #count{Z : literal(Z), member(Z, S), not h(Z, T)} == 0,  
	     time(T). 

h(X, T+1) :- time(T), T < max, h(X, T), contrary(X, Y), not h(Y, T+1). 
 
inconsistent :- time(T), contrary(X, Y), h(X, T), h(Y, T).  

all_goal(T) :- time(T), #count {X : goal(X), h(-X, T)} == 0.   	

:- not all_goal(max). 

 
#show. 
#show occurs/2.   
#show h(X, max) : fluent(X), h(X, max).
#show inconsistent/0.
%#show time/1.
#show goal/1. 
#show init/1. 
#show all_goal/1. 
