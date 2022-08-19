# Analyzing and Notifying Routes Safety During Winter Season

## What Is The Project All About?

* Many field staff across many parts of the globe face difficulty in operations during winter times due to snow piles and/or snow storms which lead to dangerous situations such as slippery roads or even road closures. Field staff like technicians having multiple operations in multiple locations, last mile delivery drivers, etc. All roads are not elevated equal as flat surface, so slippery roads are even more dangerous. Often, the drivers are not aware of the roads’ elevations along their routes’ path. This can put them in a difficult situation getting in or out of inclined or declined roads. Therefore, the drivers get stuck let alone any potential personal, vehicle or properties damage in case of an accident. The aim of this project is to analyze the safety of roads along a specified route path by reporting land elevation and roads incline or decline angles along that path.

## How Elevations and Angles Are Calculated for a Route Plan?

* The elevation data points are obtained from the Open Elevation (https://open-elevation.com) by sending a request to its API with coordinates of the route plan (obtained from a GPX file). Here is the equation to calculate the roads angles value (+ve indicate incline, -ve indicate decline, zero angle is flat):

$$ \theta = {\LARGE \frac{180}{\pi} \ tan^{-1}(\frac{dr_e}{dx})}$$

* where ${\LARGE \frac{180}{\pi}}$ is conversion from randians to degrees, ${\LARGE \frac{dr_e}{dx}}$ is route's elevation derivative with respect to route's distance. Here is an example of route elevation and route angles with respect to the distance of the route:
