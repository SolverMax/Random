# highspy hangs during solve for some models

Issue: HiGHS hangs when solving some models using highspy. It occurs more often when the model is running as a JupyterLab notebook, but also occurs if the same model is run from the command line as a py file.

When the solver hangs, CPU usage drops to zero but the memory usage remains.

The notebook in this folder is an example of a model where this behavior occurs. The HiGHS solver stops after about 50 seconds of runtime.

OS: Windows 11.

HiGHS: 1.7.0 (though same behavior occurred in 1.5.3)

Python: Same behavior on several different versions of Python.
