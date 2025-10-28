#!/usr/bin/env python3
"""
Software Supply Chain Paper Filter
Filter NDSS papers related to software supply chain security from crawled data.

This script searches for papers mentioning software supply chain related keywords
in titles and abstracts, then saves the filtered results.
"""

import json
import re
from typing import List, Dict, Set


class SupplyChainFilter:
    def __init__(self):
        # Keywords related to software supply chain
        self.keywords = {
            # Core terms
            'software supply chain',
            'supply chain',
            'supply-chain',
            
            # Package/dependency related
            'package',
            'packages',
            'dependency',
            'dependencies',
            'library',
            'libraries',
            'npm',
            'pypi',
            'maven',
            'gradle',
            
            # Build/deployment
            'build',
            'ci/cd',
            'cicd',
            'continuous integration',
            'continuous deployment',
            'pipeline',
            'artifact',
            'artifacts',
            
            # Version control
            'repository',
            'repositories',
            'github',
            'gitlab',
            'bitbucket',
            'git',
            
            # Container/registry
            'docker',
            'container',
            'registry',
            
            # Code security
            'open source',
            'open-source',
            'third-party',
            'third party',
            'code reuse',
            'software composition',
            'component',
            'components',
            
            # Specific attacks
            'typosquatting',
            'dependency confusion',
            'malicious package',
            'backdoor',
            'supply chain attack',
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for matching: lowercase and clean whitespace"""
        if not text:
            return ""
        return ' '.join(text.lower().split())
    
    def contains_keywords(self, text: str) -> Set[str]:
        """Check if text contains any supply chain related keywords"""
        normalized = self.normalize_text(text)
        found_keywords = set()
        
        for keyword in self.keywords:
            # Use word boundary for better matching
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, normalized):
                found_keywords.add(keyword)
        
        return found_keywords
    
    def is_relevant(self, paper: Dict) -> tuple[bool, Set[str]]:
        """
        Check if a paper is relevant to software supply chain.
        Returns: (is_relevant, matched_keywords)
        """
        # Check title
        title_keywords = self.contains_keywords(paper.get('title', ''))
        
        # Check abstract
        abstract_keywords = self.contains_keywords(paper.get('abstract', ''))
        
        # Combine all matched keywords
        all_keywords = title_keywords | abstract_keywords
        
        return len(all_keywords) > 0, all_keywords
    
    def filter_papers(self, papers_data: Dict[int, List[Dict]]) -> Dict:
        """
        Filter papers from all years.
        Returns: {
            'filtered_papers': {...},
            'statistics': {...}
        }
        """
        filtered = {}
        stats = {
            'total_papers': 0,
            'filtered_papers': 0,
            'by_year': {},
            'keyword_frequency': {}
        }
        
        for year, papers in papers_data.items():
            stats['total_papers'] += len(papers)
            filtered[year] = []
            year_stats = {
                'total': len(papers),
                'filtered': 0,
                'keywords': {}
            }
            
            for paper in papers:
                is_relevant, keywords = self.is_relevant(paper)
                
                if is_relevant:
                    # Add matched keywords to paper metadata
                    paper_copy = paper.copy()
                    paper_copy['matched_keywords'] = sorted(list(keywords))
                    filtered[year].append(paper_copy)
                    
                    year_stats['filtered'] += 1
                    stats['filtered_papers'] += 1
                    
                    # Count keyword frequency
                    for kw in keywords:
                        stats['keyword_frequency'][kw] = stats['keyword_frequency'].get(kw, 0) + 1
                        year_stats['keywords'][kw] = year_stats['keywords'].get(kw, 0) + 1
            
            stats['by_year'][year] = year_stats
        
        return {
            'filtered_papers': filtered,
            'statistics': stats
        }
    
    def save_results(self, result: Dict, base_filename: str = 'supply_chain_papers'):
        """Save filtered results to multiple formats"""
        filtered_papers = result['filtered_papers']
        stats = result['statistics']
        
        # 1. Save JSON
        json_filename = f'{base_filename}.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"  [SAVED] JSON: {json_filename}")
        
        # 2. Save Markdown
        md_filename = f'{base_filename}.md'
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write("# Software Supply Chain Related Papers from NDSS (2023-2025)\n\n")
            
            # Statistics
            f.write("## Statistics\n\n")
            f.write(f"- **Total papers reviewed**: {stats['total_papers']}\n")
            f.write(f"- **Supply chain related papers**: {stats['filtered_papers']}\n")
            f.write(f"- **Percentage**: {stats['filtered_papers']/stats['total_papers']*100:.1f}%\n\n")
            
            # Year breakdown
            f.write("### By Year\n\n")
            for year in sorted(filtered_papers.keys(), reverse=True):
                year_stat = stats['by_year'][year]
                f.write(f"- **NDSS {year}**: {year_stat['filtered']}/{year_stat['total']} papers "
                       f"({year_stat['filtered']/year_stat['total']*100:.1f}%)\n")
            
            # Top keywords
            f.write("\n### Top Matched Keywords\n\n")
            sorted_keywords = sorted(stats['keyword_frequency'].items(), 
                                   key=lambda x: x[1], reverse=True)
            for kw, count in sorted_keywords[:20]:
                f.write(f"- **{kw}**: {count} papers\n")
            
            # Papers by year
            f.write("\n---\n\n")
            for year in sorted(filtered_papers.keys(), reverse=True):
                papers = filtered_papers[year]
                if not papers:
                    continue
                    
                f.write(f"## NDSS {year} ({len(papers)} papers)\n\n")
                
                for i, p in enumerate(papers, 1):
                    f.write(f"### {i}. {p['title']}\n\n")
                    
                    # Matched keywords
                    f.write(f"**Matched Keywords**: {', '.join(p['matched_keywords'])}\n\n")
                    
                    # Authors
                    if p.get('authors'):
                        authors = p['authors'][:3]
                        author_str = ', '.join(authors)
                        if len(p['authors']) > 3:
                            author_str += f" et al. ({len(p['authors'])} total)"
                        f.write(f"**Authors**: {author_str}\n\n")
                    
                    # Affiliations
                    if p.get('affiliations'):
                        f.write(f"**Affiliations**: {'; '.join(p['affiliations'][:3])}\n\n")
                    
                    # Abstract
                    if p.get('abstract'):
                        abstract = p['abstract'][:500] + '...' if len(p['abstract']) > 500 else p['abstract']
                        f.write(f"**Abstract**: {abstract}\n\n")
                    
                    # Resource links
                    links = []
                    if p.get('detail_url'):
                        links.append(f"[Details]({p['detail_url']})")
                    if p.get('pdf_url'):
                        links.append(f"[PDF]({p['pdf_url']})")
                    if p.get('slides_url'):
                        links.append(f"[Slides]({p['slides_url']})")
                    if p.get('video_url'):
                        links.append(f"[Video]({p['video_url']})")
                    if p.get('code_url'):
                        links.append(f"[Code]({p['code_url']})")
                    
                    if links:
                        f.write(f"**Resources**: {' | '.join(links)}\n\n")
                    
                    f.write("---\n\n")
        
        print(f"  [SAVED] Markdown: {md_filename}")
        
        # 3. Save CSV
        csv_filename = f'{base_filename}.csv'
        import csv
        with open(csv_filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Year', 'Title', 'Matched_Keywords', 'Authors', 'Affiliations', 
                'Abstract', 'PDF_URL', 'Slides_URL', 'Video_URL', 'Detail_URL'
            ])
            writer.writeheader()
            
            for year in sorted(filtered_papers.keys(), reverse=True):
                for p in filtered_papers[year]:
                    writer.writerow({
                        'Year': p['year'],
                        'Title': p['title'],
                        'Matched_Keywords': ', '.join(p['matched_keywords']),
                        'Authors': '; '.join(p.get('authors', [])),
                        'Affiliations': '; '.join(p.get('affiliations', [])),
                        'Abstract': p.get('abstract', ''),
                        'PDF_URL': p.get('pdf_url', ''),
                        'Slides_URL': p.get('slides_url', ''),
                        'Video_URL': p.get('video_url', ''),
                        'Detail_URL': p.get('detail_url', '')
                    })
        
        print(f"  [SAVED] CSV: {csv_filename}")


def main():
    print("\n" + "="*80)
    print("  Software Supply Chain Paper Filter")
    print("="*80 + "\n")
    
    # Load data
    print("  [INFO] Loading paper data...")
    
    # Try different possible filenames
    input_files = [
        'ndss_papers_all.json',
        'ndss_papers.json',
    ]
    
    data = None
    for filename in input_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  [SUCCESS] Loaded data from: {filename}\n")
            break
        except FileNotFoundError:
            continue
    
    if not data:
        print(f"  [ERROR] No input file found. Please run the crawler first.")
        print(f"  [ERROR] Expected files: {', '.join(input_files)}")
        return
    
    # Filter papers
    print("  [INFO] Filtering supply chain related papers...\n")
    filter_engine = SupplyChainFilter()
    result = filter_engine.filter_papers(data)
    
    # Display statistics
    stats = result['statistics']
    print("\n" + "="*80)
    print("  Filtering Results")
    print("="*80)
    print(f"\n  Total papers reviewed: {stats['total_papers']}")
    print(f"  Supply chain related: {stats['filtered_papers']} "
          f"({stats['filtered_papers']/stats['total_papers']*100:.1f}%)\n")
    
    print("  By Year:")
    for year in sorted(result['filtered_papers'].keys(), reverse=True):
        year_stat = stats['by_year'][year]
        print(f"    - NDSS {year}: {year_stat['filtered']}/{year_stat['total']} papers "
              f"({year_stat['filtered']/year_stat['total']*100:.1f}%)")
    
    # Top keywords
    print("\n  Top Matched Keywords:")
    sorted_keywords = sorted(stats['keyword_frequency'].items(), 
                           key=lambda x: x[1], reverse=True)[:10]
    for kw, count in sorted_keywords:
        print(f"    - {kw}: {count} papers")
    
    # Save results
    print("\n" + "="*80)
    print("  Saving Filtered Results")
    print("="*80 + "\n")
    
    filter_engine.save_results(result, 'supply_chain_papers')
    
    print("\n" + "="*80)
    print("  Filtering Completed")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
