import re

line = "00:00:18.160 --> 00:00:20.310 align:start position:0%"
pattern = r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})\.(\d{3})'
match = re.match(pattern, line)
print(f"Match: {match}")
if match:
    print(match.groups())
