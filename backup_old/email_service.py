import imaplib
import email
import re
import logging
from typing import List, Optional
from datetime import datetime
from email.header import decode_header
from models import EmailData
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.imap = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to Gmail IMAP server"""
        try:
            self.imap = imaplib.IMAP4_SSL(settings.imap_server, settings.imap_port)
            self.imap.login(settings.gmail_email, settings.gmail_password)
            self.connected = True
            logger.info("Successfully connected to Gmail IMAP")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Gmail IMAP: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.imap and self.connected:
            try:
                self.imap.logout()
                self.connected = False
                logger.info("Disconnected from Gmail IMAP")
            except Exception as e:
                logger.error(f"Error disconnecting from IMAP: {e}")
    
    def _decode_email_header(self, header: str) -> str:
        """Decode email header properly"""
        try:
            decoded_parts = decode_header(header)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            return decoded_string
        except Exception as e:
            logger.error(f"Error decoding email header: {e}")
            return str(header)
    
    def _extract_job_url(self, email_body: str) -> Optional[str]:
        """Extract job URL from email body - flexible approach"""
        try:
            # More flexible patterns for job URLs
            url_patterns = [
                # Direct job posting URLs
                r'https?://[^\s<>"]+job[^\s<>"]*',
                r'https?://[^\s<>"]+career[^\s<>"]*',
                r'https?://[^\s<>"]+position[^\s<>"]*',
                r'https?://[^\s<>"]+apply[^\s<>"]*',
                r'https?://[^\s<>"]+opportunity[^\s<>"]*',
                r'https?://[^\s<>"]+opening[^\s<>"]*',
                r'https?://[^\s<>"]+role[^\s<>"]*',
                # Generic URLs that might contain job info
                r'https?://[^\s<>"]+remotelyx[^\s<>"]*',
                r'https?://[^\s<>"]+remote[^\s<>"]*',
                # Any URL that might be relevant
                r'https?://[^\s<>"]+',
            ]
            
            all_urls = []
            for pattern in url_patterns:
                matches = re.findall(pattern, email_body, re.IGNORECASE)
                all_urls.extend(matches)
            
            if all_urls:
                # Prioritize URLs that seem more job-related
                for url in all_urls:
                    url_lower = url.lower()
                    if any(keyword in url_lower for keyword in ['job', 'career', 'position', 'apply', 'opportunity']):
                        return url
                    elif 'remotelyx' in url_lower or 'remote' in url_lower:
                        return url
                
                # Return the first URL if no specific job-related URL found
                return all_urls[0]
            
            return None
        except Exception as e:
            logger.error(f"Error extracting job URL: {e}")
            return None
    
    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime object"""
        try:
            # Try multiple date formats
            date_formats = [
                '%a, %d %b %Y %H:%M:%S %z',
                '%d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S',
                '%d %b %Y %H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, return current time
            logger.warning(f"Could not parse email date: {date_str}")
            return datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error parsing email date: {e}")
            return datetime.utcnow()
    
    def fetch_remotelyx_emails(self, limit: int = 10) -> List[EmailData]:
        """Fetch emails from specific sender with RemotelyX subject"""
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            # Select inbox
            self.imap.select('INBOX')
            
            # Search for emails from specific sender with subject containing keyword
            search_criteria = f'(FROM "{settings.sender_email}" SUBJECT "{settings.subject_keyword}")'
            status, message_numbers = self.imap.search(None, search_criteria)
            
            if status != 'OK':
                logger.error("Failed to search emails")
                return []
            
            email_list = []
            message_number_list = message_numbers[0].split()
            
            # Process emails (limit to specified number)
            for num in message_number_list[-limit:]:
                try:
                    status, msg_data = self.imap.fetch(num, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract email details
                    subject = self._decode_email_header(email_message['subject'] or '')
                    sender = self._decode_email_header(email_message['from'] or '')
                    date_str = email_message['date'] or ''
                    date = self._parse_email_date(date_str)
                    
                    # Extract email body
                    body = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    
                    # Extract job URL from body
                    job_url = self._extract_job_url(body)
                    
                    email_data = EmailData(
                        subject=subject,
                        sender=sender,
                        date=date,
                        body=body,
                        job_url=job_url
                    )
                    
                    email_list.append(email_data)
                    logger.info(f"Processed email: {subject}")
                    
                except Exception as e:
                    logger.error(f"Error processing email {num}: {e}")
                    continue
            
            return email_list
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def mark_email_as_read(self, message_number: str) -> bool:
        """Mark email as read"""
        try:
            if not self.connected:
                return False
            
            self.imap.store(message_number, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False
    
    def get_unread_count(self) -> int:
        """Get count of unread emails"""
        try:
            if not self.connected:
                return 0
            
            self.imap.select('INBOX')
            status, message_numbers = self.imap.search(None, 'UNSEEN')
            
            if status == 'OK':
                return len(message_numbers[0].split())
            return 0
            
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0


# Global email service instance
email_service = EmailService() 