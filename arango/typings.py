__all__ = [
    "Fields",
    "Headers",
    "Json",
    "Jsons",
    "Params",
    "PrimitiveDataTypes",
    "CompoundDataTypes",
    "DataTypes",
]

from numbers import Number
from typing import Any, Dict, List, MutableMapping, Optional, Sequence, Union

Json = Dict[str, Any]
Jsons = List[Json]
Params = MutableMapping[str, Union[bool, int, str]]
Headers = MutableMapping[str, str]
Fields = Union[str, Sequence[str]]
DriverFlags = List[str]
PrimitiveDataTypes = Optional[Union[bool, Number, str]]
CompoundDataTypes = Optional[
    Union[
        Sequence[Optional[Union[PrimitiveDataTypes, "CompoundDataTypes"]]],
        MutableMapping[str, Optional[Union[PrimitiveDataTypes, "CompoundDataTypes"]]],
    ]
]
DataTypes = Optional[Union[PrimitiveDataTypes, CompoundDataTypes]]
