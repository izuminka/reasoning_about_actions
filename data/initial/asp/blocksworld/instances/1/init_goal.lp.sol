{
  "Solver": "clingo version 5.6.2",
  "Input": [
    "/Users/paveldolin/dev/research/nsf_asp/planning/data/asp/v12/blocksworld-typed/instances30_final/template/instance-1/template/asp.lp"
  ],
  "Call": [
    {
      "Witnesses": [
        {
          "Value": [
            "occurs(action_unstack(b2,b1),16)", "occurs(action_unstack(b1,b2),6)", "occurs(action_unstack(b3,b2),0)", "occurs(action_unstack(b2,b3),8)", "occurs(action_unstack(b8,b4),18)", "occurs(action_unstack(b2,b6),2)", "occurs(action_unstack(b2,b6),12)", "occurs(action_unstack(b4,b7),20)", "occurs(action_unstack(b6,b8),14)", "occurs(action_unstack(b1,b9),4)", "occurs(action_stack(b2,b1),13)", "occurs(action_stack(b4,b1),21)", "occurs(action_stack(b1,b2),5)", "occurs(action_stack(b5,b2),29)", "occurs(action_stack(b2,b3),3)", "occurs(action_stack(b7,b4),23)", "occurs(action_stack(b2,b6),11)", "occurs(action_stack(b2,b6),17)", "occurs(action_stack(b8,b7),25)", "occurs(action_stack(b3,b8),27)", "occurs(action_stack(b6,b9),15)", "occurs(action_put_down(b1),7)", "occurs(action_put_down(b2),9)", "occurs(action_put_down(b3),1)", "occurs(action_put_down(b8),19)", "occurs(action_pick_up(b2),10)", "occurs(action_pick_up(b3),26)", "occurs(action_pick_up(b5),28)", "occurs(action_pick_up(b7),22)", "occurs(action_pick_up(b8),24)"
          ],
          "Costs": [
            30
          ]
        }
      ]
    }
  ],
  "Result": "SATISFIABLE",
  "INTERRUPTED": 1,
  "Models": {
    "Number": 1,
    "More": "yes",
    "Optimum": "unknown",
    "Optimal": 0,
    "Costs": [
      30
    ]
  },
  "Calls": 1,
  "Time": {
    "Total": 23.322,
    "Solve": 22.951,
    "Model": 20.346,
    "Unsat": 0.000,
    "CPU": 22.174
  }
}
