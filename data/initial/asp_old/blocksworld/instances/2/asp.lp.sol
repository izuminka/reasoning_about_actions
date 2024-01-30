{
  "Solver": "clingo version 5.6.2",
  "Input": [
    "/Users/paveldolin/dev/research/nsf_asp/planning/data/asp/v12/blocksworld-typed/instances30_final/template/instance-2/template/asp.lp"
  ],
  "Call": [
    {
      "Witnesses": [
        {
          "Value": [
            "occurs(action_unstack(b7,b1),18)", "occurs(action_unstack(b4,b3),0)", "occurs(action_unstack(b3,b4),8)", "occurs(action_unstack(b4,b5),12)", "occurs(action_unstack(b2,b6),6)", "occurs(action_unstack(b3,b6),14)", "occurs(action_unstack(b5,b7),16)", "occurs(action_stack(b6,b1),25)", "occurs(action_stack(b1,b2),23)", "occurs(action_stack(b5,b3),17)", "occurs(action_stack(b3,b4),5)", "occurs(action_stack(b2,b5),21)", "occurs(action_stack(b4,b5),3)", "occurs(action_stack(b3,b6),9)", "occurs(action_stack(b7,b6),27)", "occurs(action_stack(b4,b7),29)", "occurs(action_put_down(b2),7)", "occurs(action_put_down(b2),11)", "occurs(action_put_down(b3),15)", "occurs(action_put_down(b4),1)", "occurs(action_put_down(b4),13)", "occurs(action_put_down(b7),19)", "occurs(action_pick_up(b1),22)", "occurs(action_pick_up(b2),10)", "occurs(action_pick_up(b2),20)", "occurs(action_pick_up(b3),4)", "occurs(action_pick_up(b4),2)", "occurs(action_pick_up(b4),28)", "occurs(action_pick_up(b6),24)", "occurs(action_pick_up(b7),26)"
          ],
          "Costs": [
            30
          ]
        },
        {
          "Value": [
            "occurs(action_unstack(b7,b1),4)", "occurs(action_unstack(b7,b1),8)", "occurs(action_unstack(b7,b1),20)", "occurs(action_unstack(b4,b3),0)", "occurs(action_unstack(b7,b4),12)", "occurs(action_unstack(b2,b6),6)", "occurs(action_unstack(b5,b7),2)", "occurs(action_stack(b6,b1),23)", "occurs(action_stack(b7,b1),5)", "occurs(action_stack(b7,b1),13)", "occurs(action_stack(b1,b2),11)", "occurs(action_stack(b5,b3),3)", "occurs(action_stack(b7,b4),9)", "occurs(action_stack(b2,b5),7)", "occurs(action_stack(b7,b6),25)", "occurs(action_stack(b4,b7),27)", "occurs(action_put_down(b4),1)", "occurs(action_put_down(b4),15)", "occurs(action_put_down(b6),17)", "occurs(action_put_down(b6),19)", "occurs(action_put_down(b7),21)", "occurs(action_pick_up(b1),10)", "occurs(action_pick_up(b4),14)", "occurs(action_pick_up(b4),26)", "occurs(action_pick_up(b6),16)", "occurs(action_pick_up(b6),18)", "occurs(action_pick_up(b6),22)", "occurs(action_pick_up(b7),24)"
          ],
          "Costs": [
            28
          ]
        }
      ]
    }
  ],
  "Result": "SATISFIABLE",
  "TIME LIMIT": 1,
  "Models": {
    "Number": 2,
    "More": "yes",
    "Optimum": "unknown",
    "Optimal": 0,
    "Costs": [
      28
    ]
  },
  "Calls": 1,
  "Time": {
    "Total": 180.013,
    "Solve": 179.874,
    "Model": 1.044,
    "Unsat": 0.000,
    "CPU": 179.828
  }
}
