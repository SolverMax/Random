# Test model for HiGHS presolve time limit.

Issue: It appears that HiGHS does not check the time_limit option during presolve. https://github.com/ERGO-Code/HiGHS/issues/1501

Cases:
- When running this model with presolve on (default), HiGHS stops well after the time limit.
- When running with presolve off (option on line 44), HiGHS stops on the time limit.

Time limit option is specified on line 192.

Note that there is some data preparation time before HiGHS is called. This is not counted towards the time limit.
