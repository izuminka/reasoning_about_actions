occurs(action_move(f1_0f,f2_0f),1).
occurs(action_move(f2_0f,f3_0f),2).
occurs(action_pickup_laser(f3_0f),3).
occurs(action_move(f3_0f,f2_0f),4).
occurs(action_move(f2_0f,f1_0f),5).
occurs(action_fire_laser(f1_0f, f1_1f),6).
occurs(action_move(f1_0f,f1_1f),7).
occurs(action_fire_laser(f1_1f, f1_2f),8).
occurs(action_move(f1_1f,f1_0f),9).
occurs(action_move(f1_0f,f2_0f),10).
occurs(action_move(f2_0f,f3_0f),11).
occurs(action_putdown_laser(f3_0f),12).
occurs(action_pickup_bomb(f3_0f),13).
occurs(action_move(f3_0f,f2_0f),14).
occurs(action_move(f2_0f,f1_0f),15).
occurs(action_move(f1_0f,f1_1f),16).
occurs(action_move(f1_1f,f1_2f),17).
occurs(action_detonate_bomb(f1_2f, f1_3f),18).
occurs(action_move(f1_2f,f1_3f),19).
occurs(action_pick_gold(f1_3f),20).
