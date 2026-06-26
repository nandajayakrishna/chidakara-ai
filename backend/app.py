from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import UploadFile
from fastapi import File
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from rag.ingest import ingest_document
from rag.rag_pipeline import ask_question

app = FastAPI(
    title="Chidakara Knowledge Assistant"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str
    workspaceId: str = "default"


class SimulationRequest(BaseModel):
    type: str
    targetId: str


@app.get("/")
def home():
    return {
        "message": "Chidakara Knowledge Assistant Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/debug")
def get_debug():
    from debug.trace_builder import get_latest_trace
    trace = get_latest_trace()
    if not trace:
        return {"message": "No traces recorded yet."}
    return {
        "latest_trace_id": trace.get("trace_id"),
        "parallel_metrics": trace.get("parallel_metrics", {})
    }


@app.post("/ask")
def ask(data: QuestionRequest):

    result = ask_question(
        data.question,
        workspace_id=data.workspaceId
    )

    return result
@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join("uploads", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunks = ingest_document(file_path)

    return {
        "status": "success",
        "chunks_created": chunks
    }
@app.get("/trace/latest")
def get_latest():
    from debug.trace_builder import get_latest_trace
    from fastapi import HTTPException
    trace = get_latest_trace()
    if not trace:
        raise HTTPException(status_code=404, detail="No traces recorded yet.")
    return trace


@app.get("/trace/history")
def get_history():
    from debug.trace_builder import get_trace_history
    return get_trace_history()


@app.get("/trace/{trace_id}")
def get_trace(trace_id: str):
    from debug.trace_builder import get_trace_by_id
    from fastapi import HTTPException
    trace = get_trace_by_id(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace with ID {trace_id} not found.")
    return trace


@app.get("/memory")
def get_memory(workspaceId: str = "default"):
    from agents.memory_agent import get_conversation_history
    return get_conversation_history(workspace_id=workspaceId)


@app.post("/memory/clear")
def clear_mem(workspaceId: str = "default"):
    from agents.memory_agent import clear_memory
    clear_memory(workspace_id=workspaceId)
    return {"status": "success"}


# ==========================================
# ORGANIZATION INTELLIGENCE MODULE ENDPOINTS
# ==========================================

@app.get("/organization/overview")
def get_org_overview():
    from organization.reasoners.org_reasoner import OrganizationReasoner
    from organization.models.org_graph import org_graph_instance
    
    reasoner = OrganizationReasoner()
    health = reasoner.reason_about_health()
    serialized = org_graph_instance.serialize()
    
    return {
        "total_nodes": len(serialized["nodes"]),
        "total_edges": len(serialized["edges"]),
        "health_report": health,
        "highlights": [
            "Chidakara Intelligence Graph mapped 3 active departments and teams.",
            "Identified 1 single point of failure (SPOF) developer constraint.",
            "Detected 1 obsolete version dependency (CUDA 11.2) actively utilized."
        ]
    }


@app.get("/organization/graph")
def get_org_graph():
    from organization.models.org_graph import org_graph_instance
    return org_graph_instance.serialize()


@app.get("/organization/insights")
def get_org_insights():
    from organization.analyzers.org_analyzer import OrganizationAnalyzer
    analyzer = OrganizationAnalyzer()
    return analyzer.run_all_analysis()


@app.get("/organization/recommendations")
def get_org_recommendations():
    from organization.recommenders.org_recommender import OrganizationRecommender
    recommender = OrganizationRecommender()
    return recommender.get_recommendations()


@app.post("/organization/simulate")
def post_org_simulate(req: SimulationRequest):
    from organization.simulators.org_simulator import OrganizationSimulator
    simulator = OrganizationSimulator()
    return simulator.run_simulation(req.type, req.targetId)


# ==========================================
# ENTERPRISE CONNECTOR FRAMEWORK ENDPOINTS
# ==========================================

class ConnectRequest(BaseModel):
    provider: str
    config: Dict[str, Any] = {}

class DisconnectRequest(BaseModel):
    provider: str

class SyncRequest(BaseModel):
    provider: str
    mode: str = "full"


@app.get("/connectors")
def get_connectors():
    from connectors.sync.sync_engine import sync_engine_instance
    return sync_engine_instance.get_connectors_info()


@app.post("/connectors/connect")
def post_connect(data: ConnectRequest):
    from connectors.sync.sync_engine import sync_engine_instance
    success = sync_engine_instance.connect_provider(data.provider, data.config)
    return {"success": success}


@app.post("/connectors/disconnect")
def post_disconnect(data: DisconnectRequest):
    from connectors.sync.sync_engine import sync_engine_instance
    success = sync_engine_instance.disconnect_provider(data.provider)
    return {"success": success}


@app.post("/connectors/sync")
def post_sync(data: SyncRequest):
    from connectors.sync.sync_engine import sync_engine_instance
    result = sync_engine_instance.sync_provider(data.provider, data.mode)
    return result


@app.get("/connectors/status")
def get_connectors_status():
    from connectors.sync.sync_engine import sync_engine_instance
    return sync_engine_instance.get_status()


@app.get("/connectors/history")
def get_connectors_history():
    from connectors.sync.sync_engine import sync_engine_instance
    return sync_engine_instance.sync_history


# ==========================================
# ENTERPRISE DECISION INTELLIGENCE ENDPOINTS
# ==========================================

decision_history_log = []

class AnalyzeRequest(BaseModel):
    type: str
    weights: Dict[str, float] = {}
    customParams: Dict[str, Any] = {}

class CompareRequest(BaseModel):
    type: str
    weights: Dict[str, float] = {}
    customParams: Dict[str, Any] = {}

class ReportRequest(BaseModel):
    type: str
    weights: Dict[str, float] = {}
    customParams: Dict[str, Any] = {}


@app.get("/decision/templates")
def get_decision_templates():
    return [
        {"id": "upgrade_software", "name": "Upgrade software version", "description": "Evaluate upgrading tech version dependencies (e.g., CUDA 11.2 to 12.8)"},
        {"id": "adopt_technology", "name": "Adopt technology framework", "description": "Assess adoption of a new language or framework (e.g., Go Language)"},
        {"id": "delay_project", "name": "Delay active project", "description": "Measure cascading delays across products and delivery pipelines"}
    ]


@app.post("/decision/analyze")
def post_decision_analyze(data: AnalyzeRequest):
    from decision.evaluators.decision_evaluator import DecisionEvaluator
    evaluator = DecisionEvaluator()
    decision = evaluator.evaluate(data.type, data.weights, data.customParams)
    
    global decision_history_log
    decision_history_log.append(decision)
    
    return decision.to_dict()


@app.post("/decision/compare")
def post_decision_compare(data: CompareRequest):
    from decision.evaluators.decision_evaluator import DecisionEvaluator
    from decision.strategies.strategy_engine import StrategyEngine
    evaluator = DecisionEvaluator()
    strategy_engine = StrategyEngine()
    
    decision = evaluator.evaluate(data.type, data.weights, data.customParams)
    comparison = strategy_engine.compare_strategies(decision)
    return comparison


@app.post("/decision/report")
def post_decision_report(data: ReportRequest):
    from decision.evaluators.decision_evaluator import DecisionEvaluator
    from decision.strategies.strategy_engine import StrategyEngine
    from decision.reports.report_generator import ReportGenerator
    evaluator = DecisionEvaluator()
    strategy_engine = StrategyEngine()
    report_gen = ReportGenerator()
    
    decision = evaluator.evaluate(data.type, data.weights, data.customParams)
    comparison = strategy_engine.compare_strategies(decision)
    report = report_gen.generate_report(decision, comparison)
    return {"report": report}


@app.get("/decision/history")
def get_decision_history():
    global decision_history_log
    return [d.to_dict() for d in decision_history_log]



