from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import FileResponse
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import tempfile
import os
import uuid

class Simulation(BaseModel):
    release_schedule: dict
    loaded_stats: dict
    customer_stats: dict
    empty_stats: dict
    plant_stats: dict

def Background_task_sim(process_id, sim_stats):
    import Rail_Simulation
    import File_Generator


    results = Rail_Simulation.Simulation(release_schedule=sim_stats.release_schedule,
                                        loaded_stats=sim_stats.loaded_stats,
                                        customer_stats=sim_stats.customer_stats,
                                        empty_stats=sim_stats.empty_stats,
                                        plant_stats=sim_stats.plant_stats)

    file = process_id + '.xlsx'

    fp = os.path.join(tempfile.gettempdir(), file)

    File_Generator.Make_file(results=results,fp=fp,process_id=process_id)
    
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "hello, workers are online and ready to work"}

@app.get("/get_file")
async def get_file(id: str):
    headers= {
    'Content-Disposition': 'attachment; filename="filename.xlsx"'
     }
    
    connect_str = 'DefaultEndpointsProtocol=https;AccountName=railsimapi;AccountKey=jSI/FlDL5zXG9dRKgPasV2LfPQf9YC4wfP04qWpTtKfrHXvXlYq6S5zioNo4UyMlhPOJ8bPldJnx+AStffklJQ==;EndpointSuffix=core.windows.net'

    process_id = id
    fp = process_id + ".xlsx"
    
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_container_client(container='sim-results')

    fp_temp = os.path.join(tempfile.gettempdir(), 'temp.xlsx')

    with open(fp_temp, "wb") as download_file:
        download_file.write(blob_client.download_blob(fp).readall())
    
    try:
        return FileResponse(fp_temp, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
    except Exception as ex:
        return (ex)

@app.get("/test_file")
async def get_test_file(background_tasks: BackgroundTasks):

    try:
        import uuid
        process_id = str(uuid.uuid4())
        import tempfile
        import File_Generator

        file = process_id + ".txt"

        fp = os.path.join(tempfile.gettempdir(), file)
        background_tasks.add_task(File_Generator.make_test_file,fp, dest_file = file)
        
        return {"process_ID":f'{process_id}'}
    except Exception as ex:
        return (f'{ex}')

@app.post("/start_sim")
async def get_csv(background_tasks: BackgroundTasks, sim: Simulation):
    
    try:
        
        process_id = str(uuid.uuid4())
        
        
        background_tasks.add_task(Background_task_sim,sim_stats = sim,process_id=process_id)


        return {"id":f'{process_id}'}


    except Exception as ex:
        return (f'{ex}')

@app.get("/start_manual_sim")
async def start_manual_sim(background_tasks: BackgroundTasks):
    
    try:
        
        import manual_sim
        process_id = str(uuid.uuid4())
        
        background_tasks.add_task(manual_sim.manual_sim_trigger)


        return {"id":f'{process_id}'}


    except Exception as ex:
        return (f'{ex}')