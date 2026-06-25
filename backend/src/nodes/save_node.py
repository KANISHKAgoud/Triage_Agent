from backend.src.graph.state import AgentState

from backend.src.services.storage_service import save_triage_result
from backend.src.storage.postgres_storage import save_triage_result_pg

from backend.ticket_status import TRIAGED


def save_node(state: AgentState):

    print("Saving Triage Result")

    save_triage_result(
        ticket_id=state["ticket_id"],
        query=state["query"],
        category=state["predicted_category"],
        subcategory=state["predicted_subcategory"],
        resolution=state["recommended_resolution"],
        ticket_status=TRIAGED,
    )

    save_triage_result_pg(
        ticket_id=state["ticket_id"],
        query=state["query"],
        category=state["predicted_category"],
        subcategory=state["predicted_subcategory"],
        resolution=state["recommended_resolution"],
        ticket_status=TRIAGED,
    )

    return state