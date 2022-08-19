# -*- coding: utf-8 -*-
from numpy.lib.function_base import angle
import pandas as pd
import numpy as np
from gpxcsv import gpxtolist
import re
import matplotlib.pyplot as plt
import haversine as hs
import urllib.request
import json
from haversine import haversine_vector, Unit

class RouteElevation():

  def __init__(self, gpx_file):
    ''' This method initializes a GPX file directory which contains info about 
        the route's lat and lon values
    '''
    self.gpx_file = gpx_file

  def gpx_latlon_values(self):
    ''' This method converts a GPX file into a Pandas dataframe in order to 
        extract the lat and lon values from it. 
    
    - Arguments: no input arugments.
    
    - Returns:
      * 'lat': is a list of latitude values obtained from the GPX file
      * 'lon': is a list of longtitude values obtained from the GPX file
    
    - Notes: the 'lat' and 'lon' lists correspond to each other in terms of 
             indices. For example, lat[0] and lon[0] make up the first location 
             in the GPX file.
    '''
    gpx_list = gpxtolist(self.gpx_file) # converts gpx_file to list
    df = pd.DataFrame(gpx_list) 
    lat = list(df['lat']) # extract lat values from the dataframe
    lon = list(df['lon']) # extract lon values form the dataframe
    return lat, lon

  def get_elevation(self):
    ''' This method retrieves the elevation profile for coordinaters values 
        obtained from a GPX file. The request for elevation profile is sent 
        to Open Elevation API.
    
    - Arguments: no input arguments

    - Returns: 
      * 'elev_list': the elvation profile in meters for each coordinate 
        in the GPX file. 
      * 'lat_list': is a list of latitude values obtained from the GPX file.
      * 'lon_list': is a list of longtitude values obtained from the GPX file.

    - Notes: this method returns 'lat_list' and 'lon_list' to aviod seperately 
            calling the 'gpx_latlon_values()' method.
    '''
    lat_list, lon_list = self.gpx_latlon_values() # retreives lat and lon values from gpx file

    # create a json file containing the coordinate values
    latlon_list = []
    for k in range(len(lat_list)):
        latlon_list.append({"latitude":lat_list[k],"longitude":lon_list[k]})
    location={"locations":latlon_list}
    latlon_json=json.dumps(location,skipkeys=int).encode('utf8')

    # send request to Open Elevation API to get elevation profile 
    url="https://api.open-elevation.com/api/v1/lookup"
    response = urllib.request.Request(url,latlon_json,headers={'Content-Type': 'application/json'})
    get_response = urllib.request.urlopen(response)

    # process the response obtained from the Open Elevation API
    result_str=get_response.read().decode("utf8")
    json_str=json.loads(result_str)
    get_response.close()

    # extract the elevation profile from the response and append them to a list 
    response_len=len(json_str['results'])
    elev_list=[]
    for n in range(response_len):
        elev_list.append(json_str['results'][n]['elevation'])
    
    return elev_list, lat_list, lon_list


  def distance(self, lat1, lat2, lon1, lon2):
    ''' This method calculates the haversine distance in kilometers between 
        coordinates (lat1,lon1) and (lat2,lon2).
    
    - Arguments:
      * 'lat1': latitude value for first coordinate.
      * 'lat2': latitude value for second coordinate.
      * 'lon1': longtitude value for first coordinate.
      * 'lon2': longtitude value for second coordinate.

    - Returns:
      * 'distance': the haversine distance in kilometers between two coordinates.
    '''
    # haversine distance in kilometers
    distance = hs.haversine((lat1,lon1),(lat2,lon2)) 
    return distance
  
  def distance_vector(self, lat_list1, lat_list2, lon_list1, lon_list2):
    ''' This method calculates the haversine distances in kilometers between 
        a list of coordinates (lat_list1,lon_list1) and (lat_list2,lon_list2).
    
    - Arguments:
      * 'lat_list1': a list of latitude values for first coordinates.
      * 'lat_list2': a list of latitude values for second coordinates.
      * 'lon_list1': a list of longtitude values for first coordinates.
      * 'lon_list2': a list of longtitude values for second coordinates.

    - Returns:
      * 'distances': a list of haversine distances in kilometers between two 
        sets of coordinates.
    '''
    # haversine distances in meters
    distances = haversine_vector(list(zip(lat_list1,lon_list1)), list(zip(lat_list2,lon_list2)), Unit.METERS) 
    return distances
    
    
  def x_axis(self, lat_list, lon_list):
    ''' This method creates the route's distance axis (x axis) from the 
        coordinates obtained from the GPX file. a cumulative sum between the 
        each consecutive coordinates is done to get the distance axis.
    
    - Arguments: 
      * 'lat_list': a list of latitude values.
      * 'lon_lost': a list of longtitude values.

    - Returns: 
      * 'distance_axis': the distance axis (x axis) in meters agianst which 
      elevation profile is measured to.    
    '''
    # distance_diff is the haversine distance in kilometers between consecutive 
    # coordinates
    distance_diff = [] 
    for k in range(1,len(lat_list)):
      distance_diff.append(self.distance(lat_list[k], lat_list[k-1], lon_list[k], lon_list[k-1]))
    # cumulative distance in meters
    distance_axis = 1000*np.array([0]+list(np.cumsum(distance_diff)))
    return distance_axis

  def angle_profile(self, elev_list, lat_list, lon_list):
    ''' This method calculates the route's path rate of rise/fall based on the
        route's elevation profile at coordinate in the GPX file with respect to 
        the distance axis. 

    - Arguments: 
      * 'elev_list': the elvation profile in meters for each coordinate 
        in the GPX file. 
      * 'lat_list': is a list of latitude values obtained from the GPX file.
      * 'lon_list': is a list of longtitude values obtained from the GPX file.

    - Returns: The angle in degrees for each rise/fall in the route's path.
    '''
    # creates the x axis
    distance_axis = self.x_axis(lat_list, lon_list) 
    # elevation points derivative with respoect to x
    dydx = np.gradient(elev_list,np.array(distance_axis)) 
    # elevation angles in degrees.
    route_angle = np.degrees(np.arctan(dydx))
    return route_angle

  def route_safety(self, distance_axis, angle_list, route_lat, route_lon, stops_lat, stops_lon, angle_threshold = 2, stop_coverage = 500):
    ''' This method determines the safety of a stop location based on the angle 
        threshold value 'angle_threshold' in degrees within an address range 
        'stop_coverage' in meters from right and left. Therefore, total coverage
        is twice the 'stop_coverage'. If 'angle_list' values within the address
        range 'stop_coverage' is greater than 'angle_threshold', then the stop
        address is considered 'potentially dangerous address'. 

    - Arugments:
      * 'distance_axis': the distance axis (x axis) in meters agianst which 
      elevation profile is measured to.
      * 'angle_list': The angle in degrees for each rise/fall in the route's path.
      * 'route_lan': is a list of latitude values obtained from the GPX file.
      * 'route_lon': is a list of longtitude values obtained from the GPX file.
      * 'stop_lat': is a list of latitude values obtained for each route's stop.
      * 'stop_lon': is a list of longtitude values obtained for each route's stop.
      * 'angle_threshold': is an angle value below which a stop address is 
                           considered 'potentially safe address' within the
                           'stop_coverage' range. has default value 2 degress.
      * 'stop_coverage': is a range value in meters within which safety check is 
                         done for stop in the route. it has default value of 
                         500 meters. 

    - Returns:
      * 'safety': is a list of string values either 'potentially safe address'
                  or 'potentially dangerous address' based on the safety of each 
                  stop address in the route based on the 'angle_threshold' and 
                  'stop_coverage' values.
      * 'indxs': returns the coverage indices for each stop in the route (left,
                  center and right indices). read project's readme for more info. 

    '''
    safety=[] # a list of 'potentially safe address' or 'potentially dangerous address'
    indxs = []
    for k in range(len(stops_lat)):
      # get stop location nearest to the route's path
      dists = list(self.distance_vector(route_lat, [stops_lat[k]]*len(route_lat), route_lon, [stops_lon[k]]*len(route_lat)))
      dists_min = min(dists)
      # index location of the stop address in the x axis (distance axis)
      min_dist_indx =  dists.index(dists_min)

      # center index at which the stop is neatest to route lat and lon.  
      center_indx = min_dist_indx
      center_distance = distance_axis[center_indx]
     
      # covering left theta points which leads to entering the stop address
      for indx in range(center_indx+1):
        left_indx = indx
        x_left = center_distance - distance_axis[indx]
        if x_left <= stop_coverage:
          break 

      # covering right theta points which leads to existing the stop address
      for indx in range(center_indx,len(distance_axis)):
        right_indx = indx
        x_right = distance_axis[indx] - center_distance
        if x_right > stop_coverage:
          right_indx -= 1
          break

      # combined left and right points
      stop_theta = angle_list[left_indx:right_indx+1]

      # check the max angle in near by the stop address for safety check
      if np.max(np.abs(stop_theta)) <= angle_threshold:
        safety.append('potentially safe address')
      else:
        safety.append('potentially dangerous address')
      # append all indices to indxs list of lists
      indxs.append([left_indx,center_indx, right_indx])
    return safety, indxs
    
  def plot_profiles(self, distance_axis, ele_values, route_angle):
    ''' This method create subplots for the elevation and angle profile for a
        route with relevant info such as mean, min and max. 
    '''
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13,13))
    fig.subplots_adjust(hspace=0.2)
    
    # plotting elevation profile
    elev_mean = np.round((sum(ele_values)/len(ele_values)),2)
    elev_min=np.round(np.min(ele_values),2)
    elev_max=np.round(np.max(ele_values),2) 
    base_reg=0
    ax1.plot(distance_axis,ele_values)
    ax1.plot(distance_axis,elev_min*np.ones(len(distance_axis)),'--g',label='min: '+str(elev_min)+' m')
    ax1.plot(distance_axis,elev_max*np.ones(len(distance_axis)),'--r',label='max: '+str(elev_max)+' m')
    ax1.plot(distance_axis,elev_mean*np.ones(len(distance_axis)),'--y',label='mean: '+str(elev_mean)+' m')
    ax1.fill_between(distance_axis,ele_values,base_reg,alpha=0.1)
    ax1.set_xlabel("Distance (m)")
    ax1.set_ylabel("Elevation (m)")
    ax1.grid()
    ax1.legend(fontsize=13)


    # plotting angle profile
    route_angle_min = np.round(np.min(route_angle),2)
    route_angle_max = np.round(np.max(route_angle),2)
    route_angle_mean = np.round(np.mean(route_angle),2)
    base_reg=0
    ax2.plot(distance_axis,route_angle)
    ax2.plot(distance_axis,route_angle_min*np.ones(len(distance_axis)),'--g',label='min: '+str(route_angle_min)+' deg')
    ax2.plot(distance_axis,route_angle_max*np.ones(len(distance_axis)),'--r',label='max: '+str(route_angle_max)+' deg')
    ax2.plot(distance_axis,route_angle_mean*np.ones(len(distance_axis)),'--y',label='mean: '+str(route_angle_mean)+' deg')
    ax2.fill_between(distance_axis,route_angle,base_reg,alpha=0.1)
    ax2.set_xlabel("Distance (m)")
    ax2.set_ylabel("angle (deg)")
    ax2.grid()
    ax2.legend(fontsize=13)
    
    plt.show()

