import sys
sys.path.append("../")
import jayhawk

# Install the SIGINT handler
jayhawk.install_signal_handler()

# Easiest example: host a directory on port 3000.
jayhawk.serve_directory("exampleroot",("localhost",3000))

# Browse to spartan://localhost:3000/ in your browser of choice and you'll see Jayhawk in action.
