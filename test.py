from tracker import *

def test_tracking():
  track = Tracker()
  track.get_tle('ISS')
  track.start_tracking()
  track.show_position()

test_tracking()