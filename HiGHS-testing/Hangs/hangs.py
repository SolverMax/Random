# Import dependencies

from pyomo.environ import *
import os.path
import json

# Get data

DataFilename = 'data-100.json'
with open(DataFilename, 'r') as f:
    Data = json.load(f)

# Declare model components and initialize simple data structures

Model = ConcreteModel(name = 'Wire cutting')

Stock  = Data['Stock']
Demand = Data['Demand']

Model.P  = Set(initialize = list(Demand.keys()))
Model.S  = Set(initialize = list(Stock.keys()))
Model.S2 = Set(initialize = Model.S - Model.S.first())  # Exclude first stock item

Model.UseOne   = Param(initialize = Data['UseOne'][0])
Model.Required = Param(Model.P, mutable = True)
Model.Lengths  = Param(Model.S, mutable = True)
Model.MustUse  = Param(Model.S, mutable = True)

Model.Cuts     = Var(Model.P, Model.S, domain = Binary, initialize = 0)
Model.UseStock = Var(Model.S, domain = Binary, initialize = 0)

# Populate remaining data structures

for p in Model.P:    
    Model.Required[p] = Demand[p]['Required']
    
for s in Model.S:
    Model.Lengths[s] = Stock[s]['Lengths']
    Model.MustUse[s] = Stock[s]['MustUse']

# Define constraints and objective function

def rule_offcut(Model, S):
    return (Model.UseStock[S] * Model.Lengths[S]) - sum(Model.Required[p] * Model.Cuts[p, S] for p in Model.P) >= 0
Model.cOffCut = Constraint(Model.S, rule = rule_offcut)

def rule_cuts(Model, P):
    return sum(Model.Cuts[P, s] for s in Model.S) == 1
Model.cCuts = Constraint(Model.P, rule = rule_cuts)

def rule_OnlyIfUsing(Model, P, S):
    return Model.Cuts[P, S] <= Model.UseStock[S]
Model.cIfUsing = Constraint(Model.P, Model.S, rule = rule_OnlyIfUsing)

def rule_MustUse(Model, S):
    return Model.UseStock[S] >= Model.MustUse[S]
Model.cMustUse = Constraint(Model.S, rule = rule_MustUse)

def rule_Obj(Model):
    if Model.UseOne == 0:
        StockInclude = Model.S2
    else:
        StockInclude = Model.S
    return sum((Model.UseStock[s] * Model.Lengths[s]) - sum(Model.Required[p] * Model.Cuts[p, s] for p in Model.P) for s in StockInclude)
Model.OffcutWaste= Objective(rule = rule_Obj, sense = minimize)

# Solve model

Solver = SolverFactory('appsi_highs')
Solver.options['time_limit']  = 300
Solver.options['mip_rel_gap'] = 0
Solver.options['log_file'] = 'highs.log'
Solver.options['threads'] = 1
Results = Solver.solve(Model, load_solutions = False, tee = True)

# Process results

WriteOut  = False
Optimal   = False
LimitStop = False
if Results.solver.termination_condition == TerminationCondition.optimal:
    Optimal = True
if Results.solver.termination_condition == TerminationCondition.maxTimeLimit or Results.solver.termination_condition == TerminationCondition.maxIterations:
    LimitStop = True
if Optimal or LimitStop:
    try:
        WriteOut = True
        Model.solutions.load_from(Results)
        SolverData = Results.Problem._list
        SolutionLB = SolverData[0].lower_bound
        SolutionUB = SolverData[0].upper_bound
    except:
        WriteOut = False
#WriteOut   = True

# Write solution

print('Status:',  Results.solver.termination_condition, '\n')
if LimitStop:
    print('Objective bounds')
    print('----------------')
    print(f'Lower: {SolutionLB:9,.2f}')
    print(f'Upper: {SolutionUB:9,.2f}\n')
if WriteOut:
    if Model.UseOne == 0:
        print('Excluding length 1')
    else:
        print('Including length 1')
    print(f'Total off-cut = {Model.OffcutWaste():7,.0f} mm')

    TotalLength = 0
    for p in Model.P:
        TotalLength += value(Model.Required[p])
    print(f'Total length  = {TotalLength:7,.0f} mm')
    WastePct = Model.OffcutWaste() / TotalLength * 100
    print(f'Waste         = {WastePct:7,.2f} %')
    
    Cut_matrix = '\n'
    Cut_matrix += 11 * ' ' + 'Stock\n'
    Cut_matrix += 'Piece' + 7 * ' '
    for s in range(1, len(Model.S) + 1):                 # Stock item numbers
        Cut_matrix += str(s).rjust(4) + 4 * ' '
    Cut_matrix += '\n'
    Cut_matrix += (8 * (len(Model.S) - 1) + 16) * '-'    # Header underline
    Cut_matrix += '\n'
    for p in range(1, len(Model.P) + 1):                 # Piece item numbers
        Cut_matrix += str(p).rjust(5) + 10 * ' '
        for s in range(1, len(Model.S) + 1):
            if round(value(Model.Cuts[str(p), str(s)]),0) == 1:   # S and P defined as string in json file, so need to use str()
                Output = 'x'
            else:
                Output = '-'
            Cut_matrix += Output + 7 * ' '
        Cut_matrix += '\n'
    Cut_matrix += (8 * (len(Model.S) - 1) + 16) * '-'    # Footer underline
    Cut_matrix += '\n'
    Cut_matrix += 'Use:' + 11 * ' '
    for s in Model.S:                                    # Item used
        if round(value(Model.UseStock[s]), 0) == 1:
            Cut_matrix += 'x' + 7 * ' '
        else:
            Cut_matrix += '-' + 7 * ' '
    Cut_matrix += '\nOff-cut '
    for s in Model.S:                                    # Length of off-cut
        UsedLength = 0
        for p in Model.P:
            UsedLength += value(Model.Cuts[str(p), str(s)]) * value(Model.Required[p])
        RemainingLength = value(Model.Lengths[s]) - UsedLength
        Cut_matrix += f'{RemainingLength:7,.0f}'.rjust(8)
    print(Cut_matrix)
else:
    print('No solution loaded')

Model.write()