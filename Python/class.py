

from typing import Any


class SuperDict:
    def __init__(self):
        self._data = {}
        pass
    
    def __setitem__(self, k: Any, v: Any) -> None:
        self._data.update({k:v})
    
    def __getitem__(self, name: Any) -> Any:
        val = self._data.get(name)
        
        if isinstance(val, str):
            return val.upper()
        
        return val

    def __repr__(self):
        return f"SuperDict({self._data})"

sd = SuperDict()

sd["name"] = "dae"
sd["age"] = 23

print(sd["name"])
print(sd["age"])

print(sd)