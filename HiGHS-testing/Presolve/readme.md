# Test model for HiGHS presolve time limit.

Issue: It appears that HiGHS does not check the time_limit option during presolve. https://github.com/ERGO-Code/HiGHS/issues/1501

This model spends a lot of time in presolve. With the test data, solve time to optimality is about 100 seconds, of which 96 seconds is in presolve.

The time limit option is specified on line 192.

Cases:
- Presolve on (line 44), time limit of 30 seconds, HiGHS stops with infeasible solution when presolve is complete at 96 seconds.
- Presolve off, time limit of 30 seconds, HiGHS stops with infeasible solution at 30 seconds.
- Presolve on or off, time limit of 300 seconds, HiGHS stops with optimal solution after about 100 seconds.

Note that there is some data preparation time before HiGHS is called. This is not counted towards the time limit.
