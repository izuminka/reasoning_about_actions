#include <incmode>.
 
fluent(X) :- pfluent(X). 

literal(X) :- fluent(X). 
literal(-X) :- fluent(X).

literal(X) :- dfluent(X). 
literal(-X) :- dfluent(X). 

contrary(X, -X) :- fluent(X). 
contrary(-X, X) :- fluent(X). 

contrary(X, -X) :- dfluent(X). 
contrary(-X, X) :- dfluent(X). 


initially(X) :- init(X). 

h(X, 1)   :- initially(X), fluent(X). 
h(-X, 1)  :- fluent(X), not initially(X). 

h(X, 1) :- dfluent(X), define(X, Y), 
	formula(Y, and), 
	#count{Z : member(Z, Y), contrary(Z,Z'), h(Z', 1)} == 0.   
 
h(-X, 1)  :- fluent(X), not h(X, 1).   
h(-X, 1)  :- dfluent(X), not h(X, 1).   
 
max(I) :- I = #max {J : occurs(_, J)}. 
  
#program step(t).

time(t). 

% {occurs(A, t) : action(A)} 1.  


h(X, t) :- define(X, Y), 
	formula(Y, and), 
%	#count{Z : member(Z, Y), contrary(Z,Z'), h(Z', t)} == 0. 
	#count{Z : member(Z, Y), not h(Z, t)} == 0. 

h(X, t) :- define(X, Y), 
	formula(Y, or), 
	#count{Z : member(Z, Y), h(Z, t)} > 0. 
%	#count{Z : member(Z, Y), literal(Z), h(Z, t)} > 0. 

%h(X, t) :- define(X, Y), 
%	formula(Y, and), 
%	#count{Z : member(Z, Y), not h(Z, t)} == 0. 
%
%h(X, t) :- define(X, Y), 
%	formula(Y, or), 
%	#count{Z : member(Z, Y), h(Z, t)} > 0. 

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

stop(J+1) :- max(J). 

#program check(t).

:- query(t), not stop(t). 
 
%#show.
%#show stop/1.
%#show occurs/2.
%#show not_exec/2.
%#show h(X, J) : h(X, J), fluent(X), stop(J).
%#show time/1.
%#show max/1.
%%#show h/2.
%%#show define/2.