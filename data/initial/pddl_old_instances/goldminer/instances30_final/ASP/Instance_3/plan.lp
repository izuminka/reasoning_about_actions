occurs(action_move(f2-0f,f1-0f),1).
occurs(action_move(f1-0f,f0-0f),2).
occurs(action_pick_up_bomb(f0-0f),3).
occurs(action_detonate_bomb(f0-0f, f0-1f),4).
occurs(action_pick_up_bomb(f0-0f),5).
occurs(action_move(f0-0f,f0-1f),6).
occurs(action_detonate_bomb(f0-1f, f0-2f),7).
occurs(action_move(f0-1f,f0-2f),8).
occurs(action_pick_gold(f0-2f),9).
