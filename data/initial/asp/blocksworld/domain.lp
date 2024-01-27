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