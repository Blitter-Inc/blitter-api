from dataclasses import dataclass
from typing import TypedDict, NamedTuple


class FetchAPIResponseDict(TypedDict):
    total_count: int
    ordering: str
    ordered_sequence: list[int]


@dataclass
class FetchAPIRequestType:
    INITIAL = 'initial'
    REFRESH = 'refresh'


class FetchAPIRequestQueryParams(NamedTuple):
    request_type: str
    ordering: str
    batch_size: int
    last_refreshed: str
