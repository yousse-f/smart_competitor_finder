import pandas as pd
from typing import List, Dict, Any
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Utility class for processing Excel files with competitor URLs."""
    
    def __init__(self):
        self.required_columns = ['URL']  # Can be extended to include 'Nome azienda', 'Codice ATECO'
        
    def process_excel_file(self, file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """
        Process uploaded Excel file and extract URLs.
        
        Args:
            file_content: Raw bytes of the Excel file
            filename: Original filename for logging
            
        Returns:
            List of dictionaries containing site data
            
        Raises:
            ValueError: If file format is invalid or required columns are missing
        """
        try:
            # Read Excel file from bytes
            df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
            
            logger.info(f"Processing Excel file: {filename} with {len(df)} rows")
            
            # Validate required columns
            self._validate_columns(df, filename)
            
            # Clean and process data
            sites_data = self._extract_sites_data(df)
            
            logger.info(f"Successfully extracted {len(sites_data)} valid URLs from {filename}")
            
            return sites_data
            
        except Exception as e:
            logger.error(f"Error processing Excel file {filename}: {str(e)}")
            raise ValueError(f"Failed to process Excel file: {str(e)}")
    
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