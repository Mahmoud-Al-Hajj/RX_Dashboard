import requests
from bs4 import BeautifulSoup
import logging
import re
import time
from typing import Optional
from models import ScrapedJobData
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class JobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.max_retries = 3
        self.retry_delay = 2
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"All request attempts failed for {url}")
                    return None
        return None
    
    def _extract_text_safely(self, element) -> str:
        """Safely extract text from BeautifulSoup element"""
        try:
            return element.get_text(strip=True) if element else ""
        except Exception:
            return ""
    
    def _extract_skills_from_text(self, text: str) -> list:
        """Extract skills from text using common patterns - flexible approach"""
        skills = []
        
        # Common skill keywords (expanded and more flexible)
        skill_keywords = [
            # Programming Languages
            'python', 'javascript', 'js', 'java', 'c#', 'c++', 'c\\+\\+', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab',
            # Web Technologies
            'react', 'reactjs', 'angular', 'vue', 'vuejs', 'node\\.js', 'nodejs', 'express', 'django', 'flask', 'laravel', 'rails', 'spring',
            'html', 'css', 'typescript', 'ts', 'jquery', 'bootstrap', 'tailwind', 'sass', 'less', 'webpack', 'babel',
            # Databases
            'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'oracle', 'sqlite',
            # Cloud & DevOps
            'aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins',
            'git', 'github', 'gitlab', 'bitbucket', 'ci/cd', 'cicd', 'devops', 'microservices', 'api', 'rest', 'graphql', 'soap',
            # Data & AI
            'machine learning', 'ml', 'ai', 'artificial intelligence', 'data science', 'data analysis', 'pandas', 'numpy', 'tensorflow', 'pytorch',
            'scikit-learn', 'scikit', 'jupyter', 'spark', 'hadoop', 'kafka', 'airflow',
            # Other Technologies
            'linux', 'unix', 'windows', 'macos', 'ios', 'android', 'flutter', 'react native', 'xamarin', 'cordova',
            'wordpress', 'drupal', 'joomla', 'shopify', 'magento', 'woocommerce',
            'agile', 'scrum', 'kanban', 'jira', 'confluence', 'slack', 'teams'
        ]
        
        text_lower = text.lower()
        for skill in skill_keywords:
            # Use regex for more flexible matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                # Clean up the skill name
                clean_skill = skill.replace('\\', '').replace('.', '').title()
                skills.append(clean_skill)
        
        # Also look for common skill patterns in the text
        skill_patterns = [
            r'Skills?:\s*([^.\n]+)',
            r'Requirements?:\s*([^.\n]+)',
            r'Technologies?:\s*([^.\n]+)',
            r'Experience with:\s*([^.\n]+)',
            r'Proficient in:\s*([^.\n]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract individual skills from the matched text
                potential_skills = re.split(r'[,;|]', match)
                for potential_skill in potential_skills:
                    skill_clean = potential_skill.strip()
                    if len(skill_clean) > 2 and len(skill_clean) < 50:
                        skills.append(skill_clean.title())
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_salary(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract salary information from page - generic approach"""
        # Try common salary patterns
        salary_patterns = [
            # Look for elements with salary-related classes
            soup.find(class_=re.compile(r'salary|compensation|pay|rate', re.I)),
            # Look for elements with salary-related IDs
            soup.find(id=re.compile(r'salary|compensation|pay|rate', re.I)),
            # Look for elements with salary-related data attributes
            soup.find(attrs={'data-salary': True}),
            soup.find(attrs={'data-compensation': True}),
            # Look for elements with salary-related content
            soup.find(string=re.compile(r'\$|salary|compensation|pay', re.I))
        ]
        
        for element in salary_patterns:
            if element:
                text = self._extract_text_safely(element)
                if text and any(keyword in text.lower() for keyword in ['$', 'salary', 'compensation', 'pay', 'rate']):
                    return text.strip()
        
        # Fallback: look for salary patterns in text
        page_text = soup.get_text()
        salary_regex_patterns = [
            r'\$\d{1,3}(?:,\d{3})*(?:-\$\d{1,3}(?:,\d{3})*)?',  # $50,000-$80,000
            r'\$\d{1,3}(?:,\d{3})*\s*(?:per\s+year|annually|yearly)',  # $50,000 per year
            r'\$\d{1,3}(?:,\d{3})*\s*(?:per\s+hour|hourly)',  # $25 per hour
            r'Salary:\s*([^\n\r]+)',
            r'Compensation:\s*([^\n\r]+)',
            r'Pay:\s*([^\n\r]+)'
        ]
        
        for pattern in salary_regex_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return None
    
    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract location information from page - generic approach"""
        # Try common location patterns
        location_patterns = [
            # Look for elements with location-related classes
            soup.find(class_=re.compile(r'location|place|address|remote', re.I)),
            # Look for elements with location-related IDs
            soup.find(id=re.compile(r'location|place|address|remote', re.I)),
            # Look for elements with location-related data attributes
            soup.find(attrs={'data-location': True}),
            soup.find(attrs={'data-place': True}),
            # Look for elements with location-related content
            soup.find(string=re.compile(r'location|place|address|remote', re.I))
        ]
        
        for element in location_patterns:
            if element:
                text = self._extract_text_safely(element)
                if text and len(text.strip()) > 0 and len(text) < 100:
                    return text.strip()
        
        # Fallback: look for location patterns in text
        page_text = soup.get_text()
        location_regex_patterns = [
            r'Location:\s*([^\n\r]+)',
            r'Based in\s*([^\n\r]+)',
            r'Remote\s*([^\n\r]*)',
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State pattern
            r'Remote\s*(?:work|job|position)?',
            r'Work from home',
            r'WFH'
        ]
        
        for pattern in location_regex_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return "Location Not Specified"
    
    def _extract_company(self, soup: BeautifulSoup, url: str) -> str:
        """Extract company name from page - generic approach"""
        # Try common company patterns
        company_patterns = [
            # Look for elements with company-related classes
            soup.find(class_=re.compile(r'company|organization|employer|brand', re.I)),
            # Look for elements with company-related IDs
            soup.find(id=re.compile(r'company|organization|employer|brand', re.I)),
            # Look for elements with company-related data attributes
            soup.find(attrs={'data-company': True}),
            soup.find(attrs={'data-organization': True}),
            # Look for elements with company-related content
            soup.find(string=re.compile(r'company|organization|employer', re.I))
        ]
        
        for element in company_patterns:
            if element:
                text = self._extract_text_safely(element)
                if text and len(text.strip()) > 0 and len(text) < 100:
                    return text.strip()
        
        # Fallback: extract from URL domain
        try:
            domain = urlparse(url).netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain.split('.')[0].title()
        except Exception:
            return "Company Not Found"
    
    def _extract_job_title(self, soup: BeautifulSoup) -> str:
        """Extract job title from page - generic approach"""
        # Try common title patterns
        title_patterns = [
            # Look for h1 tags first
            soup.find('h1'),
            # Look for elements with title-related classes
            soup.find(class_=re.compile(r'title|position|job-title|role', re.I)),
            # Look for elements with title-related IDs
            soup.find(id=re.compile(r'title|position|job-title|role', re.I)),
            # Look for elements with title-related data attributes
            soup.find(attrs={'data-title': True}),
            soup.find(attrs={'data-position': True}),
            # Look for elements with title-related content
            soup.find(string=re.compile(r'job|position|role|title', re.I))
        ]
        
        for element in title_patterns:
            if element:
                text = self._extract_text_safely(element)
                if text and len(text.strip()) > 0 and len(text) < 200:
                    return text.strip()
        
        # Fallback: try to find any meaningful heading
        for tag in ['h1', 'h2', 'h3']:
            headings = soup.find_all(tag)
            for heading in headings:
                text = self._extract_text_safely(heading)
                if text and len(text.strip()) > 0 and len(text) < 200:
                    return text.strip()
        
        return "Job Title Not Found"
    
    def scrape_job_page(self, url: str) -> Optional[ScrapedJobData]:
        """Scrape job details from a job posting URL"""
        try:
            logger.info(f"Scraping job page: {url}")
            
            response = self._make_request(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract job details
            job_title = self._extract_job_title(soup)
            company = self._extract_company(soup, url)
            location = self._extract_location(soup)
            salary = self._extract_salary(soup)
            
            # Extract skills from page content
            page_text = soup.get_text()
            skills = self._extract_skills_from_text(page_text)
            
            job_data = ScrapedJobData(
                job_title=job_title,
                company=company,
                location=location,
                skills=skills,
                salary=salary
            )
            
            logger.info(f"Successfully scraped job: {job_title} at {company}")
            return job_data
            
        except Exception as e:
            logger.error(f"Error scraping job page {url}: {e}")
            return None
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()


# Global scraper instance
job_scraper = JobScraper() 