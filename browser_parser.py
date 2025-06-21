import os
import subprocess
import sys
import logging
from pathlib import Path
import shutil

class BrowserParser:
    """Enhanced Browser Parser for forensic artifact analysis using Hindsight"""
    
    def __init__(self, browser_folder=None, hindsight_path=None, output_folder=None):
        self.pwd = os.path.dirname(os.path.abspath(__file__))
        
        # Set default paths if not provided
        self.browser_folder = browser_folder or os.path.join("output", "browser")
        self.hindsight_path = hindsight_path or self._find_hindsight()
        self.output_folder = output_folder or os.path.join(self.pwd, "parsed_artifacts", "browser")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Supported browsers
        self.supported_browsers = ['chrome', 'edge']
        
    def _find_hindsight(self):
        """Try to find Hindsight script in common locations"""
        possible_paths = [
            r"tools\hindsight\hindsight.py",
            r"C:\Users\sujay\Desktop\TAPE\tools\hindsight\hindsight.py",
            r"hindsight\hindsight.py",
            "hindsight.py"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If not found, return the default path
        return r"tools\hindsight\hindsight.py"
    
    def setup_logging(self):
        """Setup logging for the parser"""
        self.logger = logging.getLogger('BrowserParser')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def validate_environment(self):
        """Validate that all required components are available"""
        issues = []
        
        # Check if browser folder exists
        if not os.path.exists(self.browser_folder):
            issues.append(f"Browser folder not found: {self.browser_folder}")
        
        # Check if Hindsight exists
        if not os.path.exists(self.hindsight_path):
            issues.append(f"Hindsight not found: {self.hindsight_path}")
        
        # Check if browser folder has browser directories
        if os.path.exists(self.browser_folder):
            browser_dirs = []
            for browser in self.supported_browsers:
                browser_path = os.path.join(self.browser_folder, browser)
                if os.path.exists(browser_path):
                    browser_dirs.append(browser)
            
            if not browser_dirs:
                issues.append(f"No supported browser directories found in: {self.browser_folder}")
        
        return issues
    
    def run_hindsight(self, input_path, output_file, format_type):
        """Run Hindsight on a browser profile"""
        command = [
            'python',
            self.hindsight_path,
            '-i', input_path,
            '-o', output_file,
            '--format', format_type
        ]
        
        try:
            self.logger.info(f"Running Hindsight on: {input_path} (format: {format_type})")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully processed {format_type} format for: {os.path.basename(input_path)}")
                return True, result.stdout
            else:
                self.logger.error(f"Hindsight failed for {input_path} ({format_type}): {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Hindsight timed out for: {input_path} ({format_type})")
            return False, "Process timed out"
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running Hindsight on {input_path} ({format_type}): {e}")
            return False, str(e)
        except Exception as e:
            self.logger.error(f"Unexpected error processing {input_path} ({format_type}): {e}")
            return False, str(e)
    
    def process_browser_profile(self, browser_name, username, profile_path, progress_callback=None):
        """Process a single browser profile"""
        results = []
        
        # Create output directory for this user
        user_output_path = os.path.join(self.output_folder, browser_name, username)
        os.makedirs(user_output_path, exist_ok=True)
        
        # Set base output filename
        output_base = os.path.join(user_output_path, f'{username}_browser_artifacts')
        
        # Process both SQLite and XLSX formats
        formats = ['sqlite', 'xlsx']
        
        for format_type in formats:
            if progress_callback:
                progress_callback(f"Processing {browser_name} - {username} ({format_type} format)...")
            
            success, output = self.run_hindsight(profile_path, output_base, format_type)
            
            result_info = {
                'browser': browser_name,
                'username': username,
                'format': format_type,
                'success': success,
                'output_file': f"{output_base}.{format_type}",
                'profile_path': profile_path
            }
            
            if success:
                # Check if output file was created
                expected_file = f"{output_base}.{format_type}"
                if os.path.exists(expected_file):
                    file_size = os.path.getsize(expected_file)
                    result_info['file_size'] = file_size
                    self.logger.info(f"Created {format_type} file: {expected_file} ({file_size:,} bytes)")
                else:
                    result_info['success'] = False
                    result_info['error'] = "Output file not created"
            else:
                result_info['error'] = output
            
            results.append(result_info)
        
        return results
    
    def process_browser(self, browser_name, browser_path, progress_callback=None):
        """Process all profiles for a specific browser"""
        browser_results = []
        
        if not os.path.exists(browser_path):
            self.logger.warning(f"{browser_name} directory not found: {browser_path}")
            return browser_results
        
        self.logger.info(f"Processing {browser_name} browser at: {browser_path}")
        
        try:
            # Look for user profiles
            for item in os.listdir(browser_path):
                user_path = os.path.join(browser_path, item)
                
                if os.path.isdir(user_path):
                    # Look for Default profile or other profile directories
                    profile_candidates = ['Default', 'Profile 1', 'Profile 2', 'Profile 3']
                    
                    for profile_name in profile_candidates:
                        profile_path = os.path.join(user_path, profile_name)
                        
                        if os.path.isdir(profile_path):
                            username = f"{item}_{profile_name}" if profile_name != 'Default' else item
                            
                            if progress_callback:
                                progress_callback(f"Found {browser_name} profile: {username}")
                            
                            # Process this profile
                            profile_results = self.process_browser_profile(
                                browser_name, username, profile_path, progress_callback
                            )
                            browser_results.extend(profile_results)
                    
                    # If no standard profiles found, try to process the user directory directly
                    if not any(os.path.isdir(os.path.join(user_path, p)) for p in profile_candidates):
                        # Check if this directory contains browser files directly
                        browser_files = ['History', 'Cookies', 'Web Data', 'Login Data']
                        if any(os.path.exists(os.path.join(user_path, f)) for f in browser_files):
                            if progress_callback:
                                progress_callback(f"Found {browser_name} direct profile: {item}")
                            
                            profile_results = self.process_browser_profile(
                                browser_name, item, user_path, progress_callback
                            )
                            browser_results.extend(profile_results)
        
        except Exception as e:
            self.logger.error(f"Error processing {browser_name} browser: {e}")
        
        return browser_results
    
    def parse_browser_artifacts(self, progress_callback=None):
        """
        Parse all browser artifacts using Hindsight
        
        Args:
            progress_callback: Optional callback function to report progress
            
        Returns:
            dict: Results of parsing operation
        """
        # Validate environment first
        issues = self.validate_environment()
        if issues:
            error_msg = "Validation failed:\n" + "\n".join(issues)
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'processed_profiles': [],
                'failed_profiles': []
            }
        
        all_results = []
        processed_profiles = []
        failed_profiles = []
        
        try:
            if progress_callback:
                progress_callback("Starting browser artifact parsing...")
            
            # Process each supported browser
            for browser_name in self.supported_browsers:
                browser_path = os.path.join(self.browser_folder, browser_name)
                
                if os.path.exists(browser_path):
                    self.logger.info(f"Processing {browser_name} browser...")
                    
                    if progress_callback:
                        progress_callback(f"Processing {browser_name} browser...")
                    
                    browser_results = self.process_browser(browser_name, browser_path, progress_callback)
                    all_results.extend(browser_results)
                else:
                    self.logger.info(f"{browser_name} directory not found, skipping...")
            
            # Categorize results
            for result in all_results:
                profile_id = f"{result['browser']}_{result['username']}_{result['format']}"
                
                if result['success']:
                    processed_profiles.append(result)
                else:
                    failed_profiles.append(result)
            
            # Generate summary
            success_count = len(processed_profiles)
            failure_count = len(failed_profiles)
            
            summary = f"Browser parsing completed: {success_count} successful, {failure_count} failed"
            self.logger.info(summary)
            
            if progress_callback:
                progress_callback(summary)
            
            return {
                'success': True,
                'summary': summary,
                'processed_profiles': processed_profiles,
                'failed_profiles': failed_profiles,
                'output_folder': self.output_folder,
                'total_processed': success_count,
                'total_failed': failure_count
            }
            
        except Exception as e:
            error_msg = f"Error during browser parsing: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'processed_profiles': processed_profiles,
                'failed_profiles': failed_profiles
            }
    
    def get_parsing_summary(self):
        """Get a summary of parsed browser artifacts"""
        if not os.path.exists(self.output_folder):
            return "No parsed browser artifacts found"
        
        summary = f"Browser Parsing Summary:\n"
        summary += f"Output folder: {self.output_folder}\n\n"
        
        for browser in self.supported_browsers:
            browser_path = os.path.join(self.output_folder, browser)
            if os.path.exists(browser_path):
                summary += f"{browser.title()} Browser:\n"
                
                for user_dir in os.listdir(browser_path):
                    user_path = os.path.join(browser_path, user_dir)
                    if os.path.isdir(user_path):
                        files = [f for f in os.listdir(user_path) if f.endswith(('.sqlite', '.xlsx'))]
                        summary += f"  User: {user_dir} ({len(files)} files)\n"
                        
                        for file in files:
                            file_path = os.path.join(user_path, file)
                            file_size = os.path.getsize(file_path)
                            summary += f"    - {file} ({file_size:,} bytes)\n"
                
                summary += "\n"
        
        return summary

def parse_browser_artifacts(browser_folder=None, hindsight_path=None, progress_callback=None):
    """
    Convenience function to parse browser artifacts
    This is the main function that will be called from the GUI
    
    Args:
        browser_folder: Path to folder containing browser artifacts
        hindsight_path: Path to Hindsight script
        progress_callback: Function to call with progress updates
        
    Returns:
        dict: Results of parsing operation
    """
    parser = BrowserParser(browser_folder, hindsight_path)
    return parser.parse_browser_artifacts(progress_callback)

# Example usage for testing
if __name__ == '__main__':
    def test_progress_callback(message):
        print(f"Progress: {message}")
    
    # Test the parser
    result = parse_browser_artifacts(
        browser_folder=r'output\browser',
        progress_callback=test_progress_callback
    )
    
    print("\nFinal Result:")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Summary: {result['summary']}")
        print(f"Processed profiles: {result['total_processed']}")
        print(f"Failed profiles: {result['total_failed']}")
    else:
        print(f"Error: {result['error']}")
