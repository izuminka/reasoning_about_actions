% I have the following types:
object(O) :- room(O).
room(O) :- room(O).
object(O) :- object(O).
object(O) :- robot(O).
robot(O) :- robot(O).
object(O) :- gripper(O).
gripper(O) :- gripper(O).

% I have the following predicates:
pfluent(at_robby(R, Rm)) :- robot(R), room(Rm).
pfluent(at(O, Rm)) :- object(O), room(Rm).
pfluent(free(R, G)) :- robot(R), gripper(G).
pfluent(carry(R, O, G)) :- robot(R), object(O), gripper(G).

% I have the following actions and restrictions:
action(action_move(R, Rm_From, Rm_To)) :- robot(R), room(Rm_From), room(Rm_To), Rm_From != Rm_To.
cond(cond_exec_move(R, Rm_From, Rm_To)) :- robot(R), room(Rm_From), room(Rm_To), Rm_From != Rm_To.
exec(action_move(R, Rm_From, Rm_To), cond_exec_move(R, Rm_From, Rm_To)) :- robot(R), room(Rm_From), room(Rm_To), Rm_From != Rm_To.
cond(cond_causes_move(R, Rm_From, Rm_To)) :- robot(R), room(Rm_From), room(Rm_To), Rm_From != Rm_To.

action(action_pick(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
cond(cond_exec_pick(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
exec(action_pick(R, O, Rm, G), cond_exec_pick(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
cond(cond_causes_pick(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).

action(action_drop(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
cond(cond_exec_drop(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
exec(action_drop(R, O, Rm, G), cond_exec_drop(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
cond(cond_causes_drop(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).

% Action Move preconditions and effects
member(at_robby(R, Rm_From), cond_exec_move(R, Rm_From, Rm_To)) :- robot(R), room(Rm_From), room(Rm_To), Rm_From != Rm_To.
causes(action_move(R, Rm_From, Rm_To), -at_robby(R, Rm_From), cond_causes_move(R, Rm_From, Rm_To)) :- robot(R), room(Rm_From), room(Rm_To), Rm_From != Rm_To.
causes(action_move(R, Rm_From, Rm_To), at_robby(R, Rm_To), cond_causes_move(R, Rm_From, Rm_To)) :- robot(R), room(Rm_From), room(Rm_To), Rm_From != Rm_To.

% Action Pick preconditions and effects
member(at(O, Rm), cond_exec_pick(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
member(at_robby(R, Rm), cond_exec_pick(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
member(free(R, G), cond_exec_pick(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).

causes(action_pick(R, O, Rm, G), carry(R, O, G), cond_causes_pick(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
causes(action_pick(R, O, Rm, G), -at(O, Rm), cond_causes_pick(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
causes(action_pick(R, O, Rm, G), -free(R, G), cond_causes_pick(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).

% Action Drop preconditions and effects
member(carry(R, O, G), cond_exec_drop(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
member(at_robby(R, Rm), cond_exec_drop(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).

causes(action_drop(R, O, Rm, G), at(O, Rm), cond_causes_drop(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
causes(action_drop(R, O, Rm, G), free(R, G), cond_causes_drop(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).
causes(action_drop(R, O, Rm, G), -carry(R, O, G), cond_causes_drop(R, O, Rm, G)) :- robot(R), object(O), room(Rm), gripper(G).