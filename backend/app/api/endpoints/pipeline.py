"""
Pipeline API Endpoints
Provides endpoints to trigger and monitor the data generation, forecasting, and resource allocation pipeline
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

router = APIRouter()

# Pipeline status tracking
pipeline_status = {
    "data_generator": {"status": "idle", "last_run": None, "result": None},
    "forecaster": {"status": "idle", "last_run": None, "result": None},
    "resource_allocator": {"status": "idle", "last_run": None, "result": None},
    "full_pipeline": {"status": "idle", "last_run": None, "result": None}
}


class DataGeneratorRequest(BaseModel):
    start_date: str = "2022-01-01"
    end_date: str = "2024-11-22"


class ForecasterRequest(BaseModel):
    target_column: str = "total_patients"
    horizon_days: int = 7


class ResourceAllocatorRequest(BaseModel):
    condition_type: Optional[str] = None
    target_department: str = "Emergency"


class FullPipelineRequest(BaseModel):
    start_date: str = "2022-01-01"
    end_date: str = "2024-11-22"
    target_column: str = "total_patients"
    horizon_days: int = 7
    skip_data: bool = False
    skip_forecast: bool = False
    skip_allocation: bool = False


def run_data_generator_task(start_date: str, end_date: str):
    """Background task to run data generator"""
    try:
        pipeline_status["data_generator"]["status"] = "running"
        pipeline_status["data_generator"]["last_run"] = datetime.now().isoformat()
        
        from Agent.data_generator_agent import DataGeneratorAgent
        
        agent = DataGeneratorAgent()
        result = agent.generate_data(start_date=start_date, end_date=end_date)
        
        pipeline_status["data_generator"]["status"] = "completed" if result["status"] == "success" else "failed"
        pipeline_status["data_generator"]["result"] = result
        
    except Exception as e:
        pipeline_status["data_generator"]["status"] = "failed"
        pipeline_status["data_generator"]["result"] = {"status": "failed", "error": str(e)}


def run_forecaster_task(target_column: str, horizon_days: int):
    """Background task to run forecaster"""
    try:
        pipeline_status["forecaster"]["status"] = "running"
        pipeline_status["forecaster"]["last_run"] = datetime.now().isoformat()
        
        from Agent.forecaster_agent import ForecasterAgent
        
        agent = ForecasterAgent()
        result = agent.run_forecasts(target_column=target_column, horizon_days=horizon_days)
        
        pipeline_status["forecaster"]["status"] = "completed" if result["status"] == "success" else "failed"
        pipeline_status["forecaster"]["result"] = result
        
    except Exception as e:
        pipeline_status["forecaster"]["status"] = "failed"
        pipeline_status["forecaster"]["result"] = {"status": "failed", "error": str(e)}


def run_resource_allocator_task(condition_type: Optional[str], target_department: str):
    """Background task to run resource allocator"""
    try:
        pipeline_status["resource_allocator"]["status"] = "running"
        pipeline_status["resource_allocator"]["last_run"] = datetime.now().isoformat()
        
        from Agent.resource_allocator_agent import ResourceAllocatorAgent
        
        agent = ResourceAllocatorAgent()
        result = agent.allocate_resources(
            condition_type=condition_type,
            target_department=target_department
        )
        
        pipeline_status["resource_allocator"]["status"] = "completed" if result["status"] == "success" else "failed"
        pipeline_status["resource_allocator"]["result"] = result
        
    except Exception as e:
        pipeline_status["resource_allocator"]["status"] = "failed"
        pipeline_status["resource_allocator"]["result"] = {"status": "failed", "error": str(e)}


def run_full_pipeline_task(request: FullPipelineRequest):
    """Background task to run full pipeline"""
    try:
        pipeline_status["full_pipeline"]["status"] = "running"
        pipeline_status["full_pipeline"]["last_run"] = datetime.now().isoformat()
        
        from Agent.agent_orchestrator import AgentOrchestrator
        
        orchestrator = AgentOrchestrator()
        results = orchestrator.run_complete_pipeline(
            generate_data=not request.skip_data,
            run_forecasts=not request.skip_forecast,
            allocate_resources=not request.skip_allocation,
            start_date=request.start_date,
            end_date=request.end_date,
            target_column=request.target_column,
            horizon_days=request.horizon_days
        )
        
        pipeline_status["full_pipeline"]["status"] = "completed"
        pipeline_status["full_pipeline"]["result"] = results
        
    except Exception as e:
        pipeline_status["full_pipeline"]["status"] = "failed"
        pipeline_status["full_pipeline"]["result"] = {"status": "failed", "error": str(e)}


@router.post("/data-generator/run")
async def run_data_generator(request: DataGeneratorRequest, background_tasks: BackgroundTasks):
    """
    Trigger data generation process
    Generates synthetic hospital data and saves to media/data/hospital_data
    """
    if pipeline_status["data_generator"]["status"] == "running":
        raise HTTPException(status_code=409, detail="Data generator is already running")
    
    background_tasks.add_task(run_data_generator_task, request.start_date, request.end_date)
    
    return {
        "message": "Data generator started",
        "start_date": request.start_date,
        "end_date": request.end_date,
        "status": "running"
    }


@router.get("/data-generator/status")
async def get_data_generator_status():
    """Get current status of data generator"""
    return pipeline_status["data_generator"]


@router.post("/forecaster/run")
async def run_forecaster(request: ForecasterRequest, background_tasks: BackgroundTasks):
    """
    Trigger forecasting process
    Runs LightGBM, XGBoost, and Random Forest models
    Saves results to media/forecast
    """
    if pipeline_status["forecaster"]["status"] == "running":
        raise HTTPException(status_code=409, detail="Forecaster is already running")
    
    background_tasks.add_task(run_forecaster_task, request.target_column, request.horizon_days)
    
    return {
        "message": "Forecaster started",
        "target_column": request.target_column,
        "horizon_days": request.horizon_days,
        "status": "running"
    }


@router.get("/forecaster/status")
async def get_forecaster_status():
    """Get current status of forecaster"""
    return pipeline_status["forecaster"]


@router.post("/resource-allocator/run")
async def run_resource_allocator(request: ResourceAllocatorRequest, background_tasks: BackgroundTasks):
    """
    Trigger resource allocation process
    Generates staffing and inventory recommendations
    Saves results to media/allocations
    """
    if pipeline_status["resource_allocator"]["status"] == "running":
        raise HTTPException(status_code=409, detail="Resource allocator is already running")
    
    background_tasks.add_task(
        run_resource_allocator_task,
        request.condition_type,
        request.target_department
    )
    
    return {
        "message": "Resource allocator started",
        "condition_type": request.condition_type,
        "target_department": request.target_department,
        "status": "running"
    }


@router.get("/resource-allocator/status")
async def get_resource_allocator_status():
    """Get current status of resource allocator"""
    return pipeline_status["resource_allocator"]


@router.post("/full-pipeline/run")
async def run_full_pipeline(request: FullPipelineRequest, background_tasks: BackgroundTasks):
    """
    Run complete pipeline: Data Generation -> Forecasting -> Resource Allocation
    """
    if pipeline_status["full_pipeline"]["status"] == "running":
        raise HTTPException(status_code=409, detail="Full pipeline is already running")
    
    background_tasks.add_task(run_full_pipeline_task, request)
    
    return {
        "message": "Full pipeline started",
        "configuration": request.dict(),
        "status": "running"
    }


@router.get("/full-pipeline/status")
async def get_full_pipeline_status():
    """Get current status of full pipeline"""
    return pipeline_status["full_pipeline"]


@router.get("/status/all")
async def get_all_pipeline_status():
    """Get status of all pipeline components"""
    return pipeline_status
