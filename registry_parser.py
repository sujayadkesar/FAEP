# # import os
# # import subprocess
# # import sys
# # import logging
# # from pathlib import Path

# # class RegistryParser:
# #     """Enhanced Registry Parser for forensic artifact analysis"""
    
# #     def __init__(self, registry_folder=None, regripper_path=None, output_folder=None):
# #         self.pwd = os.path.dirname(os.path.abspath(__file__))
        
# #         # Set default paths if not provided
# #         self.registry_folder = registry_folder or os.path.join("output", "registry")
# #         self.regripper_path = regripper_path or self._find_regripper()
# #         self.output_folder = output_folder or os.path.join(self.pwd, "parsed_artifacts", "registry")
        
# #         # Create output directory if it doesn't exist
# #         os.makedirs(self.output_folder, exist_ok=True)
        
# #         # Setup logging with UTF-8 encoding
# #         self.setup_logging()
        
# #     def _find_regripper(self):
# #         """Try to find RegRipper executable in common locations"""
# #         possible_paths = [
# #             r"C:\Users\sujay\Desktop\TAPE\tools\RegRipper4.0-main\rip.exe",
# #             r"tools\RegRipper4.0-main\rip.exe",
# #             r"RegRipper\rip.exe",
# #             "rip.exe"
# #         ]
        
# #         for path in possible_paths:
# #             if os.path.exists(path):
# #                 return path
        
# #         # If not found, return the default path
# #         return r"C:\Users\sujay\Desktop\TAPE\tools\RegRipper4.0-main\rip.exe"
    
# #     def setup_logging(self):
# #         """Setup logging for the parser with UTF-8 encoding"""
# #         self.logger = logging.getLogger('RegistryParser')
# #         if not self.logger.handlers:
# #             # Create file handler with UTF-8 encoding
# #             log_file = os.path.join(self.pwd, "registry_parser.log")
# #             file_handler = logging.FileHandler(log_file, encoding='utf-8')
            
# #             # Create console handler
# #             console_handler = logging.StreamHandler(sys.stdout)
# #             console_handler.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
            
# #             # Create formatter
# #             formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# #             file_handler.setFormatter(formatter)
# #             console_handler.setFormatter(formatter)
            
# #             # Add handlers to logger
# #             self.logger.addHandler(file_handler)
# #             self.logger.addHandler(console_handler)
# #             self.logger.setLevel(logging.INFO)
    
# #     def find_registry_files(self):
# #         """Find all registry files in the registry folder and subfolders"""
# #         registry_files = []
        
# #         if not os.path.exists(self.registry_folder):
# #             return registry_files
        
# #         # Common registry file names
# #         registry_names = [
# #             'SYSTEM', 'SOFTWARE', 'SAM', 'SECURITY', 'DEFAULT', 'NTUSER.DAT',
# #             'UsrClass.dat', 'Amcache.hve', 'COMPONENTS', 'BCD-Template'
# #         ]
        
# #         # Search recursively for registry files
# #         for root, dirs, files in os.walk(self.registry_folder):
# #             for file in files:
# #                 file_path = os.path.join(root, file)
                
# #                 # Check if it's a known registry file
# #                 if any(reg_name.lower() in file.upper() for reg_name in registry_names):
# #                     registry_files.append(file_path)
# #                     self.logger.info(f"Found registry file: {file_path}")
# #                 # Also check files without extensions that might be registry files
# #                 elif '.' not in file and os.path.getsize(file_path) > 1024:  # At least 1KB
# #                     registry_files.append(file_path)
# #                     self.logger.info(f"Found potential registry file: {file_path}")
        
# #         return registry_files
    
# #     def validate_environment(self):
# #         """Validate that all required components are available"""
# #         issues = []
        
# #         # Check if registry folder exists
# #         if not os.path.exists(self.registry_folder):
# #             issues.append(f"Registry folder not found: {self.registry_folder}")
        
# #         # Check if RegRipper exists
# #         if not os.path.exists(self.regripper_path):
# #             issues.append(f"RegRipper not found: {self.regripper_path}")
        
# #         # Check if registry folder has files
# #         registry_files = self.find_registry_files()
# #         if not registry_files:
# #             issues.append(f"No registry files found in: {self.registry_folder}")
        
# #         return issues
    
# #     def run_regripper(self, reg_file_path):
# #         """Run RegRipper on a single registry file"""
# #         command = [self.regripper_path, '-r', reg_file_path, '-a']
        
# #         try:
# #             self.logger.info(f"Running RegRipper on: {os.path.basename(reg_file_path)}")
            
# #             result = subprocess.run(
# #                 command, 
# #                 capture_output=True, 
# #                 text=True, 
# #                 encoding="utf-8", 
# #                 errors="ignore", 
# #                 timeout=300  # 5 minute timeout
# #             )
            
# #             if result.returncode == 0 and result.stdout.strip():
# #                 self.logger.info(f"Successfully parsed: {os.path.basename(reg_file_path)}")
# #                 return result.stdout
# #             else:
# #                 error_msg = result.stderr if result.stderr else "No output generated"
# #                 self.logger.error(f"RegRipper failed for {os.path.basename(reg_file_path)}: {error_msg}")
# #                 return None
                
# #         except subprocess.TimeoutExpired:
# #             self.logger.error(f"RegRipper timed out for: {os.path.basename(reg_file_path)}")
# #             return None
# #         except subprocess.CalledProcessError as e:
# #             self.logger.error(f"Error running RegRipper on {os.path.basename(reg_file_path)}: {e}")
# #             return None
# #         except Exception as e:
# #             self.logger.error(f"Unexpected error parsing {os.path.basename(reg_file_path)}: {e}")
# #             return None
    
# #     def parse_registry_files(self, progress_callback=None):
# #         """Parse all registry files in the registry folder using RegRipper"""
# #         # Validate environment first
# #         issues = self.validate_environment()
# #         if issues:
# #             error_msg = "Validation failed:\n" + "\n".join(issues)
# #             self.logger.error(error_msg)
# #             return {
# #                 'success': False,
# #                 'error': error_msg,
# #                 'parsed_files': [],
# #                 'failed_files': []
# #             }
        
# #         parsed_files = []
# #         failed_files = []
        
# #         # Get list of registry files
# #         try:
# #             reg_files = self.find_registry_files()
            
# #             total_files = len(reg_files)
# #             self.logger.info(f"Found {total_files} registry files to parse")
            
# #             if progress_callback:
# #                 progress_callback(f"Starting to parse {total_files} registry files...")
            
# #             for i, reg_file_path in enumerate(reg_files, 1):
# #                 reg_file = os.path.basename(reg_file_path)
                
# #                 if progress_callback:
# #                     progress_callback(f"Parsing {reg_file} ({i}/{total_files})...")
                
# #                 self.logger.info(f"Processing {reg_file} ({i}/{total_files})")
                
# #                 # Parse the registry file
# #                 parsed_data = self.run_regripper(reg_file_path)
                
# #                 if parsed_data:
# #                     # Save parsed data
# #                     safe_filename = reg_file.replace(':', '_').replace('\\', '_').replace('/', '_')
# #                     output_file_path = os.path.join(self.output_folder, f"{safe_filename}_parsed.txt")
                    
# #                     try:
# #                         with open(output_file_path, 'w', encoding="utf-8") as output_file:
# #                             output_file.write(f"Registry File: {reg_file}\n")
# #                             output_file.write(f"Source Path: {reg_file_path}\n")
# #                             output_file.write(f"Parsed on: {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}\n")
# #                             output_file.write("=" * 80 + "\n\n")
# #                             output_file.write(parsed_data)
                        
# #                         parsed_files.append({
# #                             'file': reg_file,
# #                             'output': output_file_path,
# #                             'size': len(parsed_data)
# #                         })
                        
# #                         self.logger.info(f"Successfully parsed and saved: {reg_file}")
                        
# #                     except Exception as e:
# #                         self.logger.error(f"Failed to save parsed data for {reg_file}: {e}")
# #                         failed_files.append({
# #                             'file': reg_file,
# #                             'error': f"Save error: {e}"
# #                         })
# #                 else:
# #                     failed_files.append({
# #                         'file': reg_file,
# #                         'error': "RegRipper parsing failed"
# #                     })
            
# #             # Generate summary
# #             success_count = len(parsed_files)
# #             failure_count = len(failed_files)
            
# #             summary = f"Registry parsing completed: {success_count} successful, {failure_count} failed"
# #             self.logger.info(summary)
            
# #             if progress_callback:
# #                 progress_callback(summary)
            
# #             return {
# #                 'success': success_count > 0,
# #                 'summary': summary,
# #                 'parsed_files': parsed_files,
# #                 'failed_files': failed_files,
# #                 'output_folder': self.output_folder
# #             }
            
# #         except Exception as e:
# #             error_msg = f"Error during registry parsing: {e}"
# #             self.logger.error(error_msg)
# #             return {
# #                 'success': False,
# #                 'error': error_msg,
# #                 'parsed_files': parsed_files,
# #                 'failed_files': failed_files
# #             }

# # def parse_registry_artifacts(registry_folder=None, regripper_path=None, progress_callback=None):
# #     """Convenience function to parse registry artifacts"""
# #     parser = RegistryParser(registry_folder, regripper_path)
# #     return parser.parse_registry_files(progress_callback)

# # if __name__ == '__main__':
# #     def test_progress_callback(message):
# #         print(f"Progress: {message}")
    
# #     result = parse_registry_artifacts(
# #         registry_folder=r'output\registry',
# #         progress_callback=test_progress_callback
# #     )
    
# #     print("\nFinal Result:")
# #     print(f"Success: {result['success']}")
# #     if result['success']:
# #         print(f"Summary: {result['summary']}")
# #         print(f"Parsed files: {len(result['parsed_files'])}")
# #         print(f"Failed files: {len(result['failed_files'])}")
# #     else:
# #         print(f"Error: {result['error']}")


# # # import os
# # # import subprocess
# # # import sys
# # # # Set the paths
# # # # registry_folder = 'output\\registry'  # Input folder containing registry files (e.g., SAM, SECURITY, SOFTWARE)
# # # pwd=os.path.dirname(os.path.abspath(sys.argv[0])) 
# # # parsed_folder = os.path.join(pwd,"parsed_artifacts","registry")  # Output folder to store parsed artifacts

# # # # Create the parsed folder if it does not exist
# # # if not os.path.exists(parsed_folder):
# # #     os.makedirs(parsed_folder)

# # # def run_regripper(reg_file):
# # #     command = ['C:\\Users\\sujay\\Desktop\\TAPE\\tools\\RegRipper4.0-main\\rip.exe', '-r', reg_file, '-a']
# # #     try:
# # #         # result = subprocess.run(command, capture_output=True, text=True, check=True)
# # #         result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="ignore", check=True)

# # #         print(result)
# # #         return result.stdout
# # #     except subprocess.CalledProcessError as e:
# # #         print(f"Error running Regripper on {reg_file}: {e.stderr}")  # Capture standard error message
# # #         return None


# # # def parse_registry_files(registry_folder):
# # #     """
# # #     Parse all registry files in the registry folder using Regripper.
# # #     """
# # #     # Loop through all files in the registry folder
# # #     if not os.path.exists(parsed_folder):
# # #         os.makedirs(parsed_folder)
# # #     for reg_file in os.listdir(registry_folder):
# # #         reg_file_path = os.path.join(registry_folder, reg_file)
        
# # #         # Check if it's a file (skip directories)
# # #         if os.path.isfile(reg_file_path):
# # #             print(f"Parsing {reg_file}...")
            
# # #             # Run regripper and get parsed data
# # #             parsed_data = run_regripper(reg_file_path)
            
# # #             if parsed_data:
# # #                 # Save the parsed data to a .txt file in the parsed_artifacts folder
# # #                 output_file_path = os.path.join(parsed_folder, f"{reg_file}.txt")
# # #                 # with open(output_file_path, 'w') as output_file:
# # #                 with open(output_file_path, 'w', encoding="utf-8") as output_file:
# # #                     output_file.write(parsed_data)
# # #                 print(f"Parsed {reg_file} and saved to {output_file_path}")
# # #             else:
# # #                 print(f"Failed to parse {reg_file}")
# # #         else:
# # #             print(f"Skipping non-file {reg_file}")

# # # # if __name__ == '__main__':
# # # #     registry_folder = r'output\registry'
# # # #     parse_registry_files(registry_folder)

# import os
# import subprocess
# import sys
# import logging
# from pathlib import Path

# class RegistryParser:
#     """Enhanced Registry Parser for forensic artifact analysis"""
    
#     def __init__(self, registry_folder=None, regripper_path=None, output_folder=None):
#         self.pwd = os.path.dirname(os.path.abspath(__file__))
        
#         # Set default paths with absolute path resolution
#         if registry_folder:
#             self.registry_folder = os.path.abspath(registry_folder)
#         else:
#             self.registry_folder = os.path.abspath(os.path.join("output", "registry"))
            
#         self.regripper_path = regripper_path or self._find_regripper()
        
#         if output_folder:
#             self.output_folder = os.path.abspath(output_folder)
#         else:
#             self.output_folder = os.path.abspath(os.path.join(self.pwd, "parsed_artifacts", "registry"))
        
#         # Create output directory if it doesn't exist
#         os.makedirs(self.output_folder, exist_ok=True)
        
#         # Setup logging with UTF-8 encoding
#         self.setup_logging()
        
#     def _find_regripper(self):
#         """Try to find RegRipper executable in common locations"""
#         possible_paths = [
#             r"C:\Users\sujay\Desktop\TAPE\tools\RegRipper4.0-main\rip.exe",
#             r"tools\RegRipper4.0-main\rip.exe",
#             r"RegRipper\rip.exe",
#             "rip.exe"
#         ]
        
#         for path in possible_paths:
#             abs_path = os.path.abspath(path)
#             if os.path.exists(abs_path):
#                 return abs_path
        
#         # If not found, return the default path
#         return os.path.abspath(r"C:\Users\sujay\Desktop\TAPE\tools\RegRipper4.0-main\rip.exe")
    
#     def setup_logging(self):
#         """Setup logging for the parser with UTF-8 encoding"""
#         self.logger = logging.getLogger('RegistryParser')
#         if not self.logger.handlers:
#             # Create file handler with UTF-8 encoding
#             log_file = os.path.join(self.pwd, "registry_parser.log")
#             file_handler = logging.FileHandler(log_file, encoding='utf-8')
            
#             # Create console handler with proper encoding
#             console_handler = logging.StreamHandler(sys.stdout)
            
#             # Create formatter
#             formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#             file_handler.setFormatter(formatter)
#             console_handler.setFormatter(formatter)
            
#             # Add handlers to logger
#             self.logger.addHandler(file_handler)
#             self.logger.addHandler(console_handler)
#             self.logger.setLevel(logging.INFO)
    
#     def find_registry_files(self):
#         """Find all registry files in the registry folder and subfolders"""
#         registry_files = []
        
#         self.logger.info(f"Searching for registry files in: {self.registry_folder}")
        
#         if not os.path.exists(self.registry_folder):
#             self.logger.warning(f"Registry folder does not exist: {self.registry_folder}")
#             return registry_files
        
#         # Common registry file names (case insensitive)
#         registry_names = [
#             'SYSTEM', 'SOFTWARE', 'SAM', 'SECURITY', 'DEFAULT', 'NTUSER.DAT',
#             'UsrClass.dat', 'Amcache.hve', 'COMPONENTS', 'BCD-Template', 'BCD'
#         ]
        
#         # Search recursively for registry files
#         for root, dirs, files in os.walk(self.registry_folder):
#             self.logger.info(f"Scanning directory: {root}")
#             for file in files:
#                 file_path = os.path.join(root, file)
#                 file_upper = file.upper()
                
#                 # Check if it's a known registry file (case insensitive)
#                 is_registry = False
#                 for reg_name in registry_names:
#                     if reg_name.upper() in file_upper or file_upper == reg_name.upper():
#                         is_registry = True
#                         break
                
#                 if is_registry:
#                     registry_files.append(file_path)
#                     self.logger.info(f"Found registry file: {file_path}")
#                 # Also check files without extensions that might be registry files
#                 elif '.' not in file and os.path.getsize(file_path) > 1024:  # At least 1KB
#                     registry_files.append(file_path)
#                     self.logger.info(f"Found potential registry file: {file_path}")
        
#         self.logger.info(f"Total registry files found: {len(registry_files)}")
#         return registry_files
    
#     def validate_environment(self):
#         """Validate that all required components are available"""
#         issues = []
        
#         # Check if registry folder exists
#         if not os.path.exists(self.registry_folder):
#             issues.append(f"Registry folder not found: {self.registry_folder}")
        
#         # Check if RegRipper exists
#         if not os.path.exists(self.regripper_path):
#             issues.append(f"RegRipper not found: {self.regripper_path}")
        
#         # Check if registry folder has files
#         registry_files = self.find_registry_files()
#         if not registry_files:
#             issues.append(f"No registry files found in: {self.registry_folder}")
        
#         return issues
    
#     def run_regripper(self, reg_file_path):
#         """Run RegRipper on a single registry file"""
#         command = [self.regripper_path, '-r', reg_file_path, '-a']
        
#         try:
#             self.logger.info(f"Running RegRipper on: {os.path.basename(reg_file_path)}")
#             self.logger.info(f"Command: {' '.join(command)}")
            
#             result = subprocess.run(
#                 command, 
#                 capture_output=True, 
#                 text=True, 
#                 encoding="utf-8", 
#                 errors="ignore", 
#                 timeout=300,  # 5 minute timeout
#                 cwd=os.path.dirname(self.regripper_path)  # Set working directory
#             )
            
#             if result.returncode == 0 and result.stdout.strip():
#                 self.logger.info(f"Successfully parsed: {os.path.basename(reg_file_path)}")
#                 return result.stdout
#             else:
#                 error_msg = result.stderr if result.stderr else "No output generated"
#                 self.logger.error(f"RegRipper failed for {os.path.basename(reg_file_path)}: {error_msg}")
#                 self.logger.error(f"Return code: {result.returncode}")
#                 return None
                
#         except subprocess.TimeoutExpired:
#             self.logger.error(f"RegRipper timed out for: {os.path.basename(reg_file_path)}")
#             return None
#         except subprocess.CalledProcessError as e:
#             self.logger.error(f"Error running RegRipper on {os.path.basename(reg_file_path)}: {e}")
#             return None
#         except Exception as e:
#             self.logger.error(f"Unexpected error parsing {os.path.basename(reg_file_path)}: {e}")
#             return None
    
#     def parse_registry_files(self, progress_callback=None):
#         """Parse all registry files in the registry folder using RegRipper"""
#         # Validate environment first
#         issues = self.validate_environment()
#         if issues:
#             error_msg = "Validation failed:\n" + "\n".join(issues)
#             self.logger.error(error_msg)
#             return {
#                 'success': False,
#                 'error': error_msg,
#                 'parsed_files': [],
#                 'failed_files': []
#             }
        
#         parsed_files = []
#         failed_files = []
        
#         # Get list of registry files
#         try:
#             reg_files = self.find_registry_files()
            
#             total_files = len(reg_files)
#             self.logger.info(f"Found {total_files} registry files to parse")
            
#             if progress_callback:
#                 progress_callback(f"Starting to parse {total_files} registry files...")
            
#             for i, reg_file_path in enumerate(reg_files, 1):
#                 reg_file = os.path.basename(reg_file_path)
                
#                 if progress_callback:
#                     progress_callback(f"Parsing {reg_file} ({i}/{total_files})...")
                
#                 self.logger.info(f"Processing {reg_file} ({i}/{total_files})")
                
#                 # Parse the registry file
#                 parsed_data = self.run_regripper(reg_file_path)
                
#                 if parsed_data:
#                     # Save parsed data
#                     safe_filename = reg_file.replace(':', '_').replace('\\', '_').replace('/', '_').replace('?', '_').replace('*', '_')
#                     output_file_path = os.path.join(self.output_folder, f"{safe_filename}_parsed.txt")
                    
#                     try:
#                         with open(output_file_path, 'w', encoding="utf-8") as output_file:
#                             output_file.write(f"Registry File: {reg_file}\n")
#                             output_file.write(f"Source Path: {reg_file_path}\n")
#                             output_file.write(f"Parsed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
#                             output_file.write("=" * 80 + "\n\n")
#                             output_file.write(parsed_data)
                        
#                         parsed_files.append({
#                             'file': reg_file,
#                             'output': output_file_path,
#                             'size': len(parsed_data)
#                         })
                        
#                         self.logger.info(f"Successfully parsed and saved: {reg_file}")
                        
#                     except Exception as e:
#                         self.logger.error(f"Failed to save parsed data for {reg_file}: {e}")
#                         failed_files.append({
#                             'file': reg_file,
#                             'error': f"Save error: {e}"
#                         })
#                 else:
#                     failed_files.append({
#                         'file': reg_file,
#                         'error': "RegRipper parsing failed"
#                     })
            
#             # Generate summary
#             success_count = len(parsed_files)
#             failure_count = len(failed_files)
            
#             summary = f"Registry parsing completed: {success_count} successful, {failure_count} failed"
#             self.logger.info(summary)
            
#             if progress_callback:
#                 progress_callback(summary)
            
#             return {
#                 'success': success_count > 0,
#                 'summary': summary,
#                 'parsed_files': parsed_files,
#                 'failed_files': failed_files,
#                 'output_folder': self.output_folder
#             }
            
#         except Exception as e:
#             error_msg = f"Error during registry parsing: {e}"
#             self.logger.error(error_msg)
#             return {
#                 'success': False,
#                 'error': error_msg,
#                 'parsed_files': parsed_files,
#                 'failed_files': failed_files
#             }

# def parse_registry_artifacts(registry_folder=None, regripper_path=None, progress_callback=None):
#     """Convenience function to parse registry artifacts"""
#     parser = RegistryParser(registry_folder, regripper_path)
#     return parser.parse_registry_files(progress_callback)

# if __name__ == '__main__':
#     def test_progress_callback(message):
#         print(f"Progress: {message}")
    
#     result = parse_registry_artifacts(
#         registry_folder=r'output\registry',
#         progress_callback=test_progress_callback
#     )
    
#     print("\nFinal Result:")
#     print(f"Success: {result['success']}")
#     if result['success']:
#         print(f"Summary: {result['summary']}")
#         print(f"Parsed files: {len(result['parsed_files'])}")
#         print(f"Failed files: {len(result['failed_files'])}")
#     else:
#         print(f"Error: {result['error']}")
import os
import subprocess
import sys
import logging
from pathlib import Path
from datetime import datetime

class RegistryParser:
    """Enhanced Registry Parser for forensic artifact analysis"""
    
    def __init__(self, registry_folder=None, regripper_path=None, output_folder=None):
        self.pwd = os.path.dirname(os.path.abspath(__file__))
        
        # Set default paths with absolute path resolution
        if registry_folder:
            self.registry_folder = os.path.abspath(registry_folder)
        else:
            self.registry_folder = os.path.abspath(os.path.join("output", "registry"))
            
        self.regripper_path = regripper_path or self._find_regripper()
        
        if output_folder:
            self.output_folder = os.path.abspath(output_folder)
        else:
            self.output_folder = os.path.abspath(os.path.join(self.pwd, "parsed_artifacts", "registry"))
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Setup logging with UTF-8 encoding
        self.setup_logging()
        
    def _find_regripper(self):
        """Try to find RegRipper executable in common locations"""
        possible_paths = [
            r"C:\Users\sujay\Desktop\TAPE\tools\RegRipper4.0-main\rip.exe",
            r"tools\RegRipper4.0-main\rip.exe",
            r"RegRipper\rip.exe",
            "rip.exe"
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                return abs_path
        
        # If not found, return the default path
        return os.path.abspath(r"C:\Users\sujay\Desktop\TAPE\tools\RegRipper4.0-main\rip.exe")
    
    def setup_logging(self):
        """Setup logging for the parser with UTF-8 encoding"""
        self.logger = logging.getLogger('RegistryParser')
        if not self.logger.handlers:
            # Create file handler with UTF-8 encoding
            log_file = os.path.join(self.pwd, "registry_parser.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            
            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers to logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)
    
    def find_registry_files(self):
        """Find all registry files in the registry folder and subfolders with better validation"""
        registry_files = []
        
        self.logger.info(f"Searching for registry files in: {self.registry_folder}")
        
        if not os.path.exists(self.registry_folder):
            self.logger.warning(f"Registry folder does not exist: {self.registry_folder}")
            return registry_files
        
        # Common registry file names (case insensitive)
        registry_names = [
            'SYSTEM', 'SOFTWARE', 'SAM', 'SECURITY', 'DEFAULT', 'NTUSER.DAT',
            'UsrClass.dat', 'Amcache.hve', 'COMPONENTS', 'BCD-Template', 'BCD'
        ]
        
        # Search recursively for registry files
        for root, dirs, files in os.walk(self.registry_folder):
            self.logger.info(f"Scanning directory: {root}")
            for file in files:
                file_path = os.path.join(root, file)
                file_upper = file.upper()
                
                # Check file size - registry files should be substantial
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size < 10240:  # Less than 10KB, probably not a real registry file
                        continue
                except:
                    continue
                
                # Check if it's a known registry file (case insensitive)
                is_registry = False
                for reg_name in registry_names:
                    if reg_name.upper() in file_upper or file_upper == reg_name.upper():
                        is_registry = True
                        break
                
                if is_registry:
                    registry_files.append(file_path)
                    self.logger.info(f"Found registry file: {file_path} ({file_size:,} bytes)")
                # Also check files without extensions that might be registry files
                elif '.' not in file and file_size > 10240:  # At least 10KB
                    # Additional validation - check if file starts with registry signature
                    try:
                        with open(file_path, 'rb') as f:
                            header = f.read(4)
                            if header == b'regf':  # Registry file signature
                                registry_files.append(file_path)
                                self.logger.info(f"Found registry file by signature: {file_path} ({file_size:,} bytes)")
                    except:
                        pass
        
        self.logger.info(f"Total registry files found: {len(registry_files)}")
        return registry_files
    
    def validate_environment(self):
        """Validate that all required components are available"""
        issues = []
        
        # Check if registry folder exists
        if not os.path.exists(self.registry_folder):
            issues.append(f"Registry folder not found: {self.registry_folder}")
        
        # Check if RegRipper exists
        if not os.path.exists(self.regripper_path):
            issues.append(f"RegRipper not found: {self.regripper_path}")
        
        # Check if registry folder has files
        registry_files = self.find_registry_files()
        if not registry_files:
            issues.append(f"No valid registry files found in: {self.registry_folder}")
        
        return issues
    
    def run_regripper(self, reg_file_path):
        """Run RegRipper on a single registry file with enhanced validation"""
        # First, validate the registry file
        try:
            file_size = os.path.getsize(reg_file_path)
            if file_size < 10240:  # Less than 10KB
                self.logger.warning(f"Registry file too small: {reg_file_path} ({file_size} bytes)")
                return None
        except:
            self.logger.error(f"Cannot access registry file: {reg_file_path}")
            return None
        
        # Check if file is actually a registry file
        try:
            with open(reg_file_path, 'rb') as f:
                header = f.read(4)
                if header != b'regf':
                    self.logger.warning(f"File does not have registry signature: {reg_file_path}")
                    # Still try to parse, but with caution
        except:
            pass
        
        command = [self.regripper_path, '-r', reg_file_path, '-a']
        
        try:
            self.logger.info(f"Running RegRipper on: {os.path.basename(reg_file_path)} ({file_size:,} bytes)")
            self.logger.info(f"Command: {' '.join(command)}")
            
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                encoding="utf-8", 
                errors="ignore", 
                timeout=300,  # 5 minute timeout
                cwd=os.path.dirname(self.regripper_path)  # Set working directory
            )
            
            if result.returncode == 0 and result.stdout.strip():
                output_size = len(result.stdout)
                if output_size > 100:  # Ensure we have substantial output
                    self.logger.info(f"Successfully parsed: {os.path.basename(reg_file_path)} - Output: {output_size:,} characters")
                    return result.stdout
                else:
                    self.logger.warning(f"RegRipper output too small for {os.path.basename(reg_file_path)}: {output_size} characters")
                    return None
            else:
                error_msg = result.stderr if result.stderr else "No output generated or return code non-zero"
                self.logger.error(f"RegRipper failed for {os.path.basename(reg_file_path)}: {error_msg}")
                self.logger.error(f"Return code: {result.returncode}")
                self.logger.error(f"Stdout: {result.stdout[:500]}...")  # First 500 chars
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"RegRipper timed out for: {os.path.basename(reg_file_path)}")
            return None
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running RegRipper on {os.path.basename(reg_file_path)}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error parsing {os.path.basename(reg_file_path)}: {e}")
            return None
    
    def parse_registry_files(self, progress_callback=None):
        """Parse all registry files in the registry folder using RegRipper"""
        # Validate environment first
        issues = self.validate_environment()
        if issues:
            error_msg = "Validation failed:\n" + "\n".join(issues)
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'parsed_files': [],
                'failed_files': []
            }
        
        parsed_files = []
        failed_files = []
        
        # Get list of registry files
        try:
            reg_files = self.find_registry_files()
            
            total_files = len(reg_files)
            self.logger.info(f"Found {total_files} registry files to parse")
            
            if progress_callback:
                progress_callback(f"Starting to parse {total_files} registry files...")
            
            for i, reg_file_path in enumerate(reg_files, 1):
                reg_file = os.path.basename(reg_file_path)
                
                if progress_callback:
                    progress_callback(f"Parsing {reg_file} ({i}/{total_files})...")
                
                self.logger.info(f"Processing {reg_file} ({i}/{total_files})")
                
                # Parse the registry file
                parsed_data = self.run_regripper(reg_file_path)
                
                if parsed_data and len(parsed_data) > 100:  # Ensure substantial output
                    # Save parsed data
                    safe_filename = reg_file.replace(':', '_').replace('\\', '_').replace('/', '_').replace('?', '_').replace('*', '_')
                    output_file_path = os.path.join(self.output_folder, f"{safe_filename}_parsed.txt")
                    
                    try:
                        with open(output_file_path, 'w', encoding="utf-8") as output_file:
                            output_file.write(f"Registry File: {reg_file}\n")
                            output_file.write(f"Source Path: {reg_file_path}\n")
                            output_file.write(f"File Size: {os.path.getsize(reg_file_path):,} bytes\n")
                            output_file.write(f"Parsed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            output_file.write("=" * 80 + "\n\n")
                            output_file.write(parsed_data)
                        
                        parsed_files.append({
                            'file': reg_file,
                            'output': output_file_path,
                            'size': len(parsed_data),
                            'source_size': os.path.getsize(reg_file_path)
                        })
                        
                        self.logger.info(f"Successfully parsed and saved: {reg_file} -> {len(parsed_data):,} characters")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to save parsed data for {reg_file}: {e}")
                        failed_files.append({
                            'file': reg_file,
                            'error': f"Save error: {e}"
                        })
                else:
                    failed_files.append({
                        'file': reg_file,
                        'error': "RegRipper parsing failed or output too small"
                    })
            
            # Generate summary
            success_count = len(parsed_files)
            failure_count = len(failed_files)
            
            summary = f"Registry parsing completed: {success_count} successful, {failure_count} failed"
            self.logger.info(summary)
            
            if progress_callback:
                progress_callback(summary)
            
            return {
                'success': success_count > 0,
                'summary': summary,
                'parsed_files': parsed_files,
                'failed_files': failed_files,
                'output_folder': self.output_folder
            }
            
        except Exception as e:
            error_msg = f"Error during registry parsing: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'parsed_files': parsed_files,
                'failed_files': failed_files
            }

def parse_registry_artifacts(registry_folder=None, regripper_path=None, progress_callback=None):
    """Convenience function to parse registry artifacts"""
    parser = RegistryParser(registry_folder, regripper_path)
    return parser.parse_registry_files(progress_callback)

if __name__ == '__main__':
    def test_progress_callback(message):
        print(f"Progress: {message}")
    
    result = parse_registry_artifacts(
        registry_folder=r'output\registry',
        progress_callback=test_progress_callback
    )
    
    print("\nFinal Result:")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Summary: {result['summary']}")
        print(f"Parsed files: {len(result['parsed_files'])}")
        print(f"Failed files: {len(result['failed_files'])}")
    else:
        print(f"Error: {result['error']}")
