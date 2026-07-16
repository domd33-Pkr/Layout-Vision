import re

layer_pattern = re.compile(r"(?:layer_state_changed: layer (\d+) state (\d+|true|false))|(?:layer_changed: layer (\d+) state (\d+|true|false))")

lines = [
    "[00:00:00.000,000] <inf> zmk: layer_state_changed: layer 4 state 1",
    "[00:00:00.000,000] <inf> zmk: layer_state_changed: layer 4 state true",
    "[00:00:00.000,000] <inf> zmk: layer_changed: layer 5 state false",
    "[00:00:00.000,000] <inf> zmk: layer_changed: layer 2 state 0 locked 0"
]

for line in lines:
    m = layer_pattern.search(line)
    if m:
        if m.group(1) is not None:
            layer = int(m.group(1))
            state_str = m.group(2)
        else:
            layer = int(m.group(3))
            state_str = m.group(4)
        state = state_str.lower() in ('1', 'true')
        print(f"Matched: '{line}' -> Layer: {layer}, State: {state}")
    else:
        print(f"FAILED to match: '{line}'")
