#!/usr/bin/env python3
"""
NDSS Conference Paper Crawler (2023-2025)
A professional academic tool for collecting NDSS paper metadata including:
titles, authors, affiliations, abstracts, PDF links, slides, videos, etc.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed


class NDSSCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.list_urls = {
            2025: 'https://www.ndss-symposium.org/ndss2025/accepted-papers/',
            2024: 'https://www.ndss-symposium.org/ndss2024/accepted-papers/',
            2023: 'https://www.ndss-symposium.org/ndss2023/accepted-papers/'
        }
    
    def fetch_page(self, url: str, retry=3) -> BeautifulSoup:
        """Fetch web page content with retry mechanism"""
        for attempt in range(retry):
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                if attempt == retry - 1:
                    print(f"    [ERROR] Failed to fetch: {e}")
                    return None
                time.sleep(2)
        return None
    
    def get_paper_urls(self, year: int) -> List[str]:
        """Extract paper detail page URLs from the accepted papers list"""
        url = self.list_urls[year]
        soup = self.fetch_page(url)
        
        if not soup:
            return []
        
        paper_urls = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            # NDSS paper detail page URL pattern
            if '/ndss-paper/' in href and href not in paper_urls:
                paper_urls.append(href)
        
        return paper_urls
    
    def parse_paper(self, url: str, year: int) -> Dict:
        """Parse individual paper detail page and extract metadata"""
        soup = self.fetch_page(url)
        
        if not soup:
            return None
        
        paper = {
            'year': year,
            'title': '',
            'authors': [],
            'affiliations': [],
            'abstract': '',
            'pdf_url': '',
            'slides_url': '',
            'video_url': '',
            'code_url': '',
            'detail_url': url
        }
        
        # 1. Extract title
        title = soup.find('h1', class_='entry-title') or soup.find('h1')
        if title:
            paper['title'] = title.get_text(strip=True)
        
        # 2. Find main content area
        content = soup.find('div', class_='entry-content') or soup.find('article')
        if not content:
            return paper
        
        # 3. Extract authors and affiliations
        for p in content.find_all('p', limit=10):
            text = p.get_text(strip=True)
            # Author paragraph characteristics: contains parentheses and institution names
            if '(' in text and ')' in text and any(kw in text for kw in 
                ['University', 'Institute', 'Lab', 'Inc', 'Corp', 'Google', 'Microsoft', 'Meta', 'KAIST']):
                
                # Split authors
                authors = []
                affiliations = set()
                
                # Try multiple split methods
                parts = re.split(r',(?=\s*[A-Z])|;', text)
                for part in parts:
                    part = part.strip()
                    if part and len(part) < 200:  # Avoid misidentification
                        authors.append(part)
                        # Extract affiliations
                        matches = re.findall(r'\(([^)]+)\)', part)
                        affiliations.update(matches)
                
                if authors:
                    paper['authors'] = authors
                    paper['affiliations'] = sorted(list(affiliations))
                    break
        
        # 4. Extract abstract
        # NDSS stores abstract in <div class="paper-data"> with nested <p> tags
        paper_data_div = content.find('div', class_='paper-data')
        if paper_data_div:
            # The structure is: <div class="paper-data"><p><strong><p>Authors</p></strong></p><p><p>Abstract paragraphs...</p></p></div>
            # We need to skip the first <p> (contains authors) and get subsequent <p> tags
            all_p_tags = paper_data_div.find_all('p', recursive=True)
            
            # Collect abstract paragraphs (skip author paragraph which is inside <strong>)
            abstract_parts = []
            found_first_valid = False
            
            for p in all_p_tags:
                # Skip if this <p> is inside a <strong> tag (author info)
                if p.find_parent('strong'):
                    continue
                
                text = p.get_text(strip=True)
                
                # Skip author paragraph (first valid paragraph usually contains author names with parentheses)
                # It's typically shorter and contains patterns like "Name (Institution)"
                if not found_first_valid:
                    # Check if this looks like an author list (has parentheses and common institution keywords)
                    if ('(' in text and ')' in text and 
                        len(text) < 800 and  # Author lists are typically shorter
                        any(keyword in text for keyword in ['University', 'Institute', 'Inc', 'Corp', 'Lab', 'Center'])):
                        continue  # Skip author paragraph
                
                # Valid abstract paragraph should be reasonably long
                if text and len(text) > 100 and not text.startswith('http'):
                    abstract_parts.append(text)
                    found_first_valid = True
            
            if abstract_parts:
                paper['abstract'] = ' '.join(abstract_parts)
        
        # Fallback: Try other methods if paper-data div not found
        if not paper['abstract']:
            # Method 1: Find div/section with "abstract" in class
            abstract_div = content.find(['div', 'section'], class_=re.compile('abstract', re.I))
            if abstract_div:
                paper['abstract'] = abstract_div.get_text(strip=True).replace('Abstract:', '').replace('ABSTRACT:', '').strip()
            else:
                # Method 2: Find paragraphs after "Abstract" heading
                for heading in content.find_all(['h2', 'h3', 'h4', 'strong']):
                    if 'abstract' in heading.get_text(strip=True).lower():
                        next_elem = heading.find_next(['p', 'div'])
                        if next_elem:
                            abstract_text = next_elem.get_text(strip=True)
                            if len(abstract_text) > 50:  # Ensure it's abstract, not title
                                paper['abstract'] = abstract_text
                                break
        
        # 5. Extract resource links
        for link in content.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True).lower()
            
            # PDF
            if not paper['pdf_url'] and ('pdf' in text or 'paper' in text or href.endswith('.pdf')):
                paper['pdf_url'] = href
            # Slides
            elif not paper['slides_url'] and ('slide' in text or 'presentation' in text or 'ppt' in text):
                paper['slides_url'] = href
            # Video
            elif not paper['video_url'] and ('video' in text or 'youtube.com' in href or 'youtu.be' in href):
                paper['video_url'] = href
            # Code
            elif not paper['code_url'] and ('code' in text or 'github' in href or 'gitlab' in href):
                paper['code_url'] = href
        
        return paper
    
    def crawl_year(self, year: int, max_workers: int = 8) -> List[Dict]:
        """Crawl all papers for a specific year"""
        print(f"\n{'='*80}")
        print(f"  NDSS {year}")
        print(f"{'='*80}")
        
        # Get paper URL list
        print("  [INFO] Fetching paper list...")
        paper_urls = self.get_paper_urls(year)
        
        if not paper_urls:
            print("  [ERROR] No papers found")
            return []
        
        print(f"  [SUCCESS] Found {len(paper_urls)} papers\n")
        print(f"  [INFO] Starting detail crawling ({max_workers} concurrent workers)...\n")
        
        papers = []
        
        # Multi-threaded crawling
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.parse_paper, url, year): url 
                for url in paper_urls
            }
            
            completed = 0
            for future in as_completed(future_to_url):
                completed += 1
                try:
                    paper = future.result()
                    if paper and paper['title']:
                        papers.append(paper)
                        
                        # Display progress
                        title = paper['title'][:60] + '...' if len(paper['title']) > 60 else paper['title']
                        status = []
                        if paper['pdf_url']: status.append('PDF')
                        if paper['slides_url']: status.append('Slides')
                        if paper['video_url']: status.append('Video')
                        if paper['code_url']: status.append('Code')
                        status_str = f"[{', '.join(status)}]" if status else "[No resources]"
                        
                        print(f"  [{completed}/{len(paper_urls)}] {title} {status_str}")
                    else:
                        print(f"  [{completed}/{len(paper_urls)}] [FAILED] Parse error")
                except Exception as e:
                    print(f"  [{completed}/{len(paper_urls)}] [ERROR] {str(e)[:50]}")
                
                # Delay to avoid rate limiting - reduced for faster crawling
                time.sleep(0.3)
        
        # Statistics
        with_pdf = sum(1 for p in papers if p['pdf_url'])
        with_slides = sum(1 for p in papers if p['slides_url'])
        with_video = sum(1 for p in papers if p['video_url'])
        with_abstract = sum(1 for p in papers if p['abstract'])
        
        print(f"\n  [STATISTICS] Summary:")
        print(f"    - Successfully crawled: {len(papers)}/{len(paper_urls)} papers")
        print(f"    - With abstracts: {with_abstract} papers")
        print(f"    - PDF links: {with_pdf} papers")
        print(f"    - Slides links: {with_slides} papers")
        print(f"    - Video links: {with_video} papers")
        
        # Save data for this year
        year_filename = f'ndss_papers_{year}.json'
        self.save_json({year: papers}, year_filename)
        print(f"  [SAVED] Data saved to: {year_filename}")
        
        return papers
    
    def crawl_all(self) -> Dict[int, List[Dict]]:
        """Crawl papers from all years (2023-2025)"""
        print("\n" + "="*80)
        print("  NDSS Conference Paper Crawler (2023-2025)")
        print("="*80)
        
        all_papers = {}
        
        for year in sorted(self.list_urls.keys(), reverse=True):
            papers = self.crawl_year(year)
            all_papers[year] = papers
            time.sleep(1)  # Reduced delay between years
        
        return all_papers
    
    def save_json(self, data: Dict, filename: str = 'ndss_papers.json'):
        """Save data as JSON format"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_markdown(self, data: Dict, filename: str = 'ndss_papers.md'):
        """Save data as Markdown format"""
        total = sum(len(papers) for papers in data.values())
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# NDSS Papers (2023-2025)\n\n")
            f.write(f"Total: **{total}** papers collected\n\n")
            
            for year in sorted(data.keys(), reverse=True):
                papers = data[year]
                f.write(f"## NDSS {year} ({len(papers)} papers)\n\n")
                
                for i, p in enumerate(papers, 1):
                    f.write(f"### {i}. {p['title']}\n\n")
                    
                    # Authors
                    if p['authors']:
                        authors = p['authors'][:5]
                        f.write(f"**Authors:** {', '.join(authors)}")
                        if len(p['authors']) > 5:
                            f.write(f" _et al. ({len(p['authors'])} total)_")
                        f.write("\n\n")
                    
                    # Affiliations
                    if p['affiliations']:
                        f.write(f"**Affiliations:** {'; '.join(p['affiliations'][:5])}\n\n")
                    
                    # Abstract
                    if p['abstract']:
                        abstract = p['abstract'][:400] + '...' if len(p['abstract']) > 400 else p['abstract']
                        f.write(f"**Abstract:** {abstract}\n\n")
                    
                    # Resource links
                    links = []
                    if p['detail_url']:
                        links.append(f"[Details]({p['detail_url']})")
                    if p['pdf_url']:
                        links.append(f"[PDF]({p['pdf_url']})")
                    if p['slides_url']:
                        links.append(f"[Slides]({p['slides_url']})")
                    if p['video_url']:
                        links.append(f"[Video]({p['video_url']})")
                    if p['code_url']:
                        links.append(f"[Code]({p['code_url']})")
                    
                    if links:
                        f.write(f"**Resources:** {' · '.join(links)}\n\n")
                    
                    f.write("---\n\n")
    
    def save_csv(self, data: Dict, filename: str = 'ndss_papers.csv'):
        """Save data as CSV format"""
        import csv
        
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Year', 'Title', 'Authors', 'Affiliations', 'Abstract', 
                'PDF_URL', 'Slides_URL', 'Video_URL', 'Code_URL', 'Detail_URL'
            ])
            writer.writeheader()
            
            for year in sorted(data.keys(), reverse=True):
                for p in data[year]:
                    writer.writerow({
                        'Year': p['year'],
                        'Title': p['title'],
                        'Authors': '; '.join(p['authors']),
                        'Affiliations': '; '.join(p['affiliations']),
                        'Abstract': p['abstract'],
                        'PDF_URL': p['pdf_url'],
                        'Slides_URL': p['slides_url'],
                        'Video_URL': p['video_url'],
                        'Code_URL': p['code_url'],
                        'Detail_URL': p['detail_url']
                    })


def main():
    crawler = NDSSCrawler()
    
    # Crawl all data
    all_papers = crawler.crawl_all()
    
    # Save combined data
    print("\n" + "="*80)
    print("  Saving Combined Data")
    print("="*80 + "\n")
    
    crawler.save_json(all_papers, 'ndss_papers_all.json')
    print("  [SAVED] JSON: ndss_papers_all.json")
    
    crawler.save_markdown(all_papers, 'ndss_papers_all.md')
    print("  [SAVED] Markdown: ndss_papers_all.md")
    
    crawler.save_csv(all_papers, 'ndss_papers_all.csv')
    print("  [SAVED] CSV: ndss_papers_all.csv")
    
    # Final statistics
    total = sum(len(papers) for papers in all_papers.values())
    with_pdf = sum(1 for papers in all_papers.values() for p in papers if p['pdf_url'])
    with_slides = sum(1 for papers in all_papers.values() for p in papers if p['slides_url'])
    with_video = sum(1 for papers in all_papers.values() for p in papers if p['video_url'])
    with_abstract = sum(1 for papers in all_papers.values() for p in papers if p['abstract'])
    
    print("\n" + "="*80)
    print("  Crawling Completed")
    print("="*80)
    print(f"\n  Total: {total} papers")
    print(f"  - With abstracts: {with_abstract} ({with_abstract/total*100:.1f}%)")
    print(f"  - PDF links: {with_pdf} ({with_pdf/total*100:.1f}%)")
    print(f"  - Slides links: {with_slides} ({with_slides/total*100:.1f}%)")
    print(f"  - Video links: {with_video} ({with_video/total*100:.1f}%)")
    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    main()
