occurs(action_move(f1_0f,f2_0f),1).
occurs(action_pickup_bomb(f2_0f),2).
occurs(action_detonate_bomb(f2_0f, f2_1f),3).
occurs(action_pickup_bomb(f2_0f),4).
occurs(action_move(f2_0f,f2_1f),5).
occurs(action_detonate_bomb(f2_1f, f2_2f),6).
occurs(action_move(f2_1f,f2_2f),7).
occurs(action_pick_gold(f2_2f),8).
