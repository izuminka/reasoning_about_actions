% Objects:
block(b1; b2; b3; b4; b5; b6; b7; b8; b9).

% Initial State:
init(handempty;
on(b1, b9);
on(b2, b6);
on(b3, b2);
on(b4, b7);
ontable(b5);
on(b6, b8);
ontable(b7);
on(b8, b4);
ontable(b9);
clear(b1);
clear(b3);
clear(b5)).

% Goal State:
goal(on(b2, b6);
on(b3, b8);
on(b4, b1);
on(b7, b2);
on(b6, b9);
on(b8, b7)).