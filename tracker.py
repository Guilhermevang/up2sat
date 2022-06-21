import ephem
from libs import *
import time
from datetime import datetime
import requests
import re
import threading as th 

class Tracker:
  def __init__(self):
    self.id = None # id of the satellite
    self.satellite = None # ephem satellite object
    self.observer = ephem.Observer() # the observer
    self._logs = [] # logs
    self._tracking = False # if satellite is being tracked
    self._lock = th.Lock()
    self.threads = {}
    self.default_settings = {
      'lat': -24.0443,
      'lon': -52.3775,
      'ele': 618,
      'tle_filename': 'tle.txt',
      'interval': 1,
    }
    

  def setLocation(self, lat=None, lon=None, ele=None):
    """
    Set the location of the observer
    """
    lat = lat or self.default_settings['lat']
    lon = lon or self.default_settings['lon']
    ele = ele or self.default_settings['ele']

    self.default_settings = {
      'lat': lat, 'lon': lon, 'ele': ele,
    }

    self.observer.lat = str(lat)
    self.observer.lon = str(lon)
    self.observer.elevation = int(ele)
    self.observer.date = ephem.now()
    self.observer.epoch = ephem.now()
    self.logFile('Observer location set')


  def logFile(self, text=None):
    """Add a new log"""
    self._logs.append('> {}'.format(text))


  def getLogs(self):
    """Get the logs"""
    return self._logs


  def search_tle(self, target=None, base_url=None, paths=('',)):
    """
    Search for the TLE of the satellite
    """
    if target is None or base_url is None:
      self.logFile('Error: target or base_url is not set')
      return
    
    pattern = r'[\s]*?.*?' + target + r'[\t )(]*?.*?[\n\r\f\v]+?(.+?)[\n\r\f\v]+?(.+?)[\n\r\f\v]'
    for path in paths:
      url = base_url + path
      try:
        data = requests.get(url).text
        match = re.search(pattern, data)
        if match:
          tle1 = match.group(1).strip()
          tle2 = match.group(2).strip()
          self.logFile('Found Satellite')
          return (str(tle1), str(tle2))
      except:
        self.logFile('Error: could not get data from {}'.format(url))
        continue


  def get_tle(self, sat_id=None, destination='tle.txt'):
    """
    Get the TLE from satellite name (sat_id) and insert it on destination
    """
    if sat_id is None:
      self.logFile('Error: satellite ID is not especified')
      return
    
    data = self.search_tle(sat_id, URLS['AMSAT'])
    if not data:
      data = self.search_tle(sat_id, URLS['CELESTRAK'], PATHS)
    if not data:
      self.logFile('Error: satellite not found')
      return

    file = open(f'files/{destination}', 'w')
    lines = [str(sat_id)+'\n'] + [str(data[0])+'\n'] + [str(data[1])]
    file.writelines(lines)
    file.close()

    self.satellite = ephem.readtle(str(sat_id), *data)
    self.tle = [str(sat_id), *data]
    self.id = str(sat_id)
    self.logFile('Satellite saved')


  def start_tracking(self, interval=None):
    """
    Starts a new thread that calculates the position of satellite in real time
    it's based on observer coordinates
    """
    interval = self.default_settings['interval'] if interval is None else interval
    self.default_settings['interval'] = interval

    self._tracking = True
    self.start_thread('update_position', self.update_position, [interval])
    self.logFile('Tracking')

  
  def stop_tracking(self):
    """
    Pause the tracking of satellite
    """
    self.stop_thread('update_position')
    self.logFile('Tracking stopped')


  def update_position(self, interval):
    """
    It will run in a thread to calculate the coordinates of satellite
    """
    while self._tracking:
      with self._lock:
        try:
          self.observer.date = ephem.now()
          self.satellite.compute(self.observer)
        except Exception as e:
          error = f'Error: {e}'
          print(error)
          self.logFile(error)
      time.sleep(interval)

  
  def start_thread(self, name=None, target=None, args=[]):
    """
    Create and start a new thread
    """
    if None in (name, target):
      self.logFile('Error: name or target not defined')
      return

    if name in self.threads:
      self.logFile('Thread is already running')
      return

    thr = th.Thread(target=target, args=args)
    thr.daemon = True
    self.threads[name] = thr
    thr.start()
    self.logFile('New thread created and started. Thread name: {}'.format(name))


  def stop_thread(self, name=None):
    """
    Stop and delete running threads
    """
    if name is None:
      return

    if name in self.threads:
      self.threads[name].join()
      del self.threads[name]
      self.logFile('Thread deleted. Thread name: {}'.format(name))
    else:
      self.logFile('No threads found')
  
  
  def current_position(self, convert=True):
    """
    Returns the atual position (coordinates) of the satellite
    param convert tell if the response must be converted to degrees or stay radians 
    """
    alt = self.satellite.alt
    az = self.satellite.az
    lat = self.satellite.sublat
    lon = self.satellite.sublong
    
    with self._lock:
      return {
        'alt': alt if not convert else rad2deg(alt),
        'az': az if not convert else rad2deg(az),
        'lat': lat if not convert else rad2deg(lat),
        'lon': lon if not convert else rad2deg(lon),
      }

  def show_position(self, convert=True):
    """
    Prints the position in specified interval
    """
    while self._tracking:
      position = self.current_position(convert)
      print(f'{self.id} > [LAT]: {position["lat"]}, [LON]: {position["lon"]}')
      time.sleep(self.default_settings['interval'])