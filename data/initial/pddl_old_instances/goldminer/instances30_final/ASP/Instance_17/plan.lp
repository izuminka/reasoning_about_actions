occurs(action_move(f1_0f,f2_0f),1).
occurs(action_pickup_laser(f2_0f),2).
occurs(action_fire_laser(f2_0f, f2_1f),3).
occurs(action_move(f2_0f,f2_1f),4).
occurs(action_fire_laser(f2_1f, f2_2f),5).
occurs(action_move(f2_1f,f2_2f),6).
occurs(action_fire_laser(f2_2f, f2_3f),7).
occurs(action_move(f2_2f,f2_1f),8).
occurs(action_move(f2_1f,f2_0f),9).
occurs(action_put_down_laser(f2_0f),10).
occurs(action_pick_up_bomb(f2_0f),11).
occurs(action_move(f2_0f,f2_1f),12).
occurs(action_move(f2_1f,f2_2f),13).
occurs(action_move(f2_2f,f2_3f),14).
occurs(action_detonate_bomb(f2_3f, f2_4f),15).
occurs(action_move(f2_3f,f2_4f),16).
occurs(action_pick_gold(f2_4f),17).
