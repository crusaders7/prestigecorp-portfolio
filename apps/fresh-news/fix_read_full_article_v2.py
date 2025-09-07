# Read the index.html file
with open('fresh-news-deployment/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Count occurrences before fixing
read_full_count = content.count('Read Full Article')
toggle_count = content.count('toggleArticle')
print(f"Found {read_full_count} 'Read Full Article' buttons before fixing")
print(f"Found {toggle_count} 'toggleArticle' functions before fixing")

# Replace the toggleArticle function calls with openArticleInNewTab
# We need to replace the button onclick handler
content = content.replace(
    'onclick="toggleArticle(${index})"',
    'onclick="openArticleInNewTab(${index})"'
)

# Add the new openArticleInNewTab function before the closing </script> tag
function_code = '''
        function openArticleInNewTab(index) {
            // Get the article content
            const contentDiv = document.getElementById(`article-content-${index}`);
            if (!contentDiv) return;
            
            // Get the article data
            const article = scrapedArticles[index];
            if (!article) return;
            
            // Create HTML content for the new window
            const newWindowContent = `
                <!DOCTYPE html>
                <html>
                <head>
                    <title>${article.title || 'Article'}</title>
                    <style>
                        body { 
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                            background: #ffffff;
                            color: #1f2937;
                            max-width: 800px;
                            margin: 0 auto;
                            padding: 20px;
                            line-height: 1.6;
                        }
                        .article-header {
                            border-bottom: 1px solid #e5e7eb;
                            padding-bottom: 20px;
                            margin-bottom: 20px;
                        }
                        .article-content {
                            white-space: pre-wrap;
                        }
                        .article-meta {
                            color: #6b7280;
                            font-size: 0.875rem;
                            margin-top: 20px;
                            padding-top: 20px;
                            border-top: 1px solid #e5e7eb;
                        }
                    </style>
                </head>
                <body>
                    <div class="article-header">
                        <h1>${article.title || 'Untitled Article'}</h1>
                        <div class="article-meta">
                            ${article.date ? `<div>Date: ${article.date}</div>` : ''}
                            <div>Source: ${new URL(article.url).hostname}</div>
                            <div>Length: ${(article.content_length || article.content.length).toLocaleString()} characters</div>
                        </div>
                    </div>
                    <div class="article-content">${article.content.replace(/\n/g, '<br>')}</div>
                    <div class="article-meta">
                        <a href="${article.url}" target="_blank" rel="noopener noreferrer">View Original Source</a>
                    </div>
                </body>
                </html>
            `;
            
            // Open in new window/tab
            const newWindow = window.open('', '_blank');
            newWindow.document.write(newWindowContent);
            newWindow.document.close();
            newWindow.focus();
        }
'''

# Insert the new function before the closing </script> tag
content = content.replace('</script>', function_code + '\n    </script>')

# Count occurrences after fixing
read_full_count_after = content.count('Read Full Article')
toggle_count_after = content.count('toggleArticle')
open_count_after = content.count('openArticleInNewTab')
print(f"Found {read_full_count_after} 'Read Full Article' buttons after fixing")
print(f"Found {toggle_count_after} 'toggleArticle' functions after fixing")
print(f"Found {open_count_after} 'openArticleInNewTab' functions after fixing")

# Write the fixed content back to the file
with open('fresh-news-deployment/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed 'Read Full Article' to open in new tab instead of nested window")
