from typing import Optional, Dict, Any, List
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

def _eq(key: str, value: str) -> FieldCondition:
    return FieldCondition(key=key, match=MatchValue(value=value))

def build_filter(
    department: Optional[str] = None,
    category: Optional[str] = None,
    document_type: Optional[str] = None,
    region: Optional[str] = None,
    dataset_name: Optional[str] = None,
    created_from: Optional[str] = None,  
    created_to: Optional[str] = None,
) -> Optional[Filter]:
    must: List[FieldCondition] = []

    if department:
        must.append(_eq("department", department))
    if category:
        must.append(_eq("category", category))
    if document_type:
        must.append(_eq("document_type", document_type))
    if region:
        must.append(_eq("region", region))
    if dataset_name:
        must.append(_eq("dataset_name", dataset_name))

    if created_from or created_to:
        rng = {}
        if created_from:
            rng["gte"] = created_from
        if created_to:
            rng["lte"] = created_to
        must.append(FieldCondition(key="created_at", range=Range(**rng)))

    if not must:
        return None

    return Filter(must=must)
