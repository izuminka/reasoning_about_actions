occurs(action_move(f2-0f,f1-0f),1).
occurs(action_move(f1-0f,f0-0f),2).
occurs(action_pick_up_bomb(f0-0f),3).
occurs(action_move(f0-0f,f1-0f),4).
occurs(action_detonate_bomb(f1-0f, f1-1f),5).
occurs(action_move(f1-0f,f1-1f),6).
occurs(action_pick_gold(f1-1f),7).
