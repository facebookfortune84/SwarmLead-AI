import sys

with open('core/agents/governance/governance_agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace special unicode characters
replacements = {
    '\u2014': '--',   # em dash
    '\u2013': '-',    # en dash
    '\u2018': "'",     # left single quote
    '\u2019': "'",     # right single quote
    '\u201c': '"',     # left double quote
    '\u201d': '"',     # right double quote
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('core/agents/governance/governance_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed encoding issues in governance_agent.py')