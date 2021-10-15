__author__ = """
execute the command line tool
"""
"Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from argh import dispatch_command

from ehyd_tools.cl_tool import run_script

"""
execute the command line tool
"""

dispatch_command(run_script)

