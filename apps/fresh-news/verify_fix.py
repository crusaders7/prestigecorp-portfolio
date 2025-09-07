# Verify that all target="_blank" links have rel="noopener noreferrer"

with open('fresh-news-deployment/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Count total occurrences of target="_blank"
target_blank_count = content.count('target="_blank"')
print(f"Total target='_blank' occurrences: {target_blank_count}")

# Count occurrences of rel="noopener noreferrer"
rel_count = content.count('rel="noopener noreferrer"')
print(f"Total rel='noopener noreferrer' occurrences: {rel_count}")

# Check if they match
if target_blank_count == rel_count:
    print("✅ All target='_blank' links have rel='noopener noreferrer' attribute")
else:
    print(
        f"❌ Mismatch: {target_blank_count} target='_blank' vs {rel_count} rel attributes")

    # Let's find the specific instances that don't have the rel attribute
    import re
    # This pattern finds target="_blank" that is not followed by rel="noopener noreferrer" in the same tag
    pattern = r'<a[^>]*target="_blank"[^>]*>(?:(?!rel="noopener noreferrer").)*?</a>'
    matches = re.findall(pattern, content, re.DOTALL)
    print(
        f"Found {len(matches)} links with target='_blank' but without rel='noopener noreferrer'")
    for i, match in enumerate(matches[:3]):  # Show first 3 matches
        print(f"  {i+1}. {match[:100]}...")
