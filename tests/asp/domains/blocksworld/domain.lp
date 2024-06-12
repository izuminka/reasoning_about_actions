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