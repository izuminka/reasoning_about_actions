occurs(action_move(f2-0f,f1-0f),1).
occurs(action_move(f1-0f,f0-0f),2).
occurs(action_pickup_laser(f0-0f),3).
occurs(action_move(f0-0f,f1-0f),4).
occurs(action_move(f1-0f,f2-0f),5).
occurs(action_fire_laser(f2-0f, f2-1f),6).
occurs(action_move(f2-0f,f2-1f),7).
occurs(action_fire_laser(f2-1f, f2-2f),8).
occurs(action_move(f2-1f,f2-0f),9).
occurs(action_move(f2-0f,f1-0f),10).
occurs(action_move(f1-0f,f0-0f),11).
occurs(action_put_down_laser(f0-0f),12).
occurs(action_pick_up_bomb(f0-0f),13).
occurs(action_move(f0-0f,f1-0f),14).
occurs(action_move(f1-0f,f2-0f),15).
occurs(action_move(f2-0f,f2-1f),16).
occurs(action_move(f2-1f,f2-2f),17).
occurs(action_detonate_bomb(f2-2f, f2-3f),18).
occurs(action_move(f2-2f,f2-3f),19).
occurs(action_pick_gold(f2-3f),20).
