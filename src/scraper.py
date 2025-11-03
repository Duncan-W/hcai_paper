"""
UCD Module Scraper
Scrapes Computer Science module data from UCD's public module directory
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import Dict, List, Optional
from tqdm import tqdm


class UCDModuleScraper:
    """Scraper for UCD module information"""

    BASE_URL = "https://hub.ucd.ie/usis/!W_HU_MENU.P_PUBLISH"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_comp_modules(self, test_mode: bool = True, modules_file: str = "modules.txt") -> List[str]:
        """
        Get list of COMP module codes.

        Priority:
        1. If modules_file exists, read module codes from it (one per line)
        2. Otherwise, generate module codes based on patterns

        Args:
            test_mode: If True, only try a small subset for testing (default: True)
            modules_file: Path to text file with module codes (default: "modules.txt")

        Returns:
            List of module codes to try
        """
        module_codes = []

        # First, check if modules.txt exists
        import os
        if os.path.exists(modules_file):
            print(f"✓ Found {modules_file} - loading module codes from file")
            try:
                with open(modules_file, 'r') as f:
                    for line in f:
                        code = line.strip()
                        # Skip empty lines and comments
                        if code and not code.startswith('#'):
                            module_codes.append(code)

                print(f"  Loaded {len(module_codes)} module codes from {modules_file}")
                return module_codes
            except Exception as e:
                print(f"  ⚠ Error reading {modules_file}: {e}")
                print(f"  Falling back to pattern-based generation...")
        else:
            print(f"  No {modules_file} found, using pattern-based generation")

        # Fallback: Generate module codes based on patterns
        # UCD COMP modules typically follow pattern: COMP + level (1-4) + number
        if test_mode:
            # TESTING MODE: Try only a small focused set
            # Most likely to exist: Level 1 and 2, series 0 and 1, multiples of 10
            print("  Running in TEST MODE - limited module search")
            for level in [1, 2]:
                for series in [0, 1]:
                    for num in range(0, 100, 10):  # 0, 10, 20, ..., 90
                        code = f"COMP{level}{series}{num:03d}"
                        module_codes.append(code)

            # Also try some level 3 and 4 samples
            for series in [0]:
                for num in [0, 10, 20, 30]:
                    module_codes.append(f"COMP3{series}{num:03d}")
                    module_codes.append(f"COMP4{series}{num:03d}")
        else:
            # FULL MODE: Try comprehensive search
            # Level 1: COMP10xxx, COMP11xxx
            # Level 2: COMP20xxx, COMP21xxx
            # Level 3: COMP30xxx, COMP31xxx
            # Level 4: COMP40xxx, COMP41xxx, COMP47xxx (masters)
            print("  Running in FULL MODE - comprehensive search")
            for level in [1, 2, 3, 4]:
                for series in [0, 1, 2, 3, 4, 7]:  # Common series numbers
                    for num in range(0, 200, 10):  # Try every 10
                        code = f"COMP{level}{series}{num:03d}"
                        module_codes.append(code)

        return module_codes

    def fetch_module_descriptor(self, module_code: str, term_code: str = "202500") -> Optional[Dict]:
        """
        Fetch detailed module descriptor for a given module code

        Args:
            module_code: Module code (e.g., "COMP10010")
            term_code: Academic term code (default: 202500 for 2025/2026)

        Returns:
            Dictionary with module information or None if module doesn't exist
        """
        url = f"{self.BASE_URL}?p_tag=MODULE&MODULE={module_code}&ARCHIVE=Y&TERMCODE={term_code}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Check if module exists (page will have specific error message if not)
            if "No data found" in response.text or len(response.text) < 1000:
                return None

            module_data = {
                'code': module_code,
                'url': url,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'learning_outcomes': self._extract_learning_outcomes(soup),
                'syllabus': self._extract_syllabus(soup),
                'assessment': self._extract_assessment(soup),
                'credits': self._extract_credits(soup),
                'level': self._extract_level(soup),
                'coordinator': self._extract_coordinator(soup),
            }

            # Only return if we got meaningful data
            if module_data['title']:
                return module_data

            return None

        except Exception as e:
            print(f"Error fetching {module_code}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract module title"""
        # Look for title in various possible locations
        title_elem = soup.find('h1')
        if title_elem:
            return title_elem.get_text(strip=True)

        # Try meta title
        title_meta = soup.find('title')
        if title_meta:
            text = title_meta.get_text()
            # Remove "UCD - " prefix if present
            return re.sub(r'^UCD\s*-\s*', '', text).strip()

        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract module description from meta tag"""
        # Try meta description first (cleanest source)
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()

        # Fallback: look in accordion sections
        accordion_content = self._find_accordion_content(soup, ['description', 'about'])
        if accordion_content:
            return accordion_content

        return ""

    def _find_accordion_content(self, soup: BeautifulSoup, keywords: List[str]) -> str:
        """
        Find content in accordion sections by keyword

        Args:
            soup: BeautifulSoup object
            keywords: List of keywords to search for in button text

        Returns:
            Content text or empty string
        """
        # Find all accordion buttons
        buttons = soup.find_all('button', class_='accordion-button')

        for button in buttons:
            button_text = button.get_text(strip=True).lower()

            # Check if any keyword matches
            if any(keyword in button_text for keyword in keywords):
                # Get the aria-controls attribute
                controls_id = button.get('aria-controls')
                if controls_id:
                    # Find the corresponding content div
                    content_div = soup.find('div', id=controls_id)
                    if content_div:
                        # Find the accordion-body within it
                        body = content_div.find('div', class_='accordion-body')
                        if body:
                            return body.get_text(strip=True)

        return ""

    def _extract_learning_outcomes(self, soup: BeautifulSoup) -> List[str]:
        """Extract learning outcomes from accordion section"""
        outcomes = []

        # Find "What will I learn?" accordion section
        buttons = soup.find_all('button', class_='accordion-button')

        for button in buttons:
            button_text = button.get_text(strip=True).lower()

            # Look for learning outcomes section
            if 'what will i learn' in button_text or 'learning outcome' in button_text:
                # Get the aria-controls attribute
                controls_id = button.get('aria-controls')
                if controls_id:
                    # Find the corresponding content div
                    content_div = soup.find('div', id=controls_id)
                    if content_div:
                        # Find the accordion-body within it
                        body = content_div.find('div', class_='accordion-body')
                        if body:
                            # Look for h6 with "Learning Outcomes:" followed by paragraph
                            h6 = body.find('h6', string=re.compile(r'Learning Outcomes', re.IGNORECASE))
                            if h6:
                                # Get the next sibling paragraph
                                p = h6.find_next_sibling('p')
                                if p:
                                    # Replace <BR> tags with newlines before extracting text
                                    html_content = str(p)
                                    # Replace BR tags with a marker
                                    html_content = re.sub(r'<BR\s*/?>', '\n', html_content, flags=re.IGNORECASE)
                                    html_content = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)

                                    # Parse the modified HTML
                                    from bs4 import BeautifulSoup as BS
                                    temp_soup = BS(html_content, 'html.parser')
                                    full_text = temp_soup.get_text()

                                    # Split by newlines
                                    lines = full_text.split('\n')

                                    for line in lines:
                                        line = line.strip()
                                        # Look for numbered outcomes (1. 2. 3. etc.)
                                        match = re.match(r'^(\d+)\.\s+(.+)$', line)
                                        if match:
                                            outcome = match.group(2).strip()
                                            if len(outcome) > 10:  # Filter out too-short outcomes
                                                outcomes.append(outcome)

                            # Also check for traditional list format
                            if not outcomes:
                                list_elem = body.find(['ol', 'ul'])
                                if list_elem:
                                    for li in list_elem.find_all('li'):
                                        outcome_text = li.get_text(strip=True)
                                        if outcome_text and len(outcome_text) > 10:
                                            outcomes.append(outcome_text)

        return outcomes

    def _extract_syllabus(self, soup: BeautifulSoup) -> str:
        """Extract syllabus/content from accordion section"""
        # Look in accordion sections
        content = self._find_accordion_content(
            soup,
            ['syllabus', 'content', 'what is covered', 'module content']
        )
        if content:
            return content

        # Fallback to old method
        for heading in soup.find_all(['h2', 'h3', 'strong']):
            if 'syllabus' in heading.get_text().lower() or 'content' in heading.get_text().lower():
                next_elem = heading.find_next(['p', 'div', 'ul'])
                if next_elem:
                    return next_elem.get_text(strip=True)
        return ""

    def _extract_assessment(self, soup: BeautifulSoup) -> str:
        """Extract assessment information from accordion section"""
        # Look in accordion sections
        content = self._find_accordion_content(
            soup,
            ['assessment', 'how will i be assessed', 'how am i assessed']
        )
        if content:
            return content

        # Fallback to old method
        for heading in soup.find_all(['h2', 'h3', 'strong']):
            if 'assessment' in heading.get_text().lower():
                next_elem = heading.find_next(['p', 'div', 'table'])
                if next_elem:
                    return next_elem.get_text(strip=True)
        return ""

    def _extract_credits(self, soup: BeautifulSoup) -> int:
        """Extract credit value"""
        text = soup.get_text()
        match = re.search(r'Credits:\s*(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def _extract_level(self, soup: BeautifulSoup) -> int:
        """Extract module level"""
        text = soup.get_text()
        match = re.search(r'Level:\s*(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def _extract_coordinator(self, soup: BeautifulSoup) -> str:
        """Extract module coordinator"""
        text = soup.get_text()
        match = re.search(r'(?:Module Coordinator|Coordinator):\s*([^\n]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def scrape_all_comp_modules(self, output_file: str = "data/comp_modules.json",
                                test_mode: bool = True, max_modules: int = 10) -> List[Dict]:
        """
        Scrape all COMP modules and save to JSON

        Args:
            output_file: Path to save JSON output
            test_mode: If True, search only a small subset of module codes (default: True)
            max_modules: Stop after finding this many modules (default: 10 for testing)

        Returns:
            List of module dictionaries
        """
        print("Generating list of potential COMP module codes...")
        module_codes = self.get_comp_modules(test_mode=test_mode)

        limit_text = f" (will stop after finding {max_modules})" if max_modules else ""
        print(f"Attempting to fetch {len(module_codes)} potential modules{limit_text}...")
        modules = []

        for code in tqdm(module_codes, desc="Fetching modules"):
            module_data = self.fetch_module_descriptor(code)
            if module_data:
                modules.append(module_data)
                print(f"\n✓ Found: {code} - {module_data['title']}")

                # Check if we've reached our limit
                if max_modules and len(modules) >= max_modules:
                    print(f"\n✓ Reached target of {max_modules} modules, stopping search...")
                    break

            # Be respectful to the server
            time.sleep(0.5)

        print(f"\nSuccessfully scraped {len(modules)} COMP modules")

        # Save to JSON
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(modules, f, indent=2, ensure_ascii=False)

        print(f"Saved to {output_file}")
        return modules


def main():
    """Main function to run scraper"""
    scraper = UCDModuleScraper()
    modules = scraper.scrape_all_comp_modules()

    print(f"\nSummary:")
    print(f"Total modules found: {len(modules)}")
    print(f"Modules with learning outcomes: {sum(1 for m in modules if m['learning_outcomes'])}")


if __name__ == "__main__":
    main()
