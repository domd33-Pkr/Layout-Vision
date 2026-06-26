import re
layer_pattern = re.compile(r"layer_state_changed: layer (\d+) state (\d+)")
line = "[00:00:00.000,000] <inf> zmk: layer_state_changed: layer 4 state 1"
m = layer_pattern.search(line)
if m:
    print(f"Matched! Layer: {m.group(1)}, State: {m.group(2)}")
else:
    print("Not matched!")
