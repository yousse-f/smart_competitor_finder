import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging
from io import BytesIO
import re

logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Utility class for processing Excel files with competitor URLs."""
    
    def __init__(self):
        self.required_columns = ['URL']  # Can be extended to include 'Nome azienda', 'Codice ATECO'
        
        # Patterns per riconoscere colonne URL
        self.url_patterns = [
            r'url',
            r'sito',
            r'website',
            r'link',
            r'www\.',
            r'http',
            r'\.com',
            r'\.it',
            r'\.net',
            r'\.org'
        ]
        
        # Patterns per riconoscere colonne con nomi azienda
        self.company_patterns = [
            r'azienda',
            r'company',
            r'nome',
            r'ragione\s+sociale',
            r's\.p\.a\.',
            r's\.r\.l\.',
            r'società'
        ]
        
    def process_excel_file(self, file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """
        Process uploaded Excel file and extract URLs.
        Automatically detects URL and company name columns even with custom headers.
        
        Args:
            file_content: Raw bytes of the Excel file
            filename: Original filename for logging
            
        Returns:
            List of dictionaries containing site data
            
        Raises:
            ValueError: If file format is invalid or required columns are missing
        """
        try:
            # Try different Excel engines (xlsx, xls)
            df = None
            for engine in ['openpyxl', 'xlrd']:
                try:
                    df = pd.read_excel(BytesIO(file_content), engine=engine)
                    break
                except:
                    continue
            
            if df is None:
                raise ValueError("Unable to read Excel file. Supported formats: .xlsx, .xls")
            
            logger.info(f"Processing Excel file: {filename} with {len(df)} rows and columns: {list(df.columns)}")
            
            # Auto-detect column mappings
            url_col, company_col = self._auto_detect_columns(df)
            
            logger.info(f"Detected URL column: '{url_col}', Company column: '{company_col}'")
            
            # Clean and process data
            sites_data = self._extract_sites_data_auto(df, url_col, company_col)
            
            logger.info(f"Successfully extracted {len(sites_data)} valid URLs from {filename}")
            
            return sites_data
            
        except Exception as e:
            logger.error(f"Error processing Excel file {filename}: {str(e)}")
            raise ValueError(f"Failed to process Excel file: {str(e)}")
    
    def _auto_detect_columns(self, df: pd.DataFrame) -> Tuple[str, Optional[str]]:
        """
        Automatically detect which columns contain URLs and company names.
        
        Returns:
            Tuple of (url_column_name, company_column_name or None)
        """
        url_col = None
        company_col = None
        
        # First, try to find URL column by header name
        for col in df.columns:
            col_lower = str(col).lower()
            
            # Check if header matches URL patterns
            if any(re.search(pattern, col_lower) for pattern in self.url_patterns):
                url_col = col
                break
        
        # If not found by header, detect by content (check if values look like URLs)
        if url_col is None:
            for col in df.columns:
                # Check first 5 non-null values
                sample_values = df[col].dropna().head(10).astype(str)
                url_like_count = sum(
                    1 for val in sample_values 
                    if any(pattern in val.lower() for pattern in ['.com', '.it', '.net', '.org', 'www.', 'http'])
                )
                
                # If more than 60% look like URLs, it's probably the URL column
                if len(sample_values) > 0 and url_like_count / len(sample_values) > 0.6:
                    url_col = col
                    break
        
        if url_col is None:
            # Last resort: use first column
            url_col = df.columns[0]
            logger.warning(f"Could not auto-detect URL column, using first column: '{url_col}'")
        
        # Detect company name column (should be different from URL column)
        for col in df.columns:
            if col == url_col:
                continue
                
            col_lower = str(col).lower()
            
            # Check if header matches company patterns
            if any(re.search(pattern, col_lower) for pattern in self.company_patterns):
                company_col = col
                break
        
        # If not found by header, use the other column if there are only 2 columns
        if company_col is None and len(df.columns) == 2:
            company_col = df.columns[1] if url_col == df.columns[0] else df.columns[0]
            logger.info(f"Using second column as company name: '{company_col}'")
        
        return url_col, company_col
    
    def _extract_sites_data_auto(self, df: pd.DataFrame, url_col: str, company_col: Optional[str]) -> List[Dict[str, Any]]:
        """Extract and clean site data from DataFrame using auto-detected columns."""
        sites_data = []
        
        for index, row in df.iterrows():
            try:
                url = str(row[url_col]).strip()
                
                # Skip empty URLs
                if pd.isna(row[url_col]) or not url or url.lower() in ['nan', 'none', '']:
                    continue
                
                # Clean URL: remove spaces, extra characters
                url = url.strip().replace(' ', '')
                
                # Ensure URL has protocol
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                site_data = {
                    'url': url,
                    'row_index': index + 1,  # 1-based for user reference
                }
                
                # Add company name if column was detected
                if company_col and pd.notna(row.get(company_col)):
                    site_data['company_name'] = str(row[company_col]).strip()
                
                # Add optional columns if they exist
                if 'Codice ATECO' in df.columns and pd.notna(row.get('Codice ATECO')):
                    site_data['ateco_code'] = str(row['Codice ATECO']).strip()
                
                sites_data.append(site_data)
                
            except Exception as e:
                logger.warning(f"Skipping row {index + 1} due to error: {str(e)}")
                continue
        
        return sites_data
    
    def _validate_columns(self, df: pd.DataFrame, filename: str) -> None:
        """Validate that required columns exist in the DataFrame."""
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        
        if missing_columns:
            available_cols = list(df.columns)
            raise ValueError(
                f"Missing required columns in {filename}: {missing_columns}. "
                f"Available columns: {available_cols}"
            )
    
    def _extract_sites_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract and clean site data from DataFrame."""
        sites_data = []
        
        for index, row in df.iterrows():
            try:
                url = str(row['URL']).strip()
                
                # Skip empty URLs
                if pd.isna(row['URL']) or not url or url.lower() in ['nan', 'none', '']:
                    continue
                
                # Ensure URL has protocol
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                site_data = {
                    'url': url,
                    'row_index': index + 1,  # 1-based for user reference
                }
                
                # Add optional columns if they exist
                if 'Nome azienda' in df.columns and pd.notna(row.get('Nome azienda')):
                    site_data['company_name'] = str(row['Nome azienda']).strip()
                
                if 'Codice ATECO' in df.columns and pd.notna(row.get('Codice ATECO')):
                    site_data['ateco_code'] = str(row['Codice ATECO']).strip()
                
                sites_data.append(site_data)
                
            except Exception as e:
                logger.warning(f"Skipping row {index + 1} due to error: {str(e)}")
                continue
        
        return sites_data
    
    def create_sample_excel(self) -> bytes:
        """Create a sample Excel file for user reference."""
        sample_data = pd.DataFrame({
            'Nome azienda': ['Azienda 1', 'Azienda 2', 'Azienda 3'],
            'URL': ['www.example1.com', 'https://example2.it', 'example3.org'],
            'Codice ATECO': ['62.01.00', '70.22.00', '73.11.00']
        })
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            sample_data.to_excel(writer, sheet_name='Competitors', index=False)
        
        return output.getvalue()

# Global processor instance
excel_processor = ExcelProcessor()