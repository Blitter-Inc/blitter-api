from typing import TypedDict

from blitter.shared.types import FetchAPIResponseDict


class BillSubscriberResponseDict(TypedDict):
    user: int
    amount: str
    amount_paid: str
    fulfilled: bool
    created_at: str
    updated_at: str


class BillAttachmentResponseDict(TypedDict):
    name: str
    file: str
    created_at: str
    updated_at: str


class BillResponseDict(TypedDict):
    id: int
    name: str
    type: str
    description: str
    status: str
    amount: str
    settled_amount: str
    created_by: int
    created_at: str
    updated_at: str
    subscribers: list[BillSubscriberResponseDict]
    attachments: list[BillAttachmentResponseDict]


class BillFetchAPIResponseDict(FetchAPIResponseDict):
    object_map: dict[str, BillResponseDict]
