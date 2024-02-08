occurs(action_move(f4-0f,f3-0f),1).
occurs(action_pickup_laser(f3-0f),2).
occurs(action_move(f3-0f,f4-0f),3).
occurs(action_fire_laser(f4-0f, f4-1f),4).
occurs(action_move(f4-0f,f4-1f),5).
occurs(action_fire_laser(f4-1f, f4-2f),6).
occurs(action_move(f4-1f,f4-2f),7).
occurs(action_fire_laser(f4-2f, f4-3f),8).
occurs(action_move(f4-2f,f4-1f),9).
occurs(action_move(f4-1f,f4-0f),10).
occurs(action_move(f4-0f,f3-0f),11).
occurs(action_put_down_laser(f3-0f),12).
occurs(action_pick_up_bomb(f3-0f),13).
occurs(action_move(f3-0f,f4-0f),14).
occurs(action_move(f4-0f,f4-1f),15).
occurs(action_move(f4-1f,f4-2f),16).
occurs(action_move(f4-2f,f4-3f),17).
occurs(action_detonate_bomb(f4-3f, f4-4f),18).
occurs(action_move(f4-3f,f4-4f),19).
occurs(action_pick_gold(f4-4f),20).
