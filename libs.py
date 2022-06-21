PATHS = (
  'stations.txt', 'weather.txt', 'noaa.txt', 'goes.txt', 'resource.txt', 'sarsat.txt.', 'dmc.txt', 'tdrss.txt', 'argos.txt',
  'geo.txt', 'intelsat.txt', 'gorizont.txt', 'raduga.txt', 'molniya.txt', 'iridium.txt', 'orbcomm.txt', 'globalstar.txt',
  'amateur.txt', 'x-comm.txt', 'other-comm.txt', 'gps-ops.txt', 'glo-ops.txt', 'galileo.txt', 'beidou.txt',
  'sbas.txt', 'nnss.txt', 'musson.txt', 'science.txt', 'geodetic.txt', 'engineering.txt', 'education.txt', 'military.txt',
  'radat.txt', 'cubesat.txt', 'other.txt', 'tle-new.txt'
)

URLS = {
  'N2YO': 'http://www.n2yo.com/satellite/?s=',
  'CELESTRAK': 'http://www.celestrak.com/NORAD/elements/',
  'AMSAT': 'http://www.amsat.org/amsat/ftp/keps/current/nasa.all'
}

import ephem

def rad2deg(rad):
  return rad * 180 / ephem.pi