### MODULE IMPORTING ###
class Print_Suppressed:
    """ Suppress print messages during module importing """
    def __enter__(self): self.restore, sys.stdout = sys.stdout, None
    def __exit__(self, *args): sys.stdout = self.restore

def import_pyfile(filepath):
    if not filepath.is_file(): raise FileNotFoundError(f'{filepath} does not exist.')
    sys.path.insert(0, filepath.parent)
    with Print_Suppressed():
        try:
            module = importlib.import_module(filepath.name)
        except:
            raise RuntimeError(f'{filepath.name} cannot be imported properly.')
    # To import specific module functionality, use the getattr function
    # and check for AttributeError
    return module


### CLASS INSPECTION ###
import inspect
def findattr(obj, methods=True):
    # Prints all non-builtin methods/attributes of an object
    res = []
    for k in dir(obj):
        if k[0] == "_": continue # ignore built-in methods
        if (methods and inspect.isroutine(getattr(obj, k)))\
                or not (methods or inspect.isroutine(getattr(obj, k))): # attributes
            res.append(k)
    return res



########################################
##  HACK TO RUN SCRIPT IN CWD : START ##
########################################
# Required to run module from within package directory itself, by obtaining
# reference to `orm` package using cd, then pipelining output using temp stdout
# Remember to delete this section before deployment
if __name__ == "__main__":
    pkg_name = "orm"
    import subprocess, pathlib, sys, os
    cwd = pathlib.Path.cwd()
    if cwd.stem == pkg_name: # currently still in package directory
        module_name = pathlib.Path(__file__).resolve().stem
        temp_stdout = "{}.out".format(module_name)
        with open(temp_stdout, "w") as outfile:
            cmd = "python -m {}.{}".format(pkg_name, module_name)
            subprocess.call(cmd.split(), cwd=cwd.parent, stdout=outfile)
        with open(temp_stdout, "r") as infile: print(infile.read())
        os.remove(temp_stdout)
    quit() # gracefully terminate thread
#######################################
##  HACK TO RUN SCRIPT IN CWD : END  ##
#######################################
