import pandas as pd
import logging
import os
from typing import List
from datetime import datetime
from models import JobPosting
from config import settings

logger = logging.getLogger(__name__)


class ExcelExporter:
    def __init__(self, file_path: str = None):
        self.file_path = file_path or settings.excel_file_path
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Ensure Excel file exists with proper headers"""
        try:
            if not os.path.exists(self.file_path):
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                
                # Create empty DataFrame with headers
                headers = [
                    'Job Title',
                    'Company',
                    'Location',
                    'Skills',
                    'Salary',
                    'Job URL',
                    'Email Subject',
                    'Email Date',
                    'Scraped At',
                    'Processed'
                ]
                
                df = pd.DataFrame(columns=headers)
                df.to_excel(self.file_path, index=False, engine='openpyxl')
                logger.info(f"Created new Excel file: {self.file_path}")
            
        except Exception as e:
            logger.error(f"Error ensuring Excel file exists: {e}")
            raise
    
    def _format_skills(self, skills: List[str]) -> str:
        """Format skills list as comma-separated string"""
        if not skills:
            return ""
        return ", ".join(skills)
    
    def _format_date(self, date: datetime) -> str:
        """Format datetime for Excel"""
        try:
            return date.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(date)
    
    def append_jobs(self, jobs: List[JobPosting]) -> bool:
        """Append job postings to Excel file"""
        try:
            if not jobs:
                logger.info("No jobs to append to Excel")
                return True
            
            # Read existing data
            try:
                existing_df = pd.read_excel(self.file_path, engine='openpyxl')
            except FileNotFoundError:
                # If file doesn't exist, create it
                self.ensure_file_exists()
                existing_df = pd.DataFrame()
            except Exception as e:
                logger.error(f"Error reading existing Excel file: {e}")
                return False
            
            # Prepare new data
            new_data = []
            for job in jobs:
                new_row = {
                    'Job Title': job.job_title,
                    'Company': job.company,
                    'Location': job.location,
                    'Skills': self._format_skills(job.skills),
                    'Salary': job.salary or "",
                    'Job URL': job.job_url,
                    'Email Subject': job.email_subject,
                    'Email Date': self._format_date(job.email_date),
                    'Scraped At': self._format_date(job.scraped_at),
                    'Processed': job.processed
                }
                new_data.append(new_row)
            
            # Create DataFrame for new data
            new_df = pd.DataFrame(new_data)
            
            # Combine existing and new data
            if existing_df.empty:
                combined_df = new_df
            else:
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Remove duplicates based on Job URL
            combined_df = combined_df.drop_duplicates(subset=['Job URL'], keep='first')
            
            # Save to Excel with formatting
            with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='w') as writer:
                combined_df.to_excel(writer, index=False, sheet_name='Job Postings')
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Job Postings']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"Successfully appended {len(jobs)} jobs to Excel file")
            return True
            
        except Exception as e:
            logger.error(f"Error appending jobs to Excel: {e}")
            return False
    
    def get_existing_urls(self) -> List[str]:
        """Get list of existing job URLs from Excel file"""
        try:
            if not os.path.exists(self.file_path):
                return []
            
            df = pd.read_excel(self.file_path, engine='openpyxl')
            return df['Job URL'].dropna().tolist()
            
        except Exception as e:
            logger.error(f"Error reading existing URLs from Excel: {e}")
            return []
    
    def backup_file(self) -> bool:
        """Create a backup of the Excel file"""
        try:
            if not os.path.exists(self.file_path):
                return True
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.file_path.replace('.xlsx', f'_backup_{timestamp}.xlsx')
            
            import shutil
            shutil.copy2(self.file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """Get statistics about the Excel file"""
        try:
            if not os.path.exists(self.file_path):
                return {
                    'total_jobs': 0,
                    'companies': [],
                    'locations': [],
                    'last_updated': None
                }
            
            df = pd.read_excel(self.file_path, engine='openpyxl')
            
            stats = {
                'total_jobs': len(df),
                'companies': df['Company'].dropna().unique().tolist(),
                'locations': df['Location'].dropna().unique().tolist(),
                'last_updated': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting Excel statistics: {e}")
            return {
                'total_jobs': 0,
                'companies': [],
                'locations': [],
                'last_updated': None,
                'error': str(e)
            }


# Global Excel exporter instance
excel_exporter = ExcelExporter() 