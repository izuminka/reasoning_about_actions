% I have the following predicates:
pfluent(on_board(I, S)) :- instrument(I), satellite(S).
pfluent(supports(I, M)) :- instrument(I), mode(M).
pfluent(pointing(S, D)) :- satellite(S), direction(D).
pfluent(power_available(S)) :- satellite(S).
pfluent(power_on(I)) :- instrument(I).
pfluent(calibrated(I)) :- instrument(I).
pfluent(have_image(D, M)) :- direction(D), mode(M).
pfluent(calibration_target(I, D)) :- instrument(I), direction(D).

% I have the following actions and restrictions:
action(action_turn_to(S, New_D, Prev_D)) :- satellite(S), direction(New_D), direction(Prev_D), New_D != Prev_D.
cond(cond_exec_turn_to(S, New_D, Prev_D)) :- satellite(S), direction(New_D), direction(Prev_D), New_D != Prev_D.
exec(action_turn_to(S, New_D, Prev_D), cond_exec_turn_to(S, New_D, Prev_D)) :- satellite(S), direction(New_D), direction(Prev_D), New_D != Prev_D.
cond(cond_causes_turn_to(S, New_D, Prev_D)) :- satellite(S), direction(New_D), direction(Prev_D), New_D != Prev_D.

action(action_switch_on(I, S)) :- instrument(I), satellite(S).
cond(cond_exec_switch_on(I, S)) :- instrument(I), satellite(S).
exec(action_switch_on(I, S), cond_exec_switch_on(I, S)) :- instrument(I), satellite(S).
cond(cond_causes_switch_on(I, S)) :- instrument(I), satellite(S).

action(action_switch_off(I, S)) :- instrument(I), satellite(S).
cond(cond_exec_switch_off(I, S)) :- instrument(I), satellite(S).
exec(action_switch_off(I, S), cond_exec_switch_off(I, S)) :- instrument(I), satellite(S).
cond(cond_causes_switch_off(I, S)) :- instrument(I), satellite(S).

action(action_calibrate(S, I, D)) :- satellite(S), instrument(I), direction(D).
cond(cond_exec_calibrate(S, I, D)) :- satellite(S), instrument(I), direction(D).
exec(action_calibrate(S, I, D), cond_exec_calibrate(S, I, D)) :- satellite(S), instrument(I), direction(D).
cond(cond_causes_calibrate(S, I, D)) :- satellite(S), instrument(I), direction(D).

action(action_take_image(S, D, I, M)) :- satellite(S), direction(D), instrument(I), mode(M).
cond(cond_exec_take_image(S, D, I, M)) :- satellite(S), direction(D), instrument(I), mode(M).
exec(action_take_image(S, D, I, M), cond_exec_take_image(S, D, I, M)) :- satellite(S), direction(D), instrument(I), mode(M).
cond(cond_causes_take_image(S, D, I, M)) :- satellite(S), direction(D), instrument(I), mode(M).

% Action Turn to preconditions and effects
member(pointing(S, Prev_D), cond_exec_turn_to(S, New_D, Prev_D)) :- satellite(S), direction(New_D), direction(Prev_D), New_D != Prev_D.
causes(action_turn_to(S, New_D, Prev_D), pointing(S, New_D), cond_causes_turn_to(S, New_D, Prev_D)) :- satellite(S), direction(New_D), direction(Prev_D), New_D != Prev_D.
causes(action_turn_to(S, New_D, Prev_D), -pointing(S, Prev_D), cond_causes_turn_to(S, New_D, Prev_D)) :- satellite(S), direction(New_D), direction(Prev_D), New_D != Prev_D.

% Action Switch on preconditions and effects
member(on_board(I, S), cond_exec_switch_on(I, S)) :- instrument(I), satellite(S).
member(power_available(S), cond_exec_switch_on(I, S)) :- instrument(I), satellite(S).
causes(action_switch_on(I, S), power_on(I), cond_causes_switch_on(I, S)) :- instrument(I), satellite(S).
causes(action_switch_on(I, S), -calibrated(I), cond_causes_switch_on(I, S)) :- instrument(I), satellite(S).
causes(action_switch_on(I, S), -power_available(S), cond_causes_switch_on(I, S)) :- instrument(I), satellite(S).

% Action Switch off preconditions and effects
member(on_board(I, S), cond_exec_switch_off(I, S)) :- instrument(I), satellite(S).
member(power_on(I), cond_exec_switch_off(I, S)) :- instrument(I), satellite(S).
causes(action_switch_off(I, S), -power_on(I), cond_causes_switch_off(I, S)) :- instrument(I), satellite(S).
causes(action_switch_off(I, S), power_available(S), cond_causes_switch_off(I, S)) :- instrument(I), satellite(S).

% Action Calibrate preconditions and effects
member(on_board(I, S), cond_exec_calibrate(S, I, D)) :- satellite(S), instrument(I), direction(D).
member(calibration_target(I, D), cond_exec_calibrate(S, I, D)) :- satellite(S), instrument(I), direction(D).
member(pointing(S, D), cond_exec_calibrate(S, I, D)) :- satellite(S), instrument(I), direction(D).
member(power_on(I), cond_exec_calibrate(S, I, D)) :- satellite(S), instrument(I), direction(D).
causes(action_calibrate(S, I, D), calibrated(I), cond_causes_calibrate(S, I, D)) :- satellite(S), instrument(I), direction(D).

% Action Take image preconditions and effects
member(calibrated(I), cond_exec_take_image(S, D, I, M)) :- satellite(S), direction(D), instrument(I), mode(M).
member(on_board(I, S), cond_exec_take_image(S, D, I, M)) :- satellite(S), direction(D), instrument(I), mode(M).
member(supports(I, M), cond_exec_take_image(S, D, I, M)) :- satellite(S), direction(D), instrument(I), mode(M).
member(power_on(I), cond_exec_take_image(S, D, I, M)) :- satellite(S), direction(D), instrument(I), mode(M).
member(pointing(S, D), cond_exec_take_image(S, D, I, M)) :- satellite(S), direction(D), instrument(I), mode(M).
causes(action_take_image(S, D, I, M), have_image(D, M), cond_causes_take_image(S, D, I, M)) :- satellite(S), direction(D), instrument(I), mode(M).