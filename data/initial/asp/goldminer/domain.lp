% I have the following types:
loc(L) :- loc(L).

% I have the following predicates:
pfluent(robot_at(L)) :- loc(L).
pfluent(bomb_at(L)) :- loc(L).
pfluent(laser_at(L)) :- loc(L).
pfluent(soft_rock_at(L)) :- loc(L).
pfluent(hard_rock_at(L)) :- loc(L).
pfluent(gold_at(L)) :- loc(L).
pfluent(arm_empty).
pfluent(holds_bomb).
pfluent(holds_laser).
pfluent(holds_gold).
pfluent(clear(L)) :- loc(L).
pfluent(connected(L1, L2)) :- loc(L1), loc(L2), L1 != L2.

% I have the following actions and restrictions:
action(action_move(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
cond(cond_exec_move(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
exec(action_move(L1, L2), cond_exec_move(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
cond(cond_causes_move(L1, L2)) :- loc(L1), loc(L2), L1 != L2.

action(action_pick_up_laser(L)) :- loc(L).
cond(cond_exec_pick_up_laser(L)) :- loc(L).
exec(action_pick_up_laser(L), cond_exec_pick_up_laser(L)) :- loc(L).
cond(cond_causes_pick_up_laser(L)) :- loc(L).

action(action_pick_up_bomb(L)) :- loc(L).
cond(cond_exec_pick_up_bomb(L)) :- loc(L).
exec(action_pick_up_bomb(L), cond_exec_pick_up_bomb(L)) :- loc(L).
cond(cond_causes_pick_up_bomb(L)) :- loc(L).

action(action_put_down_laser(L)) :- loc(L).
cond(cond_exec_put_down_laser(L)) :- loc(L).
exec(action_put_down_laser(L), cond_exec_put_down_laser(L)) :- loc(L).
cond(cond_causes_put_down_laser(L)) :- loc(L).

action(action_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
cond(cond_exec_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
exec(action_detonate_bomb(L1, L2), cond_exec_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
cond(cond_causes_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.

action(action_fire_laser(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
cond(cond_exec_fire_laser(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
exec(action_fire_laser(L1, L2), cond_exec_fire_laser(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
cond(cond_causes_fire_laser(L1, L2)) :- loc(L1), loc(L2), L1 != L2.

action(action_pick_gold(L)) :- loc(L).
cond(cond_exec_pick_gold(L)) :- loc(L).
exec(action_pick_gold(L), cond_exec_pick_gold(L)) :- loc(L).
cond(cond_causes_pick_gold(L)) :- loc(L).

% Action Move preconditions and effects
member(robot_at(L1), cond_exec_move(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
member(connected(L1, L2), cond_exec_move(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
member(clear(L2), cond_exec_move(L1, L2)) :- loc(L1), loc(L2), L1 != L2.

causes(action_move(L1, L2), -robot_at(L1), cond_causes_move(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
causes(action_move(L1, L2), robot_at(L2), cond_causes_move(L1, L2)) :- loc(L1), loc(L2), L1 != L2.

% Action Pick up laser preconditions and effects
member(robot_at(L), cond_exec_pick_up_laser(L)) :- loc(L).
member(laser_at(L), cond_exec_pick_up_laser(L)) :- loc(L).
member(arm_empty, cond_exec_pick_up_laser(L)) :- loc(L).

causes(action_pick_up_laser(L), -arm_empty, cond_causes_pick_up_laser(L)) :- loc(L).
causes(action_pick_up_laser(L), holds_laser, cond_causes_pick_up_laser(L)) :- loc(L).
causes(action_pick_up_laser(L), -laser_at(L), cond_causes_pick_up_laser(L)) :- loc(L).

% Action Pick up bomb preconditions and effects
member(robot_at(L), cond_exec_pick_up_bomb(L)) :- loc(L).
member(bomb_at(L), cond_exec_pick_up_bomb(L)) :- loc(L).
member(arm_empty, cond_exec_pick_up_bomb(L)) :- loc(L).

causes(action_pick_up_bomb(L), -arm_empty, cond_causes_pick_up_bomb(L)) :- loc(L).
causes(action_pick_up_bomb(L), holds_bomb, cond_causes_pick_up_bomb(L)) :- loc(L).

% Action Put down laser preconditions and effects
member(robot_at(L), cond_exec_put_down_laser(L)) :- loc(L).
member(holds_laser, cond_exec_put_down_laser(L)) :- loc(L).

causes(action_put_down_laser(L), arm_empty, cond_causes_put_down_laser(L)) :- loc(L).
causes(action_put_down_laser(L), -holds_laser, cond_causes_put_down_laser(L)) :- loc(L).
causes(action_put_down_laser(L), laser_at(L), cond_causes_put_down_laser(L)) :- loc(L).

% Action Detonate bomb preconditions and effects
member(robot_at(L1), cond_exec_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
member(holds_bomb, cond_exec_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
member(connected(L1, L2), cond_exec_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
member(soft_rock_at(L2), cond_exec_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.

causes(action_detonate_bomb(L1, L2), -holds_bomb, cond_causes_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
causes(action_detonate_bomb(L1, L2), arm_empty, cond_causes_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
causes(action_detonate_bomb(L1, L2), clear(L2), cond_causes_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
causes(action_detonate_bomb(L1, L2), -soft_rock_at(L2), cond_causes_detonate_bomb(L1, L2)) :- loc(L1), loc(L2), L1 != L2.

% Action Fire laser preconditions and effects
member(robot_at(L1), cond_exec_fire_laser(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
member(holds_laser, cond_exec_fire_laser(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
member(connected(L1, L2), cond_exec_fire_laser(L1, L2)) :- loc(L1), loc(L2), L1 != L2.

causes(action_fire_laser(L1, L2), clear(L2), cond_causes_fire_laser(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
causes(action_fire_laser(L1, L2), -soft_rock_at(L2), cond_causes_fire_laser(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
causes(action_fire_laser(L1, L2), -gold_at(L2), cond_causes_fire_laser(L1, L2)) :- loc(L1), loc(L2), L1 != L2.
causes(action_fire_laser(L1, L2), -hard_rock_at(L2), cond_causes_fire_laser(L1, L2)) :- loc(L1), loc(L2), L1 != L2.

% Action Pick gold preconditions and effects
member(robot_at(L), cond_exec_pick_gold(L)) :- loc(L).
member(arm_empty, cond_exec_pick_gold(L)) :- loc(L).
member(gold_at(L), cond_exec_pick_gold(L)) :- loc(L).

causes(action_pick_gold(L), -arm_empty, cond_causes_pick_gold(L)) :- loc(L).
causes(action_pick_gold(L), holds_gold, cond_causes_pick_gold(L)) :- loc(L).