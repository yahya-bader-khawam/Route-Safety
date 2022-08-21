# Analyzing and Notifying Routes Safety During Winter Season

## What Is The Project All About?

* Many field staff across many parts of the globe face difficulty in operations during winter times due to snow piles and/or snow storms which lead to dangerous situations such as slippery roads or even road closures. Field staff like technicians having multiple operations in multiple locations, last mile delivery drivers, etc. All roads are not elevated equal as flat surface, so slippery roads are even more dangerous. Often, the drivers are not aware of the roads’ elevations along their routes’ path. This can put them in a difficult situation getting in or out of inclined or declined roads. Therefore, the drivers get stuck let alone any potential personal, vehicle or properties damage in case of an accident. The aim of this project is to analyze the safety of roads along a specified route path by reporting land elevation and roads incline or decline angles along that path.

## How Elevations and Angles Are Calculated for a Route Plan?

* The elevation data points are obtained from the Open Elevation (https://open-elevation.com) by sending a request to its API with coordinates of the route plan (obtained from a GPX file). Here is the equation to calculate the roads angles value (+ve indicate incline, -ve indicate decline, zero angle is flat):

$$ \theta_i = {\LARGE \frac{180}{\pi} \ tan^{-1}(\frac{de_i}{dx_i})}$$

* where ${\LARGE \frac{180}{\pi}}$ is conversion from randians to degrees, ${\LARGE \frac{de_i}{dx_i}}$ is route's elevation derivative with respect to route's distance. Here is an example of route elevation and route angles with respect to the distance of the route:

$$ $$

  ![alt text](https://github.com/yahya-bader-khawam/Route-Safety/blob/main/re.png?raw=true)

## How the Algorithm Works?
![alt text](https://github.com/yahya-bader-khawam/Route-Safety/blob/main/ra.png?raw=true)

* The algorithm work in this way:
  * Extract elevation data points for a given set of coordinates in a GPX file format, and outputs the angles in degrees for the elevation points to report how much inclined or decline a route path is. 
  * then analyzes each stop in a given route path for the following:
    * determine the nearest location of a stop to the route path.
    * Then, checks the roads safety (how much inclined or declined a road is at that stop) within some coverage distance ```stop_coverage``` to the right and left of a stop address. If any of the angle data points within the coverage distance range of a stop address is is greater than ```angle_threshold``` threshold, then going to or oute of that stop address is not considered safe. 

## RouteElevation Class Methods Description:

* ```RouteElevation.__init__(self, gpx_file)```: 
  * This method initializes a GPX file directory which contains info about 
        the route's lat and lon values.
        
* ```RouteElevation.gpx_latlon_values(self)```: 
  * This method converts a GPX file into a Pandas dataframe in order to 
        extract the lat and lon values from it. 
        
* ```RouteElevation.get_elevation(self)```: 
  * This method retrieves the elevation profile for coordinaters values 
        obtained from a GPX file. The request for elevation profile is sent 
        to Open Elevation API.
        
* ```RouteElevation.distance(self, lat1, lat2, lon1, lon2)```: 
  * This method calculates the haversine distance in kilometers between 
        coordinates (lat1,lon1) and (lat2,lon2).

* ```RouteElevation.distance_vector(self, lat_list1, lat_list2, lon_list1, lon_list2)```: 
  * This method calculates the haversine distances in kilometers between 
        a list of coordinates (lat_list1,lon_list1) and (lat_list2,lon_list2).

* ```RouteElevation.x_axis(self, lat_list, lon_list)```: 
  * This method creates the route's distance axis (x axis) from the 
        coordinates obtained from the GPX file. a cumulative sum between the 
        each consecutive coordinates is done to get the distance axis.

* ```RouteElevation.angle_profile(self, elev_list, lat_list, lon_list)```: 
  * This method calculates the route's path rate of rise/fall based on the
        route's elevation profile at coordinate in the GPX file with respect to 
        the distance axis. 
* ```RouteElevation.route_safety(self, distance_axis, angle_list, route_lat, route_lon, stops_lat, stops_lon, angle_threshold = 2, stop_coverage = 500)```: 
  * This method determines the safety of a stop location based on the angle 
        threshold value 'angle_threshold' in degrees within an address range 
        'stop_coverage' in meters from right and left. Therefore, total coverage
        is twice the 'stop_coverage'. If 'angle_list' values within the address
        range 'stop_coverage' is greater than 'angle_threshold', then the stop
        address is considered 'potentially dangerous address'. 

* ```RouteElevation.plot_profiles(self, distance_axis, ele_values, route_angle)```: 
  * This method create subplots for the elevation and angle profile for a
        route with relevant info such as mean, min and max. 

## Image Reference:
https://cdn.vectorstock.com/i/1000x1000/52/73/home-delivery-services-online-delivery-concept-vector-30605273.webp
