import re

# Read the index.html file
with open('fresh-news-deployment/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Look for the Read Full Article button creation
# This is in the displayScrapedArticles function where the button is created
pattern = r'(<button\s+[^>]*onclick="toggleArticle\([^>]*>\s*<i[^>]*></i>\s*Read Full Article\s*</button>)'
matches = re.findall(pattern, content)

print(f"Found {len(matches)} 'Read Full Article' buttons")

# The issue is that the toggleArticle function shows content within the same page,
# but the user is experiencing a nested window issue.
# Let's modify the button to open content in a new tab/window instead of toggling visibility

# Find the entire article content section where the button is created
article_pattern = r'(<div class="mb-3">\s*<button\s+[^>]*onclick="toggleArticle\([^>]*>\s*<i[^>]*></i>\s*Read Full Article\s*</button>\s*</div>\s*<div id="article-content-\$\{index\}"[^>]*>.*?</div>\s*</div>)'
article_matches = re.findall(article_pattern, content, re.DOTALL)

print(
    f"Found {len(article_matches)} article sections with Read Full Article buttons")

# Let's replace the toggle button with a link that opens in a new tab
# We'll create a function to open the content in a new window/tab
replacement = r'''
                    <div class="mb-3">
                        <button 
                            onclick="openArticleInNewTab(${index})" 
                            class="text-indigo-400 hover:text-indigo-300 text-sm font-medium focus:outline-none transition-colors flex items-center"
                            id="toggle-btn-${index}"
                        >
                            <i class="fas fa-book-open mr-2"></i>
                            Read Full Article
                        </button>
                    </div>
                    <div id="article-content-${index}" class="hidden mt-4 p-6 bg-black/30 rounded-xl border border-gray-600">
                        <div class="prose prose-invert max-w-none">
                            <div class="text-gray-200 leading-relaxed whitespace-pre-wrap text-base" style="line-height: 1.7;">
                                ${article.content.replace(/\n\s*\n/g, '\n\n').replace(/\n/g, '\n\n')}
                            </div>
                        </div>
                        <div class="mt-6 pt-4 border-t border-gray-600 flex justify-between items-center">
                            <div class="flex items-center space-x-4 text-sm text-gray-400">
                                <span><i class="fas fa-word mr-1"></i>~${Math.round((article.content_length || article.content.length) / 5)} words</span>
                                <span><i class="fas fa-clock mr-1"></i>~${Math.round((article.content_length || article.content.length) / 1000)} min read</span>
                            </div>
                            <a href="${article.url}" target="_blank" rel="noopener noreferrer"
                               class="inline-flex items-center text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors">
                                <i class="fas fa-link mr-1"></i>
                                Original Source
                                <i class="fas fa-external-link-alt ml-1 text-xs"></i>
                            </a>
                        </div>
                    </div>
'''

# Also need to add the new function to open articles in a new tab
function_pattern = r'(</script>)'
function_replacement = r'''
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
''' + r'\1'

# Apply both replacements
fixed_content = re.sub(article_pattern, replacement, content, flags=re.DOTALL)
fixed_content = re.sub(function_pattern, function_replacement, fixed_content)

# Write the fixed content back to the file
with open('fresh-news-deployment/index.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed 'Read Full Article' to open in new tab instead of nested window")
