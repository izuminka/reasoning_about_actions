occurs(action_move(f0-0f,f1-0f),1).
occurs(action_pickup_laser(f1-0f),2).
occurs(action_move(f1-0f,f0-0f),3).
occurs(action_fire_laser(f0-0f, f0-1f),4).
occurs(action_move(f0-0f,f0-1f),5).
occurs(action_fire_laser(f0-1f, f0-2f),6).
occurs(action_move(f0-1f,f0-2f),7).
occurs(action_fire_laser(f0-2f, f0-3f),8).
occurs(action_move(f0-2f,f0-1f),9).
occurs(action_move(f0-1f,f0-0f),10).
occurs(action_move(f0-0f,f1-0f),11).
occurs(action_put_down_laser(f1-0f),12).
occurs(action_pick_up_bomb(f1-0f),13).
occurs(action_move(f1-0f,f0-0f),14).
occurs(action_move(f0-0f,f0-1f),15).
occurs(action_move(f0-1f,f0-2f),16).
occurs(action_move(f0-2f,f0-3f),17).
occurs(action_detonate_bomb(f0-3f, f0-4f),18).
occurs(action_move(f0-3f,f0-4f),19).
occurs(action_pick_gold(f0-4f),20).
