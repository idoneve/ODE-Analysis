"""
System function helpers for dynamic variable handling.
Useful when you want unpacking-like behavior for arbitrary numbers of variables.

USAGE EXAMPLES:
    
    # Using StateAccessor with attribute access
    state = [1.0, 2.0, 3.0]
    var_names = ['x', 'y', 'z']
    s = StateAccessor(state, var_names)
    x = s.x  # Access by attribute
    y = s['y']  # Or dict-like access
    
    # In a system function
    def system_func(t, state):
        s = StateAccessor(state, ['x', 'y', 'z'])
        dx = -s.y - s.z
        dy = s.x + 0.1 * s.y
        dz = 0.1 + s.z * (s.x - 5.7)
        return [dx, dy, dz]
    
    # Alternative: Using make_state_dict
    state_dict = make_state_dict([1, 2, 3], ['x', 'y', 'z'])
    x = state_dict['x']
"""


def make_state_dict(state, var_names):
    """
    Convert state list to dictionary for easier access.
    
    Example:
        state_dict = make_state_dict([1, 2, 3], ['x', 'y', 'z'])
        # {'x': 1, 'y': 2, 'z': 3}
        x = state_dict['x']
    """
    return {name: val for name, val in zip(var_names, state)}


class StateAccessor:
    """
    Convenient object for accessing state by variable name.
    Supports both dict-like and attribute access.
    
    Example:
        state = StateAccessor([1, 2, 3], ['x', 'y', 'z'])
        x = state.x  or  x = state['x']
        print(state)  # Prints readable representation
    """
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
        """Return state as list."""
        return self._state
    
    def to_dict(self):
        """Return state as dictionary."""
        return self._dict.copy()



