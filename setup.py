import cx_Freeze

executables = [cx_Freeze.Executable("Tetresta.py")]

cx_Freeze.setup(
    name="Tetresta",
    options={"build_exe": {"packages":["pygame"]}},
    executables = executables

    )