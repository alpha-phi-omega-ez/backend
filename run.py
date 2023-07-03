__author__ = "Rafael Cenzano and Jadyn Baidoo-Davis"
__copyright__ = "Copyright 2023, Alpha Phi Omega, Epsilon Zeta Chapter"
__credits__ = ["Rafael Cenzano", "Jadyn Baidoo-Davis", "Samuel DeMarrias"]
__license__ = "GNU GPL v3"
__version__ = "0.1.0"
__maintainer__ = "Rafael Cenzano"
__email__ = "contact@apoez.org"
__status__ = "Development"

from apo import app

if __name__ == "__main__":
    # app.run(ssl_context="adhoc", port="8000")
    app.run(port="8000")