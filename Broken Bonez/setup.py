from cx_Freeze import setup, Executable 

buildOptions = dict(include_files = ['C:/Users/Connor/Documents/CF1/Python/Projects/Completed/Broken Bonez/Assets/']) #folder,relative path. Use tuple like in the single file to set a absolute path.

setup(
         name = "Broken Bonez",
         version = "1.0.2",
         description = "description",
         options = dict(build_exe = buildOptions),
         executables = [Executable("Broken Bonez.pyw")])
