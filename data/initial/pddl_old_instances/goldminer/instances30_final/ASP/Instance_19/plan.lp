occurs(action_move(f0_0f,f1_0f),1).
occurs(action_pickup_laser(f1_0f),2).
occurs(action_fire_laser(f1_0f, f1_1f),3).
occurs(action_move(f1_0f,f1_1f),4).
occurs(action_fire_laser(f1_1f, f1_2f),5).
occurs(action_move(f1_1f,f1_2f),6).
occurs(action_fire_laser(f1_2f, f1_3f),7).
occurs(action_move(f1_2f,f1_1f),8).
occurs(action_move(f1_1f,f1_0f),9).
occurs(action_put_down_laser(f1_0f),10).
occurs(action_pick_up_bomb(f1_0f),11).
occurs(action_move(f1_0f,f1_1f),12).
occurs(action_move(f1_1f,f1_2f),13).
occurs(action_move(f1_2f,f1_3f),14).
occurs(action_detonate_bomb(f1_3f, f1_4f),15).
occurs(action_move(f1_3f,f1_4f),16).
occurs(action_pick_gold(f1_4f),17).
