occurs(action_move(f1-0f,f0-0f),1).
occurs(action_pickup_laser(f0-0f),2).
occurs(action_fire_laser(f0-0f, f0-1f),3).
occurs(action_move(f0-0f,f0-1f),4).
occurs(action_fire_laser(f0-1f, f0-2f),5).
occurs(action_move(f0-1f,f0-2f),6).
occurs(action_fire_laser(f0-2f, f0-3f),7).
occurs(action_move(f0-2f,f0-1f),8).
occurs(action_move(f0-1f,f0-0f),9).
occurs(action_put_down_laser(f0-0f),10).
occurs(action_pick_up_bomb(f0-0f),11).
occurs(action_move(f0-0f,f0-1f),12).
occurs(action_move(f0-1f,f0-2f),13).
occurs(action_move(f0-2f,f0-3f),14).
occurs(action_detonate_bomb(f0-3f, f0-4f),15).
occurs(action_move(f0-3f,f0-4f),16).
occurs(action_pick_gold(f0-4f),17).
