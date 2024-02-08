occurs(action_move(f1_0f,f0_0f),1).
occurs(action_pickup_laser(f0_0f),2).
occurs(action_fire_laser(f0_0f, f0_1f),3).
occurs(action_move(f0_0f,f0_1f),4).
occurs(action_fire_laser(f0_1f, f0_2f),5).
occurs(action_move(f0_1f,f0_2f),6).
occurs(action_fire_laser(f0_2f, f0_3f),7).
occurs(action_move(f0_2f,f0_1f),8).
occurs(action_move(f0_1f,f0_0f),9).
occurs(action_putdown_laser(f0_0f),10).
occurs(action_pickup_bomb(f0_0f),11).
occurs(action_move(f0_0f,f0_1f),12).
occurs(action_move(f0_1f,f0_2f),13).
occurs(action_move(f0_2f,f0_3f),14).
occurs(action_detonate_bomb(f0_3f, f0_4f),15).
occurs(action_move(f0_3f,f0_4f),16).
occurs(action_pick_gold(f0_4f),17).
