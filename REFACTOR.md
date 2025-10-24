DIRECTORY STRUCTURE:

README.md

CLAUDE.md

controllers/
  INA219.py
  battery.py  # wrapper around INA219, 1 func 'status' returns dict
  pca.py  # initializes and exports
  servo.py  # takes channel, name, uses default min_pulse max_pulse, includes a dict of servo-specific data like directional modifiers and calibration and limits.

subscribers/
  server.py
  webapp/
  xbox.py  # LATER, add a dummy for now

diamond.py (entry point)
  1. initialize 12 servos and battery
  2. sets up a command queue, main loop that processes command queue once/sec (1hz)
  3. define two funcs: status() returns current angles and battery stats, command adds to the queue
  4. start the two subscribers in separate threads and pass them status() and command()

diamond.service (runs diamond.py)

requirements.txt

.gitignore

(get rid of the docs, was a bad idea)