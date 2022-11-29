__all__ = ["Fields", "Headers", "Json", "Jsons", "Params"]

from typing import Any, Dict, List, MutableMapping, Sequence, Union

Json = Dict[str, Any]
Jsons = List[Json]
Params = MutableMapping[str, Union[bool, int, str]]
Headers = MutableMapping[str, str]
Fields = Union[str, Sequence[str]]
DriverFlags = List[str]
