from datetime import datetime, timedelta
import pandas as pd
import scipy.stats
import numpy as np



date_data = {'Date': [],'Day': [], 'Cars_released': [], 'Available for shipping date (week Numbr)': []}
date = []
day = []
Cars_released = []
return_week = []

for i in range(365):
    date.append((datetime(2023 , 1 , 1)) + timedelta(days=i))
    day.append(((datetime(2023 , 1 , 1)) + timedelta(days=i)).strftime("%A"))
    Cars_released.append(int(0))
    return_week.append(None)

date_data['Date'] += date
date_data['Day'] += day
date_data['Cars_released'] += Cars_released
date_data['Available for shipping date (week Numbr)'] += return_week

xls = pd.DataFrame(data=date_data)


def Simulation(release_schedule,loaded_stats,customer_stats,empty_stats,plant_stats):

    Simulation_results = {'Fleet Size': [], "Expected Yearly Demand":[],"Actuals":[], "Service Level":[]}

    loaded_transit_mean = loaded_stats['mean']
    loaded_transit_std = loaded_stats['std']
    loaded_transit_min = loaded_stats['min']
    loaded_transit_max = loaded_stats['max']

    Customer_Layover_mean = customer_stats['mean']
    Customer_Layover_std = customer_stats['std']
    Customer_Layover_min = customer_stats['min']
    Customer_Layover_max = customer_stats['max']

    empty_transit_mean = empty_stats['mean']
    empty_transit_std = empty_stats['std']
    empty_transit_min = empty_stats['min']
    empty_transit_max = empty_stats['max']

    plant_layover_mean = plant_stats['mean']
    plant_layover_std = plant_stats['std']
    plant_layover_min = plant_stats['min']
    plant_layover_max = plant_stats['max']

    baseline_stock = round(((loaded_transit_mean+
                            Customer_Layover_mean+
                            empty_transit_mean+
                            plant_layover_mean+
                            loaded_transit_std*2+
                            Customer_Layover_std*2+
                            empty_transit_std*2+
                            plant_layover_std*2)/7)*sum(release_schedule.values()))

    stock_distribution = []
   
    for idx, i in enumerate(np.arange(-.05,.06,.01)):
        stock_iteration = round(baseline_stock * (1+(i*2)))

        try:
            if stock_iteration == stock_distribution[idx-1]:
                stock_iteration += 1
            elif stock_iteration < stock_distribution[idx-1]:
                stock_iteration = stock_distribution[idx-1] + 1
        except:
            stock_iteration
    
        stock_distribution.append(stock_iteration)


    for s in range(len(stock_distribution)):

        stock = stock_distribution[s]

        for i in range((len(xls))):
            if stock < release_schedule[xls['Day'].iloc[i]]:
                xls.at[i , 'Cars_released'] = stock
            elif i > 0 and xls['Cars_released'].iloc[i-1] < release_schedule[xls['Day'].iloc[i-1]]:
                remainder = release_schedule[xls['Day'].iloc[i-1]] - xls['Cars_released'].iloc[i-1]
                if (remainder + release_schedule[xls['Day'].iloc[i]]) > stock:
                    xls.at[i, 'Cars_released'] = release_schedule[xls['Day'].iloc[i]] + (stock - release_schedule[xls['Day'].iloc[i]])
                else:
                    xls.at[i , 'Cars_released'] = release_schedule[xls['Day'].iloc[i]] + remainder
            else:
                xls.at[i , 'Cars_released'] = release_schedule[xls['Day'].iloc[i]]

            if xls['Cars_released'].iloc[i] > 0:
                xls.at[i , 'Loaded Transit days'] = scipy.stats.truncnorm.rvs(((loaded_transit_min + (
                        loaded_transit_min  )) - loaded_transit_mean) / loaded_transit_std ,
                        (((loaded_transit_max) + (loaded_transit_max  )) - loaded_transit_mean) / loaded_transit_std ,
                        loc=loaded_transit_mean ,scale=loaded_transit_std)

                xls.at[i , 'AMP layover days'] = scipy.stats.truncnorm.rvs(
                    ((Customer_Layover_min + (Customer_Layover_min  )) - Customer_Layover_mean) / Customer_Layover_std ,
                    (((Customer_Layover_max) + (Customer_Layover_max  )) - Customer_Layover_mean) / Customer_Layover_std ,
                    loc=Customer_Layover_mean , scale=Customer_Layover_std)

                xls.at[i , 'empty transit days'] = scipy.stats.truncnorm.rvs(
                    ((empty_transit_min + (empty_transit_min  )) - empty_transit_mean) / empty_transit_std ,
                    (((empty_transit_max) + (empty_transit_max  )) - empty_transit_mean) / empty_transit_std ,
                    loc=empty_transit_mean , scale=empty_transit_std)

                xls.at[i , 'plant Layover Days'] = scipy.stats.truncnorm.rvs(((plant_layover_min + (
                        plant_layover_min  )) - plant_layover_mean) / plant_layover_std , (((
                        plant_layover_max) + (plant_layover_max  )) - plant_layover_mean) / plant_layover_std ,
                        loc=plant_layover_mean ,scale=plant_layover_std)

                xls.at[i , 'Total Cycle Time'] = xls['Loaded Transit days'].iloc[i] + xls['AMP layover days'].iloc[i] + \
                                                xls['empty transit days'].iloc[i] + xls['plant Layover Days'].iloc[i]

                xls.at[i , 'Available for shipping date'] = xls['Date'].iloc[i] + pd.to_timedelta(
                    xls['Total Cycle Time'].iloc[i] , unit='D')

                xls.at[i , 'Available for shipping date (week Numbr)'] = xls['Available for shipping date'].dt.isocalendar().week.iloc[i]

            for k in range(i):
                if xls['Date'].dt.isocalendar().week[i] == xls['Available for shipping date (week Numbr)'].iloc[k]:
                    stock += xls['Cars_released'].iloc[k]
                    xls.at[k , 'Available for shipping date (week Numbr)'] = None
            stock = stock - xls['Cars_released'].iloc[i]
            xls.at[i , 'Stock'] = stock
        
        Simulation_results['Fleet Size'].append(stock_distribution[s])
        Simulation_results['Expected Yearly Demand'].append(sum(release_schedule.values()) * 52)
        Simulation_results['Actuals'].append (xls['Cars_released'].sum())
        Simulation_results['Service Level'].append((xls['Cars_released'].sum())/(sum(release_schedule.values()) * 52))

    

    return Simulation_results

