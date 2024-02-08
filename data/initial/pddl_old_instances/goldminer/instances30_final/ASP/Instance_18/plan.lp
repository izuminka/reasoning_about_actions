occurs(action_move(f0-0f,f1-0f),1).
occurs(action_move(f1-0f,f2-0f),2).
occurs(action_move(f2-0f,f3-0f),3).
occurs(action_move(f3-0f,f4-0f),4).
occurs(action_pickup_laser(f4-0f),5).
occurs(action_move(f4-0f,f3-0f),6).
occurs(action_move(f3-0f,f2-0f),7).
occurs(action_move(f2-0f,f1-0f),8).
occurs(action_fire_laser(f1-0f, f1-1f),9).
occurs(action_move(f1-0f,f1-1f),10).
occurs(action_fire_laser(f1-1f, f1-2f),11).
occurs(action_move(f1-1f,f1-0f),12).
occurs(action_move(f1-0f,f2-0f),13).
occurs(action_move(f2-0f,f3-0f),14).
occurs(action_move(f3-0f,f4-0f),15).
occurs(action_put_down_laser(f4-0f),16).
occurs(action_pick_up_bomb(f4-0f),17).
occurs(action_move(f4-0f,f3-0f),18).
occurs(action_move(f3-0f,f2-0f),19).
occurs(action_move(f2-0f,f1-0f),20).
occurs(action_move(f1-0f,f1-1f),21).
occurs(action_move(f1-1f,f1-2f),22).
occurs(action_detonate_bomb(f1-2f, f1-3f),23).
occurs(action_move(f1-2f,f1-3f),24).
occurs(action_pick_gold(f1-3f),25).
