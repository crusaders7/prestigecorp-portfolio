import re

# Read the index.html file
with open('fresh-news-deployment/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Count occurrences before fixing
count_before = len(re.findall(r'target="_blank"', content))
rel_count_before = len(re.findall(r'rel="noopener noreferrer"', content))

print(f"Found {count_before} occurrences of target='_blank' before fixing")
print(
    f"Found {rel_count_before} occurrences of rel='noopener noreferrer' before fixing")

# Add rel="noopener noreferrer" to all target="_blank" links that don't already have it
# This regex looks for target="_blank" that is not followed by rel="noopener noreferrer"
fixed_content = re.sub(r'(target="_blank")(?!.*?rel="noopener noreferrer")',
                       r'\1 rel="noopener noreferrer"', content)

# Count occurrences after fixing
count_after = len(re.findall(r'target="_blank"', fixed_content))
rel_count_after = len(re.findall(r'rel="noopener noreferrer"', fixed_content))

print(f"Found {count_after} occurrences of target='_blank' after fixing")
print(
    f"Found {rel_count_after} occurrences of rel='noopener noreferrer' after fixing")

# Write the fixed content back to the file
with open('fresh-news-deployment/index.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed all target='_blank' links to include rel='noopener noreferrer'")
