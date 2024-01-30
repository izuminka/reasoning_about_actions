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
