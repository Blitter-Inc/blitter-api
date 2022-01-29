from datetime import datetime
from typing import Callable
from rest_framework.request import Request

from .types import FetchAPIRequestType, FetchAPIRequestQueryParams


class FetchAPIRequestParser:

    def __init__(self, request: Request) -> None:
        self.query_params = request.query_params
        self.query_param_error_stacks: dict[str, list[str]] = dict(
            request_type=[],
            ordering=[],
            batch_size=[],
            last_refreshed=[],
        )
        self.query_param_validators: dict[str, Callable[[], bool]] = dict(
            request_type=self.__request_type_param_validator,
            ordering=self.__ordering_param_validator,
            batch_size=self.__batch_size_param_validator,
            last_refreshed=self.__last_refreshed_param_validator,
        )
        self.validated = False

    def __missing_param_check(self, param: str, error_stack: list[str]) -> bool:
        if param not in self.query_params:
            error_stack.append("Missing param")
            return True
        return False

    def __request_type_param_validator(self):
        param_error_stack = self.query_param_error_stacks['request_type']
        if self.__missing_param_check('request_type', param_error_stack):
            return
        value = self.query_params['request_type']
        if value not in {FetchAPIRequestType.INITIAL, FetchAPIRequestType.REFRESH}:
            param_error_stack.append("Invalid value provided")

    def __ordering_param_validator(self):
        param_error_stack = self.query_param_error_stacks['ordering']
        if self.__missing_param_check('ordering', param_error_stack):
            return
        value = self.query_params['ordering']
        if value not in {'updated_at', '-updated_at'}:
            param_error_stack.append(
                "Provide a valid object field for ordering")

    def __batch_size_param_validator(self):
        if self.query_params.get('request_type') != FetchAPIRequestType.INITIAL:
            return
        param_error_stack = self.query_param_error_stacks['batch_size']
        if self.__missing_param_check('batch_size', param_error_stack):
            return
        value = self.query_params['batch_size']
        try:
            batch_size = int(value)
            if not isinstance(batch_size, int) or batch_size < 1:
                param_error_stack.append(
                    "Provide a valid integer value (>= 0)")
        except ValueError:
            param_error_stack.append("Provide a valid integer value (>= 0)")

    def __last_refreshed_param_validator(self):
        if self.query_params.get('request_type') != FetchAPIRequestType.REFRESH:
            return
        param_error_stack = self.query_param_error_stacks['last_refreshed']
        if self.__missing_param_check('last_refreshed', param_error_stack):
            return
        value = self.query_params['last_refreshed']
        try:
            parse_datetime_string(value)
        except:
            param_error_stack.append("Provide a valid datetime string")

    def is_valid(self) -> bool:
        for param in ['request_type', 'ordering', 'batch_size', 'last_refreshed']:
            param_validator = self.query_param_validators[param]
            param_validator()
        self.validated = True
        return not any(len(stack) != 0 for stack in self.query_param_error_stacks.values())

    @property
    def error_dict(self) -> dict[str, list[str]]:
        if not self.validated:
            raise Exception("Run is_valid() before using error_dict")
        d: dict[str, list[str]] = dict()
        for param, stack in self.query_param_error_stacks.items():
            if len(stack):
                d[param] = stack
        return d

    @property
    def props(self) -> FetchAPIRequestQueryParams:
        if not self.validated:
            raise Exception("Run is_valid() before using props")
        return FetchAPIRequestQueryParams(
            request_type=self.query_params.get('request_type', ''),
            ordering=self.query_params.get('ordering', ''),
            batch_size=int(self.query_params.get('batch_size', '1')),
            last_refreshed=self.query_params.get('last_refreshed', ''),
        )


def parse_datetime_string(datetime_str: str) -> datetime:
    format_str = f"%Y-%m-%d %H:%M:%S.%f{'Z' if 'Z' in datetime_str else ''}"
    return datetime.strptime(datetime_str, format_str)
