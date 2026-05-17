def make_state_dict(state, var_names):
    return {name: val for name, val in zip(var_names, state)}

class StateAccessor:
    def __init__(self, state, var_names):
        self._state = state
        self._var_names = var_names
        self._dict = dict(zip(var_names, state))
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._state[key]
        return self._dict[key]
    
    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        if name in self._dict:
            return self._dict[name]
        raise AttributeError(f"No variable named '{name}'")
    
    def __repr__(self):
        return "{" + ", ".join(f"{k}: {v:.6f}" for k, v in self._dict.items()) + "}"
    
    def to_list(self):
        return self._state
    
    def to_dict(self):
        return self._dict.copy()
