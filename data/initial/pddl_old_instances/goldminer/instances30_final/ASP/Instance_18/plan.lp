occurs(action_move(f0_0f,f1_0f),1).
occurs(action_move(f1_0f,f2_0f),2).
occurs(action_move(f2_0f,f3_0f),3).
occurs(action_move(f3_0f,f4_0f),4).
occurs(action_pickup_laser(f4_0f),5).
occurs(action_move(f4_0f,f3_0f),6).
occurs(action_move(f3_0f,f2_0f),7).
occurs(action_move(f2_0f,f1_0f),8).
occurs(action_fire_laser(f1_0f, f1_1f),9).
occurs(action_move(f1_0f,f1_1f),10).
occurs(action_fire_laser(f1_1f, f1_2f),11).
occurs(action_move(f1_1f,f1_0f),12).
occurs(action_move(f1_0f,f2_0f),13).
occurs(action_move(f2_0f,f3_0f),14).
occurs(action_move(f3_0f,f4_0f),15).
occurs(action_putdown_laser(f4_0f),16).
occurs(action_pickup_bomb(f4_0f),17).
occurs(action_move(f4_0f,f3_0f),18).
occurs(action_move(f3_0f,f2_0f),19).
occurs(action_move(f2_0f,f1_0f),20).
occurs(action_move(f1_0f,f1_1f),21).
occurs(action_move(f1_1f,f1_2f),22).
occurs(action_detonate_bomb(f1_2f, f1_3f),23).
occurs(action_move(f1_2f,f1_3f),24).
occurs(action_pick_gold(f1_3f),25).
