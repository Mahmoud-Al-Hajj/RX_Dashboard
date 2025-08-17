"""
Web scraping service for RemotelyX job postings.
Handles intelligent data extraction with fallback strategies and error handling.
"""

import re
import time
import random
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from loguru import logger

from ..core.config import get_settings
from ..models.job_posting import JobPostingCreate, SeniorityLevel, WorkMode, EmploymentType


class RemotelyXScraper:
    """Scraper for RemotelyX job postings with intelligent data extraction."""
    
    def __init__(self):
        self.settings = get_settings()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.settings.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Common job-related keywords for better extraction
        self.seniority_keywords = {
            SeniorityLevel.JUNIOR: ['junior', 'entry', 'entry-level', 'jr', 'graduate', 'new grad'],
            SeniorityLevel.MID: ['mid', 'middle', 'intermediate', 'mid-level', 'mid level'],
            SeniorityLevel.SENIOR: ['senior', 'sr', 'senior-level', 'senior level', 'experienced'],
            SeniorityLevel.LEAD: ['lead', 'team lead', 'technical lead', 'engineering lead'],
            SeniorityLevel.EXECUTIVE: ['executive', 'director', 'vp', 'cto', 'ceo', 'head of']
        }
        
        self.work_mode_keywords = {
            WorkMode.REMOTE: ['remote', 'work from home', 'wfh', 'fully remote', '100% remote'],
            WorkMode.HYBRID: ['hybrid', 'partially remote', 'flexible', 'remote-first'],
            WorkMode.ONSITE: ['onsite', 'on-site', 'in-office', 'office-based', 'local']
        }
        
        self.employment_type_keywords = {
            EmploymentType.FULL_TIME: ['full-time', 'full time', 'fulltime', 'permanent'],
            EmploymentType.PART_TIME: ['part-time', 'part time', 'parttime'],
            EmploymentType.CONTRACT: ['contract', 'contractor', 'freelance', 'consulting'],
            EmploymentType.INTERNSHIP: ['internship', 'intern', 'co-op', 'coop'],
            EmploymentType.FREELANCE: ['freelance', 'freelancer', 'gig', 'project-based']
        }
    
    def scrape_job_posting(self, url: str) -> Optional[JobPostingCreate]:
        """Scrape a single job posting from the given URL."""
        try:
            logger.info(f"Scraping job posting: {url}")
            
            # Fetch the page
            response = self._fetch_page(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract job data
            job_data = self._extract_job_data(soup, url)
            if not job_data:
                logger.warning(f"Failed to extract job data from: {url}")
                return None
            
            # Add random delay to be respectful
            time.sleep(random.uniform(1, 3))
            
            logger.success(f"Successfully scraped job: {job_data.title}")
            return job_data
            
        except Exception as e:
            logger.error(f"Error scraping job posting {url}: {e}")
            return None
    
    def _fetch_page(self, url: str) -> Optional[requests.Response]:
        """Fetch a web page with retry logic."""
        for attempt in range(self.settings.max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=self.settings.request_timeout,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.settings.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All attempts failed for {url}")
                    return None
        
        return None
    
    def _extract_job_data(self, soup: BeautifulSoup, url: str) -> Optional[JobPostingCreate]:
        """Extract job data from BeautifulSoup object with simplified fields."""
        try:
            # Extract basic information
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            
            if not all([title, description]):
                logger.warning("Missing required fields: title or description")
                return None
            
            # Extract additional information
            skills = self._extract_skills(soup)
            
            # Infer classifications
            seniority = self._infer_seniority(title, description)
            work_mode = self._infer_work_mode(title, description)
            
            # Extract salary
            salary_info = self._extract_salary(soup)
            salary_min, salary_max, _, _ = self._parse_salary(salary_info)
            
            return JobPostingCreate(
                title=title,
                job_url=url,
                description=description,
                skills=skills,
                seniority=seniority,
                work_mode=work_mode,
                salary_min=salary_min,
                salary_max=salary_max
            )
            
        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract job title using multiple strategies."""
        title_selectors = [
            'h1[class*="title"]',
            'h1[class*="job"]',
            'h1[class*="position"]',
            'h1[class*="role"]',
            'h1',
            '[data-testid*="title"]',
            '[data-testid*="job"]',
            '.job-title',
            '.position-title',
            '.role-title',
            'title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = self._clean_text(element.get_text())
                if title and len(title) < 200:
                    return title
        
        # Fallback: look for title in meta tags
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return self._clean_text(meta_title['content'])
        
        return "Job Title Not Found"
    
    def _extract_company(self, soup: BeautifulSoup) -> str:
        """Extract company name using multiple strategies."""
        company_selectors = [
            '[class*="company"]',
            '[class*="organization"]',
            '[data-testid*="company"]',
            '.company-name',
            '.organization-name',
            '.employer',
            'h2[class*="company"]',
            'h3[class*="company"]'
        ]
        
        for selector in company_selectors:
            element = soup.select_one(selector)
            if element:
                company = self._clean_text(element.get_text())
                if company and len(company) < 100:
                    return company
        
        # Fallback: extract from URL
        return self._extract_company_from_url(soup)
    
    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract job location using multiple strategies."""
        location_selectors = [
            '[class*="location"]',
            '[class*="place"]',
            '[data-testid*="location"]',
            '.location',
            '.place',
            '.job-location',
            '.work-location'
        ]
        
        for selector in location_selectors:
            element = soup.select_one(selector)
            if element:
                location = self._clean_text(element.get_text())
                if location and len(location) < 100:
                    return location
        
        return "Location Not Specified"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract job description using multiple strategies."""
        description_selectors = [
            '[class*="description"]',
            '[class*="content"]',
            '[class*="body"]',
            '[data-testid*="description"]',
            '.job-description',
            '.position-description',
            '.role-description',
            'article',
            'main'
        ]
        
        for selector in description_selectors:
            element = soup.select_one(selector)
            if element:
                description = self._clean_text(element.get_text())
                if description and len(description) > 50:
                    return description[:5000]  # Limit length
        
        return "Description Not Available"
    
    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract skills from job posting."""
        skills = []
        
        # Look for skills sections
        skills_selectors = [
            '[class*="skill"]',
            '[class*="technology"]',
            '[class*="tech"]',
            '[class*="requirement"]',
            '.skills',
            '.technologies',
            '.requirements'
        ]
        
        for selector in skills_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text()
                skills.extend(self._extract_skills_from_text(text))
        
        # Extract from description
        description = self._extract_description(soup)
        skills.extend(self._extract_skills_from_text(description))
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text using keyword matching."""
        # Common programming languages and technologies
        skill_keywords = [
            'python', 'javascript', 'js', 'java', 'c#', 'c++', 'php', 'ruby', 'go', 'rust',
            'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'nosql', 'mongodb', 'postgresql',
            'mysql', 'redis', 'elasticsearch', 'react', 'angular', 'vue', 'node.js', 'express',
            'django', 'flask', 'spring', 'laravel', 'rails', 'docker', 'kubernetes', 'aws',
            'azure', 'gcp', 'terraform', 'ansible', 'jenkins', 'git', 'github', 'gitlab',
            'html', 'css', 'sass', 'less', 'typescript', 'webpack', 'babel', 'jest', 'mocha',
            'pytest', 'junit', 'selenium', 'cypress', 'figma', 'sketch', 'adobe', 'photoshop',
            'illustrator', 'tableau', 'powerbi', 'excel', 'spreadsheet', 'word', 'powerpoint'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.append(skill.title())
        
        return found_skills
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract tags from job posting."""
        tags = []
        
        # Look for tag elements
        tag_selectors = [
            '[class*="tag"]',
            '[class*="label"]',
            '[class*="category"]',
            '.tag',
            '.label',
            '.category'
        ]
        
        for selector in tag_selectors:
            elements = soup.select(selector)
            for element in elements:
                tag = self._clean_text(element.get_text())
                if tag and len(tag) < 50:
                    tags.append(tag)
        
        return list(set(tags))
    
    def _extract_salary(self, soup: BeautifulSoup) -> str:
        """Extract salary information."""
        salary_selectors = [
            '[class*="salary"]',
            '[class*="compensation"]',
            '[class*="pay"]',
            '.salary',
            '.compensation',
            '.pay'
        ]
        
        for selector in salary_selectors:
            element = soup.select_one(selector)
            if element:
                salary = self._clean_text(element.get_text())
                if salary and len(salary) < 200:
                    return salary
        
        return ""
    
    def _extract_posting_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract job posting date."""
        date_selectors = [
            '[class*="date"]',
            '[class*="posted"]',
            '[class*="published"]',
            '.date',
            '.posted-date',
            '.published-date'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_text = self._clean_text(element.get_text())
                if date_text:
                    try:
                        # Try to parse common date formats
                        date_formats = [
                            '%Y-%m-%d',
                            '%m/%d/%Y',
                            '%d/%m/%Y',
                            '%B %d, %Y',
                            '%b %d, %Y'
                        ]
                        
                        for fmt in date_formats:
                            try:
                                return datetime.strptime(date_text, fmt)
                            except ValueError:
                                continue
                    except Exception:
                        pass
        
        return None
    
    def _extract_job_id(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract job ID from page or URL."""
        # Try to find job ID in meta tags
        meta_job_id = soup.find('meta', {'name': 'job-id'})
        if meta_job_id and meta_job_id.get('content'):
            return meta_job_id['content']
        
        # Try to extract from URL
        url_parts = url.split('/')
        for part in url_parts:
            if re.match(r'^\d+$', part):
                return part
        
        return None
    
    def _extract_company_from_url(self, soup: BeautifulSoup) -> str:
        """Extract company name from URL as fallback."""
        # This would need to be implemented based on RemotelyX URL structure
        return "Company Not Found"
    
    def _infer_seniority(self, title: str, description: str) -> Optional[SeniorityLevel]:
        """Infer seniority level from title and description."""
        text = f"{title} {description}".lower()
        
        for level, keywords in self.seniority_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return level
        
        return None
    
    def _infer_work_mode(self, title: str, description: str) -> Optional[WorkMode]:
        """Infer work mode from title and description."""
        text = f"{title} {description}".lower()
        
        for mode, keywords in self.work_mode_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return mode
        
        return None
    
    def _infer_employment_type(self, title: str, description: str) -> Optional[EmploymentType]:
        """Infer employment type from title and description."""
        text = f"{title} {description}".lower()
        
        for emp_type, keywords in self.employment_type_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return emp_type
        
        return None
    
    def _parse_salary(self, salary_text: str) -> tuple[Optional[float], Optional[float], str, str]:
        """Parse salary information from text."""
        if not salary_text:
            return None, None, "USD", "year"
        
        # Common salary patterns
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*to\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, salary_text)
            if match:
                try:
                    if len(match.groups()) == 2:
                        min_salary = float(match.group(1).replace(',', ''))
                        max_salary = float(match.group(2).replace(',', ''))
                        return min_salary, max_salary, "USD", "year"
                    else:
                        salary = float(match.group(1).replace(',', ''))
                        return salary, salary, "USD", "year"
                except ValueError:
                    continue
        
        return None, None, "USD", "year"
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        return text


# Global scraper instance
scraper = RemotelyXScraper()