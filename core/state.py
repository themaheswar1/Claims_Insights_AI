from typing import TypedDict, List, Optional, Any

class AgentState(TypedDict):
    user_query : str  # what user asked

    # For agent1 - schema discovery
    schema_db1 : dict
    schema_db2 : dict

    # For agent2 - query building
    sql_query : str
    query_valid : bool
    query_error : str

    # For agent3 - DB executions
    db1_results : List[dict]
    db2_results : List[dict]
    execution_error: str 

    # Agent 4 - Analyst
    diff_report : dict
    anomalies : List[dict]
    summary : str

    # Agent 5 - Chat
    response: str
    memory : List[dict]

    # Quardrails
    blocked : bool
    block_reason: str

    # Metadata
    agent_path : List[str]
    session_id: str
