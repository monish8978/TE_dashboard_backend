from settings import api_ip,api_port
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import traceback
from compute_layer_functions import all_agent_list,get_skill_list_by_campaign,get_list_name_by_campaign,main_test
from compute_layer_function_cmp import main_test as main_cmp
from agent_compute_layer import main_test as main_agent
from datetime import datetime
import numpy as np

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware to allow requests from specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace '*' with a list of allowed origins if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Define the request model
class User(BaseModel):
    selected_campaign_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    selected_filter_name: Optional[str] = None
    selected_campaign_type: Optional[str] = None
    selected_agent_filter: Optional[str] = None
    selected_skills_name: Optional[str] = None
    selected_list_name: Optional[str] = None

@app.post("/get-data")
async def create_user(user: User):
    # Convert start_date and end_date from string to datetime.date
    start_date_obj = datetime.strptime(user.start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(user.end_date, "%Y-%m-%d").date()

    dict_data = main_test(user.selected_campaign_name, start_date_obj, end_date_obj, user.selected_filter_name, user.selected_campaign_type,user.selected_agent_filter,user.selected_skills_name,user.selected_list_name)

    # Convert numpy.int64 to int (if present in dict_data)
    def convert_numpy_to_native(data):
        if isinstance(data, dict):
            return {key: convert_numpy_to_native(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [convert_numpy_to_native(item) for item in data]
        elif isinstance(data, np.int64):
            return int(data)  # Convert numpy.int64 to native Python int
        return data

    dict_data = convert_numpy_to_native(dict_data)

    return {"message": "Data found.", "data": dict_data, "status_code": 200}


@app.post("/get-data-cmp")
async def create_user_cmp(user: User):
    # Convert start_date and end_date from string to datetime.date
    start_date_obj = datetime.strptime(user.start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(user.end_date, "%Y-%m-%d").date()

    # selected_campaign_name,start_date,end_date,selected_campaign_type

    dict_data = main_cmp(user.selected_campaign_name, start_date_obj, end_date_obj, user.selected_campaign_type)

    return {"message": "Data found.", "data": dict_data, "status_code": 200}


@app.post("/get-data-agent")
async def create_user_agent(user: User):
    # Convert start_date and end_date from string to datetime.date
    start_date_obj = datetime.strptime(user.start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(user.end_date, "%Y-%m-%d").date()

    # selected_campaign_name,start_date,end_date

    dict_data = main_agent(user.selected_campaign_name, start_date_obj, end_date_obj)

    return {"message": "Data found.", "data": dict_data, "status_code": 200}


@app.post("/agent-list")
async def agent_list(user: User):
    """
    API endpoint to fetch agent_id list based on campaign and agent filter.

    Endpoint:
        POST /agent-list

    Request Body:
        user (User):
            Pydantic model containing:
            - selected_campaign_name
            - selected_agent_filter

    Returns:
        dict:
            JSON response containing message, data (agent_id list),
            and status_code.
    """

    # Call the agent_list function to get agent_id list
    # using campaign name and agent filter from request body
    agent_id_list = all_agent_list(
        user.selected_campaign_name
    )

    # Return API response in JSON format
    return {
        "message": "Data found.",
        "data": agent_id_list,   # list of agent IDs
        "status_code": 200
    }

@app.post("/skill-list")
async def skill_list(user: User):
    """
    API endpoint to fetch skill list based on campaign.

    Endpoint:
        POST /skill-list
    """

    skill_list = get_skill_list_by_campaign(
        user.selected_campaign_name
    )

    return {
        "message": "Data found.",
        "data": skill_list,
        "status_code": 200
    }

@app.post("/list-name")
async def skill_list(user: User):
    """
    API endpoint to fetch list name based on campaign.

    Endpoint:
        POST /list-name
    """

    list_name = get_list_name_by_campaign(
        user.selected_campaign_name
    )

    return {
        "message": "Data found.",
        "data": list_name,
        "status_code": 200
    }


# Entry point for running the application
if __name__ == "__main__":
    try:
        uvicorn.run(app, host=api_ip, port=api_port)  # Start the FastAPI app
    except Exception as e:
        traceback.print_exc()
