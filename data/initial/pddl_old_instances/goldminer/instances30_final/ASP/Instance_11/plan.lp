occurs(action_move(f4-0f,f3-0f),1).
occurs(action_move(f3-0f,f2-0f),2).
occurs(action_move(f2-0f,f1-0f),3).
occurs(action_pick_up_bomb(f1-0f),4).
occurs(action_move(f1-0f,f0-0f),5).
occurs(action_detonate_bomb(f0-0f, f0-1f),6).
occurs(action_move(f0-0f,f1-0f),7).
occurs(action_pick_up_bomb(f1-0f),8).
occurs(action_move(f1-0f,f0-0f),9).
occurs(action_move(f0-0f,f0-1f),10).
occurs(action_detonate_bomb(f0-1f, f0-2f),11).
occurs(action_move(f0-1f,f0-2f),12).
occurs(action_pick_gold(f0-2f),13).
