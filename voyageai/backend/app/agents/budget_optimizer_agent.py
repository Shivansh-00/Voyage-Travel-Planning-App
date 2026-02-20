from ortools.linear_solver import pywraplp
from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState


class BudgetOptimizerAgent(BaseAgent):
    name = 'BudgetOptimizerAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        budget = state['request'].budget
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if solver is None:
            state['optimization_summary'] = 'Optimizer unavailable; using default itinerary.'
            return state

        vars_ = []
        for idx, exp in enumerate(state['experiences']):
            vars_.append((exp, solver.IntVar(0, 1, f'x_{idx}')))

        total_exp_cost = solver.Sum(var * exp['cost'] for exp, var in vars_)
        flight_cost = state['itinerary'][0].estimated_cost
        hotel_cost = next(item.estimated_cost for item in state['itinerary'] if item.category == 'hotel')
        fixed_cost = flight_cost + hotel_cost + 25
        solver.Add(total_exp_cost + fixed_cost <= budget)
        solver.Maximize(solver.Sum(var * exp['score'] for exp, var in vars_))

        solver.Solve()
        selected = {exp['name'] for exp, var in vars_ if var.solution_value() > 0.5}
        state['itinerary'] = [
            item for item in state['itinerary']
            if item.category != 'experience' or item.activity in selected
        ]
        state['total_cost'] = sum(item.estimated_cost for item in state['itinerary'])
        state['optimization_summary'] = (
            f'Selected {len(selected)} experiences, optimized under budget {budget:.2f} '
            f'with projected spend {state["total_cost"]:.2f}.'
        )
        self.log(state, state['optimization_summary'])
        return state
