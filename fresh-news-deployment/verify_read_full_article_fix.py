# Verify that the Read Full Article fix was applied correctly

with open('fresh-news-deployment/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Count occurrences
read_full_count = content.count('Read Full Article')
toggle_count = content.count('toggleArticle')
open_count = content.count('openArticleInNewTab')
function_count = content.count('function openArticleInNewTab')

print(f"'Read Full Article' buttons: {read_full_count}")
print(f"'toggleArticle' functions: {toggle_count}")
print(f"'openArticleInNewTab' functions: {open_count}")
print(f"openArticleInNewTab function definitions: {function_count}")

# Check if the fix was applied
if toggle_count < 2 and open_count >= 1 and function_count >= 1:
    print("✅ Fix applied successfully - Read Full Article now opens in new tab")
else:
    print("❌ Fix may not have been applied correctly")

# Look for the new function
if 'function openArticleInNewTab' in content:
    print("✅ openArticleInNewTab function found")
else:
    print("❌ openArticleInNewTab function not found")
