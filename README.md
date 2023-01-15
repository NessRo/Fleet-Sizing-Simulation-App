# Fleet-Sizing-Simulation-App

This app is intended to be deployed on azure using azure Blob storage and azure web app services.

# Purpose

purpose of the app is to simulate rail transportation cycle times in order to determine the optimal rail car fleet size given a weekly demand parameter.

# how it works

the app is given several paramters sent over as a JSON payload.

these parameters are:
1. Weekly Demand structured as a dictionary where keys are days of the week and value is the expected demand (in rail cars)
2. cycle time statistics for the particular scenario. statistics include
    * Mean, Max, Min and Standard deviation for transit times going to destination.
    * Mean, Max, Min and Standard deviation for wait times at the destination. (wait times can include processing and unloading time)
    * Mean, Max, Min and Standard deviation for transit times back to origin.
    * Mean, Max, Min and Standard deviation for wait times at the Origin. (wait times can include processing and loading time)
    
the app intializes an initial rail fleet size based on the following formula:

$(\frac{(DTm+DWm+OTm+OWm)+((DTstdev+DWstdev+OTstdev+OWstdev)\times2)}{7}) \times \sum(WD)$

$DTm =$ mean of the destination transit times.

$DWm =$ mean of the destination wait times.

$OTm =$ mean of the origin transit times.

$OWm =$ mean of the origin wait times.

$DTstdev =$ Standard deviation of the destination transit times.

$DWstdev =$ Standard deviation of the destination wait times.

$OTstdev =$ Standard deviation of the origin transit times.

$OWstdev =$ Standard deviation of the origin wait times.

$WD =$ Weekly Demand.



Given the parameters above, the app simulates a random point in a trunctated normal distribution given the summary statistics of the cycle time.

the app creates 10 seperate simulations each with 365 days simulated. each simulation uses +-2% of the initial fleetsize set at the begining of the process.

the app further plots all 10 simulations on a graph showing:

    * Exected Yearly Demand = the demand that is expected if all deliveries are made according to the weekly demand expanded for 365 days a year.
    
    * actual demand = the demand that was simulated given the randomly selected distribution for 365 days a year.
    
    * service level = the actual demand divided by the expected yearly demand. service expressed as a peprcentage.
    
![alt text](https://github.com/NessRo/Fleet-Sizing-Simulation-App/blob/master/plot.png?raw=true)

the app saves the plot and a table describing the results to an excel file which gets stored in a blob storage.

# API Structure

there are two main end points for the app.

1. start_sim post end point:

    * end point takes a JSON payload that includes the weekly demand and the sumary statistics necessary for the simulation.
    
    * the end point starts the simulation as a background process and returns a reponse containing a unique ID for the process/simulation.
    
    * it is critical that the response be stored so the results can be retrieved.
    
2. get_file get end point:

    * end point takes the ID from the start_sim response to go and retrieve the file from the blob storge.
    
    * if file does not exist/simulation has not completed it will return a file not found error.
    
    * response is a file response: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet / an excel document.
