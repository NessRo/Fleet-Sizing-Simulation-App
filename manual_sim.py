import Rail_Simulation
import File_Generator



def manual_sim_trigger():
    release_schedule = {'Monday': 1,'Tuesday': 0 ,'Wednesday': 1 ,'Thursday': 0 ,'Friday': 0 ,'Saturday': 1 ,'Sunday': 0}
    loaded_stats =  {'mean':16,'std':4,'min':12,'max':30}
    customer_stats= {'mean':10,'std':1,'min':9,'max':11}
    empty_stats= {'mean':20, 'std':7, 'min':13,'max':41}
    plant_stats= {'mean':10,'std':1,'min':9,'max':11}

    fp = r'C:\Users\nassim.rostane\OneDrive - JM Huber Corp\Desktop\Reporting\Logistics\fleet size simulations\Prime - Woodland\sim_results.xlsx'

    print(sum(release_schedule.values()))

    sim_results = Rail_Simulation.Simulation(release_schedule=release_schedule,loaded_stats=loaded_stats,customer_stats=customer_stats,empty_stats=empty_stats, plant_stats=plant_stats)

    File_Generator.Make_file_manual(results=sim_results,fp=fp)

if __name__ == "__main__":
    manual_sim_trigger()