import json
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time


def handler(event, context):
    """
    Vercel serverless function for website audit
    """

    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }

    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        url = body.get('url', '').strip()

        if not url:
            return error_response('URL is required', 400)

        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            parsed_url = urlparse(url)
            if not parsed_url.netloc:
                return error_response('Invalid URL format', 400)
        except Exception:
            return error_response('Invalid URL format', 400)

        # Perform audit
        audit_results = perform_audit(url)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(audit_results)
        }

    except Exception as e:
        print(f"Audit error: {str(e)}")
        return error_response(f'Audit failed: {str(e)}', 500)


def perform_audit(url):
    """
    Perform comprehensive website audit
    """

    results = {
        'url': url,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'overall_score': 0,
        'seo_score': 0,
        'performance_score': 0,
        'accessibility_score': 0,
        'security_score': 0,
        'pages_analyzed': 0,
        'issues_found': [],
        'recommendations': []
    }

    try:
        # Fetch the main page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # SEO Analysis
        seo_score, seo_issues, seo_recommendations = analyze_seo(soup, url)
        results['seo_score'] = seo_score
        results['issues_found'].extend(
            [f"SEO: {issue}" for issue in seo_issues])
        results['recommendations'].extend(
            [f"SEO: {rec}" for rec in seo_recommendations])

        # Performance Analysis
        performance_score, perf_issues, perf_recommendations = analyze_performance(
            response, soup)
        results['performance_score'] = performance_score
        results['issues_found'].extend(
            [f"Performance: {issue}" for issue in perf_issues])
        results['recommendations'].extend(
            [f"Performance: {rec}" for rec in perf_recommendations])

        # Accessibility Analysis
        accessibility_score, acc_issues, acc_recommendations = analyze_accessibility(
            soup)
        results['accessibility_score'] = accessibility_score
        results['issues_found'].extend(
            [f"Accessibility: {issue}" for issue in acc_issues])
        results['recommendations'].extend(
            [f"Accessibility: {rec}" for rec in acc_recommendations])

        # Security Analysis
        security_score, sec_issues, sec_recommendations = analyze_security(
            response, url)
        results['security_score'] = security_score
        results['issues_found'].extend(
            [f"Security: {issue}" for issue in sec_issues])
        results['recommendations'].extend(
            [f"Security: {rec}" for rec in sec_recommendations])

        # Calculate overall score
        results['overall_score'] = round(
            (seo_score + performance_score + accessibility_score + security_score) / 4)

        results['pages_analyzed'] = 1

        # Add summary statistics
        results['total_issues'] = len(results['issues_found'])
        results['total_recommendations'] = len(results['recommendations'])

        # Add priority levels to recommendations
        priority_recommendations = []
        for rec in results['recommendations']:
            if any(word in rec.lower() for word in ['critical', 'missing', 'https', 'security']):
                priority_recommendations.append(
                    {'text': rec, 'priority': 'high'})
            elif any(word in rec.lower() for word in ['optimize', 'improve', 'consider']):
                priority_recommendations.append(
                    {'text': rec, 'priority': 'medium'})
            else:
                priority_recommendations.append(
                    {'text': rec, 'priority': 'low'})

        results['priority_recommendations'] = priority_recommendations

        return results

    except requests.RequestException as e:
        results['error'] = f'Failed to fetch website: {str(e)}'
        return results
    except Exception as e:
        results['error'] = f'Analysis failed: {str(e)}'
        return results


def analyze_seo(soup, url):
    """Analyze SEO factors with detailed recommendations"""
    score = 0
    issues = []
    recommendations = []

    # Title tag analysis
    title = soup.find('title')
    if title and title.get_text().strip():
        title_text = title.get_text().strip()
        title_length = len(title_text)

        if title_length > 0:
            score += 20
            if title_length <= 60:
                score += 10
            elif title_length > 60:
                issues.append(
                    f"Title tag is {title_length} characters (recommended: 50-60)")
                recommendations.append(
                    "Shorten your title tag to 50-60 characters for better search engine display")
        else:
            issues.append("Title tag is empty")
            recommendations.append(
                "Add a descriptive title tag with your primary keywords")
    else:
        issues.append("Missing title tag")
        recommendations.append(
            "Add a title tag to improve search engine visibility")

    # Favicon analysis
    favicon = soup.find('link', rel=lambda x: x and 'icon' in x.lower(
    )) or soup.find('link', rel='shortcut icon')
    if favicon:
        score += 5
    else:
        recommendations.append(
            "Add a favicon to improve brand recognition and user experience")

    # Meta description analysis
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content', '').strip():
        desc_content = meta_desc.get('content', '').strip()
        desc_length = len(desc_content)
        score += 20

        if desc_length < 120:
            recommendations.append(
                "Meta description could be longer for better search engine display (120-160 characters)")
        elif desc_length > 160:
            issues.append(
                f"Meta description is {desc_length} characters (recommended: 120-160)")
            recommendations.append(
                "Shorten your meta description to 120-160 characters")
        else:
            score += 5  # Bonus for optimal length
    else:
        issues.append("Missing meta description")
        recommendations.append(
            "Add a compelling meta description to improve click-through rates")

    # Keywords meta tag (discouraged but still check)
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if meta_keywords:
        recommendations.append(
            "Meta keywords tag is deprecated and ignored by search engines - consider removing")

    # Robots meta tag
    robots_meta = soup.find('meta', attrs={'name': 'robots'})
    if robots_meta:
        robots_content = robots_meta.get('content', '').lower()
        if 'noindex' in robots_content:
            issues.append(
                "Page is set to noindex - it won't appear in search results")
        score += 3
    else:
        recommendations.append(
            "Consider adding robots meta tag for explicit indexing control")

    # H1 tag analysis
    h1_tags = soup.find_all('h1')
    if h1_tags:
        score += 15
        if len(h1_tags) == 1:
            score += 10
            h1_text = h1_tags[0].get_text().strip()
            if len(h1_text) > 70:
                recommendations.append(
                    "H1 tag is quite long - consider shortening for better readability")
        elif len(h1_tags) > 1:
            issues.append(f"Multiple H1 tags found ({len(h1_tags)})")
            recommendations.append(
                "Use only one H1 tag per page for better SEO structure")
    else:
        issues.append("Missing H1 tag")
        recommendations.append("Add an H1 tag with your main page keyword")

    # Schema markup analysis
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    if json_ld_scripts:
        score += 10
        try:
            for script in json_ld_scripts:
                if script.string:
                    import json
                    schema_data = json.loads(script.string)
                    if isinstance(schema_data, dict) and '@type' in schema_data:
                        score += 5
                        break
        except:
            recommendations.append(
                "JSON-LD schema markup found but may have syntax errors")
    else:
        recommendations.append(
            "Add structured data (Schema.org) markup to help search engines understand your content")

    # Heading hierarchy
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if len(headings) >= 2:
        score += 10
    else:
        recommendations.append(
            "Use proper heading hierarchy (H1, H2, H3) to structure your content")

    # Meta viewport
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport:
        score += 10
    else:
        issues.append("Missing viewport meta tag")
        recommendations.append(
            "Add viewport meta tag for mobile responsiveness")

    # Open Graph tags
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    og_desc = soup.find('meta', attrs={'property': 'og:description'})
    og_image = soup.find('meta', attrs={'property': 'og:image'})

    og_score = 0
    if og_title:
        og_score += 5
    if og_desc:
        og_score += 5
    if og_image:
        og_score += 5

    score += og_score
    if og_score < 15:
        recommendations.append(
            "Add Open Graph tags for better social media sharing")

    # Canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if canonical:
        score += 5
        canonical_url = canonical.get('href', '')
        if not canonical_url.startswith(('http://', 'https://')):
            issues.append("Canonical URL should be absolute, not relative")
    else:
        recommendations.append(
            "Add canonical URL to prevent duplicate content issues")

    # Language attributes
    html_lang = soup.find('html')
    if html_lang and html_lang.get('lang'):
        score += 5
    else:
        issues.append("Missing lang attribute on html element")
        recommendations.append(
            "Add lang attribute to html element for better accessibility and SEO")

    # Meta charset
    charset = soup.find('meta', charset=True) or soup.find(
        'meta', attrs={'http-equiv': 'Content-Type'})
    if charset:
        score += 3
    else:
        issues.append("Missing charset declaration")
        recommendations.append(
            "Add meta charset declaration (preferably UTF-8)")

    # Page loading optimization
    preload_links = soup.find_all('link', rel='preload')
    prefetch_links = soup.find_all('link', rel='prefetch')
    if preload_links or prefetch_links:
        score += 3
    else:
        recommendations.append(
            "Consider using resource hints (preload/prefetch) for critical resources")

    return min(score, 100), issues, recommendations


def analyze_performance(response, soup):
    """Analyze performance factors with detailed insights"""
    score = 0
    issues = []
    recommendations = []

    # Response time analysis
    if hasattr(response, 'elapsed'):
        response_time = response.elapsed.total_seconds()
        if response_time < 0.5:
            score += 25
        elif response_time < 1:
            score += 20
        elif response_time < 2:
            score += 15
            recommendations.append(
                f"Response time is {response_time:.2f}s - consider optimizing server response")
        elif response_time < 3:
            score += 10
            issues.append(
                f"Response time is {response_time:.2f}s (slow: should be <2s)")
            recommendations.append(
                "Optimize server response time with caching and CDN")
        else:
            issues.append(
                f"Response time is {response_time:.2f}s (very slow: should be <1s)")
            recommendations.append(
                "Critical: Server response time is very slow. Immediate optimization needed")

    # Content size analysis
    content_size = len(response.content)
    content_size_mb = content_size / (1024 * 1024)

    if content_size < 50000:  # Less than 50KB
        score += 20
    elif content_size < 100000:  # Less than 100KB
        score += 15
    elif content_size < 500000:  # Less than 500KB
        score += 10
    elif content_size < 1000000:  # Less than 1MB
        score += 5
        issues.append(
            f"Page size is {content_size_mb:.1f}MB (recommended: <0.5MB)")
        recommendations.append(
            "Optimize images and minify CSS/JS to reduce page size")
    else:
        issues.append(
            f"Page size is {content_size_mb:.1f}MB (large: should be <1MB)")
        recommendations.append(
            "Page is very large. Compress images, minify code, and use lazy loading")

    # Images optimization analysis
    images = soup.find_all('img')
    if images:
        images_with_alt = len([img for img in images if img.get('alt')])
        images_without_srcset = len(
            [img for img in images if not img.get('srcset')])
        images_without_loading = len(
            [img for img in images if not img.get('loading')])
        images_without_width_height = len(
            [img for img in images if not (img.get('width') and img.get('height'))])

        alt_ratio = images_with_alt / len(images)
        score += round(alt_ratio * 10)

        # More than 70% missing srcset
        if images_without_srcset > len(images) * 0.7:
            recommendations.append(
                f"Add responsive images (srcset) for better performance on different devices")

        # More than 50% missing lazy loading
        if images_without_loading > len(images) * 0.5:
            recommendations.append(
                f"Add lazy loading to improve initial page load time")

        if images_without_width_height > len(images) * 0.5:
            recommendations.append(
                "Add width and height attributes to images to prevent layout shift")

        # Check for oversized images
        large_images = [img for img in images if img.get('src') and any(
            ext in img.get('src', '').lower() for ext in ['.jpg', '.jpeg', '.png', '.gif'])]
        if len(large_images) > 5:
            recommendations.append(
                "Consider using modern image formats like WebP or AVIF for better compression")
    else:
        score += 10  # No images is neutral for performance

    # CSS optimization
    css_files = soup.find_all('link', rel='stylesheet')
    inline_css = soup.find_all('style')

    css_score = 0
    if len(css_files) <= 2:
        css_score += 15
    elif len(css_files) <= 4:
        css_score += 10
        recommendations.append(
            "Consider combining CSS files to reduce HTTP requests")
    elif len(css_files) <= 6:
        css_score += 5
        issues.append(
            f"Multiple CSS files ({len(css_files)}) may slow page loading")
        recommendations.append(
            "Combine and minify CSS files to improve loading speed")
    else:
        issues.append(f"Too many CSS files ({len(css_files)})")
        recommendations.append(
            "Combine and minify CSS files to improve loading speed")

    score += css_score

    if len(inline_css) > 5:
        recommendations.append(
            "Minimize inline CSS and move to external files for better caching")

    # Check for CSS minification opportunities
    for css_link in css_files:
        href = css_link.get('href', '')
        if '.min.' not in href and 'min.css' not in href:
            recommendations.append(
                "Consider using minified CSS files for better performance")
            break

    # JavaScript optimization
    js_files = soup.find_all('script', src=True)
    inline_js = soup.find_all('script', src=False)

    js_score = 0
    if len(js_files) <= 3:
        js_score += 15
    elif len(js_files) <= 6:
        js_score += 10
        recommendations.append("Consider combining JavaScript files")
    elif len(js_files) <= 10:
        js_score += 5
        issues.append(
            f"Multiple JavaScript files ({len(js_files)}) may impact performance")
        recommendations.append("Combine and minify JavaScript files")
    else:
        issues.append(f"Too many JavaScript files ({len(js_files)})")
        recommendations.append("Combine and minify JavaScript files")

    score += js_score

    # Check for async/defer attributes
    blocking_js = [js for js in js_files if not js.get(
        'async') and not js.get('defer')]
    if len(blocking_js) > 2:
        recommendations.append(
            "Add async or defer attributes to non-critical JavaScript")

    # Check for JS minification
    for js_script in js_files:
        src = js_script.get('src', '')
        if '.min.' not in src and 'min.js' not in src:
            recommendations.append(
                "Consider using minified JavaScript files for better performance")
            break

    # Check for modern JS loading patterns
    module_scripts = soup.find_all('script', type='module')
    if module_scripts:
        score += 3  # Bonus for modern loading

    # Font loading optimization
    font_links = soup.find_all(
        'link', href=lambda x: x and 'font' in x.lower())
    font_preloads = soup.find_all(
        'link', attrs={'rel': 'preload', 'as': 'font'})

    if font_links and not font_preloads:
        recommendations.append(
            "Consider preloading critical fonts to reduce layout shift")

    # Check for content delivery network usage
    external_resources = []
    for resource in css_files + js_files:
        href_or_src = resource.get('href') or resource.get('src', '')
        if href_or_src and ('cdn' in href_or_src.lower() or 'cloudflare' in href_or_src.lower() or 'jsdelivr' in href_or_src.lower()):
            external_resources.append(href_or_src)

    if external_resources:
        score += 5  # Bonus for CDN usage
    else:
        recommendations.append(
            "Consider using a CDN for static assets to improve global loading times")

    return min(score, 100), issues, recommendations


def analyze_accessibility(soup):
    """Analyze accessibility factors with detailed insights"""
    score = 0
    issues = []
    recommendations = []

    # Images with alt text
    images = soup.find_all('img')
    if images:
        images_with_alt = len([img for img in images if img.get(
            'alt') is not None])  # Include empty alt=""
        images_with_meaningful_alt = len(
            [img for img in images if img.get('alt', '').strip()])
        # Properly marked decorative
        images_decorative = len(
            [img for img in images if img.get('alt') == ''])

        # Score based on proper alt usage
        if images_with_alt == len(images):
            score += 25
            if images_with_meaningful_alt > 0:
                score += 5
        else:
            missing_alt = len(images) - images_with_alt
            issues.append(f"{missing_alt} images missing alt attributes")
            recommendations.append(
                "Add alt attributes to all images - use descriptive text or empty alt='' for decorative images")

        # Check for overly long alt text
        long_alt_images = [img for img in images if len(
            img.get('alt', '')) > 125]
        if long_alt_images:
            recommendations.append(
                f"{len(long_alt_images)} images have very long alt text - consider shortening to under 125 characters")
    else:
        score += 25  # No images means no alt text issues

    # Proper heading hierarchy
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if headings:
        score += 10

        # Check heading order and hierarchy
        heading_levels = [int(h.name[1]) for h in headings]

        # Check for proper H1 usage
        h1_count = heading_levels.count(1)
        if h1_count == 1:
            score += 5
        elif h1_count == 0:
            issues.append("No H1 heading found")
            recommendations.append(
                "Add an H1 heading to establish the main topic of the page")
        else:
            issues.append(f"Multiple H1 headings found ({h1_count})")
            recommendations.append("Use only one H1 heading per page")

        # Check for skipped heading levels
        unique_levels = sorted(set(heading_levels))
        for i in range(len(unique_levels) - 1):
            if unique_levels[i + 1] - unique_levels[i] > 1:
                issues.append(
                    f"Heading levels skip from H{unique_levels[i]} to H{unique_levels[i + 1]}")
                recommendations.append(
                    "Don't skip heading levels (e.g., H2 should follow H1, not H3)")
                break

        # Check for empty headings
        empty_headings = [h for h in headings if not h.get_text().strip()]
        if empty_headings:
            issues.append(f"{len(empty_headings)} empty headings found")
            recommendations.append(
                "Remove empty headings or add meaningful content")
    else:
        issues.append("No headings found")
        recommendations.append(
            "Use proper heading structure (H1-H6) to organize content for screen readers")

    # Form accessibility
    forms = soup.find_all('form')
    inputs = soup.find_all(['input', 'textarea', 'select'])

    if forms:
        form_score = 0

        if inputs:
            # Check for labels and ARIA attributes
            properly_labeled = 0
            for inp in inputs:
                inp_id = inp.get('id')
                inp_type = inp.get('type', '').lower()
                aria_label = inp.get('aria-label')
                aria_labelledby = inp.get('aria-labelledby')
                aria_describedby = inp.get('aria-describedby')

                # Skip hidden inputs
                if inp_type == 'hidden':
                    continue

                has_label = False
                if inp_id and soup.find('label', attrs={'for': inp_id}):
                    has_label = True
                elif aria_label or aria_labelledby:
                    has_label = True
                elif inp.find_parent('label'):  # Input wrapped in label
                    has_label = True

                if has_label:
                    properly_labeled += 1

                # Check for required field indicators
                if inp.get('required') and not (aria_label and 'required' in aria_label.lower()):
                    if not soup.find('label', attrs={'for': inp_id}, string=lambda text: text and '*' in text):
                        recommendations.append(
                            "Mark required fields clearly for screen readers")

            visible_inputs = len(
                [inp for inp in inputs if inp.get('type', '').lower() != 'hidden'])
            if visible_inputs > 0:
                label_ratio = properly_labeled / visible_inputs
                form_score += round(label_ratio * 20)

                if label_ratio < 1:
                    unlabeled = visible_inputs - properly_labeled
                    issues.append(
                        f"{unlabeled} form inputs missing proper labels")
                    recommendations.append(
                        "Add labels, aria-label, or aria-labelledby to all form inputs")

        # Check for fieldsets in complex forms
        fieldsets = soup.find_all('fieldset')
        if len(inputs) > 5 and not fieldsets:
            recommendations.append(
                "Use fieldsets with legends to group related form elements")
        elif fieldsets:
            form_score += 5
            # Check fieldsets have legends
            fieldsets_without_legend = [
                fs for fs in fieldsets if not fs.find('legend')]
            if fieldsets_without_legend:
                issues.append(
                    f"{len(fieldsets_without_legend)} fieldsets missing legends")
                recommendations.append(
                    "Add legends to all fieldsets for better form structure")

        # Check for form validation and error handling
        error_elements = soup.find_all(class_=lambda x: x and (
            'error' in x.lower() or 'invalid' in x.lower()))
        if not error_elements and len(inputs) > 2:
            recommendations.append(
                "Implement accessible error messaging for form validation")

        score += form_score
    else:
        score += 20  # No forms is neutral

    # Language and document structure
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        score += 8
        lang_value = html_tag.get('lang', '')
        if len(lang_value) < 2:
            issues.append("Invalid lang attribute format")
            recommendations.append(
                "Use proper language codes (e.g., 'en', 'en-US') for the lang attribute")
    else:
        issues.append("Missing lang attribute on html element")
        recommendations.append(
            "Add lang attribute to html element for screen readers")

    # Page title
    title = soup.find('title')
    if not title or not title.get_text().strip():
        issues.append("Missing or empty page title")
        recommendations.append(
            "Add a descriptive page title for screen readers and browser tabs")
    else:
        score += 5

    # Skip navigation links
    skip_links = soup.find_all('a', href=lambda x: x and x.startswith('#'))
    has_skip_nav = any('skip' in link.get_text().lower(
    ) or 'jump' in link.get_text().lower() for link in skip_links)
    if has_skip_nav:
        score += 5
    else:
        recommendations.append("Add skip navigation links for keyboard users")

    # Link and button accessibility
    links = soup.find_all('a')
    if links:
        link_issues = 0
        empty_links = []

        for link in links:
            link_text = link.get_text().strip()
            aria_label = link.get('aria-label', '').strip()
            title = link.get('title', '').strip()

            # Check for descriptive link text
            if not link_text and not aria_label:
                empty_links.append(link)
            elif link_text.lower() in ['click here', 'read more', 'more', 'here', 'link']:
                link_issues += 1

            # Check for target="_blank" without warning
            if link.get('target') == '_blank' and not aria_label and 'new window' not in link_text.lower():
                recommendations.append(
                    "Links opening in new windows should inform users (add 'opens in new window' to link text or aria-label)")

        if empty_links:
            issues.append(f"{len(empty_links)} links without descriptive text")
            recommendations.append(
                "Ensure all links have descriptive text or aria-label")

        if link_issues > 0:
            recommendations.append(
                f"{link_issues} links have non-descriptive text like 'click here' - use more meaningful link text")

        if len(empty_links) == 0:
            score += 5

    # Button accessibility
    buttons = soup.find_all('button')
    if buttons:
        empty_buttons = []
        for btn in buttons:
            btn_text = btn.get_text().strip()
            aria_label = btn.get('aria-label', '').strip()

            if not btn_text and not aria_label:
                empty_buttons.append(btn)

        if empty_buttons:
            issues.append(
                f"{len(empty_buttons)} buttons without descriptive text")
            recommendations.append(
                "Add descriptive text or aria-label to all buttons")
        else:
            score += 5

    # Keyboard navigation support
    focusable_elements = soup.find_all(
        ['a', 'button', 'input', 'select', 'textarea'])
    elements_with_tabindex = soup.find_all(attrs={'tabindex': True})
    positive_tabindex = [el for el in elements_with_tabindex if el.get(
        'tabindex', '0').isdigit() and int(el.get('tabindex', '0')) > 0]

    if positive_tabindex:
        issues.append(
            f"{len(positive_tabindex)} elements use positive tabindex values")
        recommendations.append(
            "Avoid positive tabindex values - use 0 or -1, or rely on natural tab order")

    # ARIA landmarks and roles
    landmarks = soup.find_all(attrs={'role': lambda x: x and x.lower() in [
                              'main', 'navigation', 'banner', 'contentinfo', 'complementary']})
    semantic_elements = soup.find_all(
        ['main', 'nav', 'header', 'footer', 'aside', 'section', 'article'])

    if landmarks or semantic_elements:
        score += 8
    else:
        recommendations.append(
            "Use ARIA landmarks or semantic HTML5 elements to structure page content")

    # Color and contrast considerations
    recommendations.append(
        "Ensure sufficient color contrast (4.5:1 for normal text, 3:1 for large text, 7:1 for enhanced)")

    # Media accessibility
    videos = soup.find_all('video')
    audios = soup.find_all('audio')

    if videos:
        videos_with_captions = [v for v in videos if v.find(
            'track', kind='captions') or v.find('track', kind='subtitles')]
        if len(videos_with_captions) < len(videos):
            issues.append(
                f"{len(videos) - len(videos_with_captions)} videos missing captions")
            recommendations.append(
                "Add captions or subtitles to all video content")
        else:
            score += 5

    if audios:
        recommendations.append("Provide transcripts for audio content")

    return min(score, 100), issues, recommendations


def analyze_security(response, url):
    """Analyze security factors with detailed insights"""
    score = 0
    issues = []
    recommendations = []

    # HTTPS check
    if url.startswith('https://'):
        score += 25
    else:
        issues.append("Website not using HTTPS")
        recommendations.append(
            "Enable HTTPS encryption for secure data transmission - this is critical for user trust and SEO")

    # Security headers analysis
    headers = response.headers
    header_scores = 0

    # Strict Transport Security
    hsts_header = headers.get('Strict-Transport-Security', '')
    if hsts_header:
        header_scores += 12
        if 'max-age' in hsts_header:
            try:
                max_age = int(hsts_header.split('max-age=')[1].split(';')[0])
                if max_age >= 31536000:  # 1 year
                    header_scores += 3
                elif max_age < 86400:  # Less than 1 day
                    recommendations.append(
                        "HSTS max-age is too short - consider at least 1 year")
            except:
                pass
        if 'includeSubDomains' in hsts_header:
            header_scores += 2
        if 'preload' in hsts_header:
            header_scores += 3
    else:
        issues.append("Missing HSTS header")
        recommendations.append(
            "Add Strict-Transport-Security header to enforce HTTPS and prevent downgrade attacks")

    # Content Type Options
    if headers.get('X-Content-Type-Options', '').lower() == 'nosniff':
        header_scores += 8
    else:
        issues.append("Missing X-Content-Type-Options header")
        recommendations.append(
            "Add X-Content-Type-Options: nosniff header to prevent MIME sniffing attacks")

    # Frame Options / CSP
    has_frame_protection = False
    x_frame_options = headers.get('X-Frame-Options', '')
    if x_frame_options:
        header_scores += 8
        has_frame_protection = True
        if x_frame_options.upper() not in ['DENY', 'SAMEORIGIN']:
            recommendations.append(
                "X-Frame-Options should be set to DENY or SAMEORIGIN")

    csp_header = headers.get('Content-Security-Policy', '')
    if csp_header:
        header_scores += 15
        has_frame_protection = True

        # Analyze CSP quality
        if 'unsafe-inline' in csp_header:
            issues.append("CSP allows 'unsafe-inline' which reduces security")
            recommendations.append(
                "Remove 'unsafe-inline' from Content Security Policy and use nonces or hashes")
        if 'unsafe-eval' in csp_header:
            issues.append("CSP allows 'unsafe-eval' which is dangerous")
            recommendations.append(
                "Remove 'unsafe-eval' from Content Security Policy")
        if '*' in csp_header and 'data:' not in csp_header:
            recommendations.append(
                "CSP uses wildcards - consider more restrictive policies")

        # Check for important directives
        important_directives = ['default-src',
                                'script-src', 'style-src', 'img-src']
        missing_directives = [
            directive for directive in important_directives if directive not in csp_header]
        if missing_directives:
            recommendations.append(
                f"Consider adding CSP directives: {', '.join(missing_directives)}")

    if not has_frame_protection:
        issues.append("Missing clickjacking protection")
        recommendations.append(
            "Add X-Frame-Options or Content-Security-Policy frame-ancestors directive to prevent clickjacking")

    # XSS Protection (deprecated but still worth checking)
    xss_protection = headers.get('X-XSS-Protection', '')
    if xss_protection:
        if xss_protection == '1; mode=block':
            header_scores += 3
        else:
            recommendations.append(
                "X-XSS-Protection should be '1; mode=block' or removed in favor of CSP")
    else:
        if not csp_header:  # Only recommend if no CSP
            recommendations.append(
                "Consider adding X-XSS-Protection header (though CSP is preferred)")

    # Referrer Policy
    referrer_policy = headers.get('Referrer-Policy', '')
    if referrer_policy:
        header_scores += 5
        if referrer_policy in ['no-referrer', 'strict-origin-when-cross-origin', 'same-origin']:
            header_scores += 3
    else:
        recommendations.append(
            "Add Referrer-Policy header to control referrer information leakage")

    # Permissions Policy (Feature Policy)
    permissions_policy = headers.get(
        'Permissions-Policy', '') or headers.get('Feature-Policy', '')
    if permissions_policy:
        header_scores += 5
    else:
        recommendations.append(
            "Consider adding Permissions-Policy header to control browser features")

    # Additional security headers
    expect_ct = headers.get('Expect-CT', '')
    if expect_ct:
        header_scores += 3

    # Cross-Origin headers
    corp = headers.get('Cross-Origin-Resource-Policy', '')
    coop = headers.get('Cross-Origin-Opener-Policy', '')
    coep = headers.get('Cross-Origin-Embedder-Policy', '')

    if corp or coop or coep:
        header_scores += 5
        recommendations.append(
            "Good use of Cross-Origin headers for enhanced security")
    else:
        recommendations.append(
            "Consider implementing Cross-Origin security headers (CORP, COOP, COEP)")

    score += min(header_scores, 50)  # Cap header score at 50

    # Information disclosure checks
    info_disclosure_score = 0

    server_header = headers.get('Server', '')
    if server_header:
        if any(server in server_header.lower() for server in ['apache', 'nginx', 'iis', 'express']):
            recommendations.append(
                "Consider hiding or customizing Server header to reduce information disclosure")
    else:
        info_disclosure_score += 3  # Good if hidden

    powered_by = headers.get('X-Powered-By', '')
    if powered_by:
        recommendations.append(
            "Remove X-Powered-By header to reduce information disclosure")
    else:
        info_disclosure_score += 3  # Good if not present

    # Check for other revealing headers
    revealing_headers = ['X-AspNet-Version',
                         'X-AspNetMvc-Version', 'X-Generator']
    for header in revealing_headers:
        if header in headers:
            recommendations.append(
                f"Remove {header} header to reduce information disclosure")

    score += info_disclosure_score

    # Content-based security checks
    content_score = 0

    # Check for HTTPS mixed content potential
    if url.startswith('https://'):
        content_score += 5  # Bonus for HTTPS
        recommendations.append(
            "Ensure all resources (images, scripts, stylesheets) are loaded over HTTPS to avoid mixed content warnings")

    # Check response for security indicators
    if hasattr(response, 'url') and response.url != url:
        if not response.url.startswith('https://') and url.startswith('https://'):
            issues.append(
                "HTTPS request redirected to HTTP - potential security issue")
        elif response.url.startswith('https://') and not url.startswith('https://'):
            content_score += 5  # Good - auto-redirect to HTTPS

    score += content_score

    return min(score, 100), issues, recommendations


def error_response(message, status_code):
    """Return standardized error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({
            'error': message,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
    }
