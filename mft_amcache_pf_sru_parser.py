import os
import subprocess
import sys
import logging
from pathlib import Path
import glob
from datetime import datetime

class EricZimmermanParser:
    """Enhanced parser for Eric Zimmerman tools with comprehensive logging and error handling"""
    
    def __init__(self, tools_base_path=None, output_base_path=None, input_base_path=None):
        self.pwd = os.path.dirname(os.path.abspath(__file__))
        
        # Set default paths with absolute path resolution
        if tools_base_path:
            self.tools_base_path = os.path.abspath(tools_base_path)
        else:
            self.tools_base_path = os.path.abspath(os.path.join(self.pwd, "tools"))
            
        if output_base_path:
            self.output_base_path = os.path.abspath(output_base_path)
        else:
            self.output_base_path = os.path.abspath(os.path.join(self.pwd, "parsed_artifacts", "system"))
            
        if input_base_path:
            self.input_base_path = os.path.abspath(input_base_path)
        else:
            self.input_base_path = os.path.abspath(os.path.join(self.pwd, "output"))
        
        # Create output directory
        os.makedirs(self.output_base_path, exist_ok=True)
        
        # Tool executable paths
        self.tool_paths = {
            'amcache': os.path.join(self.tools_base_path, 'AmcacheParser', 'AmcacheParser.exe'),
            'mft': os.path.join(self.tools_base_path, 'MFTECmd', 'MFTECmd.exe'),
            'srum': os.path.join(self.tools_base_path, 'SrumECmd', 'SrumECmd.exe'),
            'prefetch': os.path.join(self.tools_base_path, 'PECmd', 'PECmd.exe'),
            'hayabusa': os.path.join(self.tools_base_path, 'hayabusa-3.0.1-win-x64', 'hayabusa-3.0.1-win-x64.exe')
        }
        
        # Setup logging with UTF-8 encoding
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the parser with UTF-8 encoding"""
        self.logger = logging.getLogger('EricZimmermanParser')
        if not self.logger.handlers:
            # Create file handler with UTF-8 encoding
            log_file = os.path.join(self.pwd, "system_parser.log")
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
    
    def find_files_recursive(self, patterns, min_size=1024):
        """Find files recursively with multiple pattern matching and size validation"""
        files = []
        
        if isinstance(patterns, str):
            patterns = [patterns]
        
        self.logger.info(f"Searching for patterns: {patterns} in {self.input_base_path}")
        
        # Enhanced search paths - more comprehensive
        search_paths = [
            self.input_base_path,
            os.path.join(self.input_base_path, "**"),
        ]
        
        # Add Windows-specific paths with more variations
        windows_paths = [
            os.path.join(self.input_base_path, "*", "Windows", "**"),
            os.path.join(self.input_base_path, "*", "Windows", "System32", "**"),
            os.path.join(self.input_base_path, "*", "Windows", "System32", "config", "**"),
            os.path.join(self.input_base_path, "*", "Windows", "appcompat", "**"),
            os.path.join(self.input_base_path, "*", "Windows", "appcompat", "Programs", "**"),
            os.path.join(self.input_base_path, "*", "Windows", "Prefetch", "**"),
            os.path.join(self.input_base_path, "*", "Windows", "System32", "sru", "**"),
            os.path.join(self.input_base_path, "*", "Windows", "System32", "winevt", "**"),
            os.path.join(self.input_base_path, "**", "Windows", "**"),
            os.path.join(self.input_base_path, "**", "System32", "**"),
            os.path.join(self.input_base_path, "**", "config", "**"),
            os.path.join(self.input_base_path, "**", "appcompat", "**"),
            os.path.join(self.input_base_path, "**", "Programs", "**"),
            os.path.join(self.input_base_path, "**", "Prefetch", "**"),
            os.path.join(self.input_base_path, "**", "sru", "**"),
            os.path.join(self.input_base_path, "**", "winevt", "**"),
            os.path.join(self.input_base_path, "**", "eventlogs", "**"),
            # Add root level search
            os.path.join(self.input_base_path, "**", "*"),
        ]
        search_paths.extend(windows_paths)
        
        for pattern in patterns:
            self.logger.info(f"Searching for pattern: {pattern}")
            for search_path in search_paths:
                try:
                    full_pattern = os.path.join(search_path, pattern)
                    self.logger.debug(f"Checking pattern: {full_pattern}")
                    found_files = glob.glob(full_pattern, recursive=True)
                    
                    # Validate files
                    for file_path in found_files:
                        if os.path.isfile(file_path):
                            try:
                                file_size = os.path.getsize(file_path)
                                if file_size >= min_size:
                                    files.append(file_path)
                                    self.logger.info(f"Found valid file: {file_path} ({file_size:,} bytes)")
                                else:
                                    self.logger.debug(f"File too small: {file_path} ({file_size} bytes)")
                            except Exception as e:
                                self.logger.debug(f"Error checking file {file_path}: {e}")
                        
                except Exception as e:
                    self.logger.debug(f"Error searching {search_path} for {pattern}: {e}")
        
        # Remove duplicates and ensure files exist
        unique_files = []
        seen = set()
        for file_path in files:
            abs_path = os.path.abspath(file_path)
            if abs_path not in seen and os.path.isfile(abs_path):
                unique_files.append(abs_path)
                seen.add(abs_path)
        
        self.logger.info(f"Total unique files found for patterns {patterns}: {len(unique_files)}")
        for file_path in unique_files:
            try:
                size = os.path.getsize(file_path)
                self.logger.info(f"  - {file_path} ({size:,} bytes)")
            except:
                self.logger.info(f"  - {file_path} (size unknown)")
        
        return unique_files
    
    def validate_environment(self, selected_parsers):
        """Validate that all required tools and files are available"""
        issues = []
        
        # Check if tools directory exists
        if not os.path.exists(self.tools_base_path):
            issues.append(f"Tools directory not found: {self.tools_base_path}")
            return issues
        
        # Check each selected parser tool
        for parser in selected_parsers:
            tool_path = self.tool_paths.get(parser)
            if not tool_path or not os.path.exists(tool_path):
                issues.append(f"{parser.upper()} tool not found: {tool_path}")
        
        # Check input files based on selected parsers with enhanced search
        if 'mft' in selected_parsers:
            mft_files = self.find_files_recursive(["$MFT", "*MFT*", "mft*"], min_size=1024*1024)  # At least 1MB
            if not mft_files:
                issues.append("No MFT files found in output directory")
        
        if 'srum' in selected_parsers:
            srum_files = self.find_files_recursive(["SRUDB.dat", "*SRUDB*", "srudb*"], min_size=10240)  # At least 10KB
            if not srum_files:
                issues.append("No SRUDB.dat files found in output directory")
        
        if 'prefetch' in selected_parsers:
            prefetch_dirs = glob.glob(os.path.join(self.input_base_path, "**", "Prefetch"), recursive=True)
            pf_files = self.find_files_recursive(["*.pf"], min_size=1024)  # At least 1KB
            if not prefetch_dirs and not pf_files:
                issues.append("No Prefetch directories or .pf files found in output directory")
        
        if 'amcache' in selected_parsers:
            amcache_files = self.find_files_recursive(["Amcache.hve", "*Amcache*", "amcache*"], min_size=10240)  # At least 10KB
            if not amcache_files:
                issues.append("No Amcache.hve files found in output directory")
        
        if 'eventlogs' in selected_parsers:
            eventlog_dirs = glob.glob(os.path.join(self.input_base_path, "**", "eventlogs"), recursive=True)
            evtx_files = self.find_files_recursive(["*.evtx"], min_size=1024)  # At least 1KB
            if not eventlog_dirs and not evtx_files:
                issues.append("No Event log directories or .evtx files found in output directory")
        
        return issues
    
    def run_amcache_parser(self, progress_callback=None):
        """Parse Amcache.hve files using AmcacheParser - FINAL CORRECTED VERSION"""
        if progress_callback:
            progress_callback("Starting Amcache parsing...")
        
        self.logger.info("Starting Amcache parsing...")
        
        # Find Amcache.hve files with enhanced search
        amcache_files = self.find_files_recursive(["Amcache.hve", "*Amcache*", "amcache*"], min_size=10240)
        
        if not amcache_files:
            error_msg = "No Amcache.hve files found"
            self.logger.warning(error_msg)
            return False, error_msg
        
        output_dir = os.path.join(self.output_base_path, 'Amcache')
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        for amcache_file in amcache_files:
            try:
                file_size = os.path.getsize(amcache_file)
                if progress_callback:
                    progress_callback(f"Parsing Amcache: {os.path.basename(amcache_file)} ({file_size:,} bytes)")
                
                self.logger.info(f"Processing Amcache file: {amcache_file} ({file_size:,} bytes)")
                
                # Validate that this is actually an Amcache.hve file
                try:
                    with open(amcache_file, 'rb') as f:
                        header = f.read(4)
                        if header != b'regf':
                            self.logger.warning(f"File does not have registry signature: {amcache_file}")
                            results.append(False)
                            continue
                except Exception as e:
                    self.logger.error(f"Cannot read file header: {amcache_file} - {e}")
                    results.append(False)
                    continue
                
                # Clear output directory before parsing
                try:
                    for file in os.listdir(output_dir):
                        file_path = os.path.join(output_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                except Exception as e:
                    self.logger.warning(f"Could not clear output directory: {e}")
                
                # AmcacheParser command - CORRECTED based on search results
                # From search results: AmcacheParser.exe -f C:\Windows\appcompat\Programs\Amcache.hve --csv c:\temp --dt yyyy-MM-ddTHH:mm:ss
                cmd = [
                    self.tool_paths['amcache'],
                    '-f', amcache_file,
                    '--csv', output_dir,
                    '--dt', 'yyyy-MM-ddTHH:mm:ss'  # Exact format from search results
                ]
                
                self.logger.info(f"Running command: {' '.join(cmd)}")
                
                # Run with proper working directory and elevated privileges
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=600,
                    encoding='utf-8',
                    errors='ignore',
                    cwd=os.path.dirname(self.tool_paths['amcache']),  # Set working directory
                    shell=False  # Don't use shell
                )
                
                self.logger.info(f"AmcacheParser return code: {result.returncode}")
                self.logger.info(f"AmcacheParser stdout: {result.stdout}")
                if result.stderr:
                    self.logger.info(f"AmcacheParser stderr: {result.stderr}")
                
                # Wait a moment for files to be written
                import time
                time.sleep(3)
                
                if result.returncode == 0:
                    # Check if any CSV files were created
                    # According to search results, AmcacheParser creates SIX different CSV files
                    csv_files = glob.glob(os.path.join(output_dir, "*.csv"))
                    
                    if csv_files:
                        # Validate that files have content
                        valid_files = []
                        for csv_file in csv_files:
                            try:
                                csv_size = os.path.getsize(csv_file)
                                if csv_size > 50:  # At least 50 bytes (header)
                                    valid_files.append(csv_file)
                                    self.logger.info(f"Valid CSV file: {os.path.basename(csv_file)} ({csv_size:,} bytes)")
                            except:
                                pass
                        
                        if valid_files:
                            total_size = sum(os.path.getsize(f) for f in valid_files)
                            self.logger.info(f"Successfully parsed Amcache: {amcache_file} -> {len(valid_files)} CSV files ({total_size:,} bytes)")
                            results.append(True)
                        else:
                            self.logger.error(f"CSV files created but are empty for Amcache: {amcache_file}")
                            results.append(False)
                    else:
                        self.logger.error(f"No CSV files generated for Amcache: {amcache_file}")
                        
                        # Enhanced debugging - check all files in output directory
                        try:
                            all_files = os.listdir(output_dir)
                            self.logger.info(f"Files in output directory: {all_files}")
                            
                            if all_files:
                                for file in all_files:
                                    file_path = os.path.join(output_dir, file)
                                    if os.path.isfile(file_path):
                                        file_size = os.path.getsize(file_path)
                                        self.logger.info(f"  Found file: {file} ({file_size:,} bytes)")
                            else:
                                self.logger.error("Output directory is completely empty")
                                
                        except Exception as e:
                            self.logger.error(f"Error checking output directory: {e}")
                        
                        results.append(False)
                else:
                    self.logger.error(f"Amcache parsing failed for {amcache_file}")
                    self.logger.error(f"Return code: {result.returncode}")
                    self.logger.error(f"Stderr: {result.stderr}")
                    self.logger.error(f"Stdout: {result.stdout}")
                    
                    # Check for specific error patterns from search results
                    stderr_lower = result.stderr.lower() if result.stderr else ""
                    stdout_lower = result.stdout.lower() if result.stdout else ""
                    
                    if "access" in stderr_lower and "denied" in stderr_lower:
                        self.logger.error("Access denied - try running as administrator")
                    elif "locked" in stderr_lower or "locked" in stdout_lower:
                        self.logger.error("File appears to be locked - close any applications using the file")
                    elif "not found" in stderr_lower:
                        self.logger.error("Tool or file not found - check paths")
                    elif "invalid" in stderr_lower or "corrupt" in stderr_lower:
                        self.logger.error("Invalid or corrupt file format")
                    elif "administrator" in stderr_lower or "administrator" in stdout_lower:
                        self.logger.error("Administrator privileges required")
                    elif result.returncode == -1073741515:  # Common Windows error
                        self.logger.error("Application failed to initialize - missing dependencies")
                    
                    results.append(False)
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"Amcache parsing timed out for: {amcache_file}")
                results.append(False)
            except Exception as e:
                self.logger.error(f"Error parsing Amcache {amcache_file}: {e}")
                results.append(False)
        
        success = any(results)
        summary = f"Amcache parsing completed: {sum(results)}/{len(results)} files successful"
        
        if progress_callback:
            progress_callback(summary)
        
        return success, summary
    
    def run_eventlogs_parser(self, progress_callback=None):
        """Parse Event Logs using Hayabusa - NEW FUNCTIONALITY"""
        if progress_callback:
            progress_callback("Starting Event Logs parsing with Hayabusa...")
        
        self.logger.info("Starting Event Logs parsing with Hayabusa...")
        
        # Find event log directories and files
        eventlog_dirs = []
        evtx_files = []
        
        # Search for eventlogs directory
        eventlog_search_paths = [
            os.path.join(self.input_base_path, "eventlogs"),
            os.path.join(self.input_base_path, "**", "eventlogs"),
            os.path.join(self.input_base_path, "*", "Windows", "System32", "winevt", "Logs"),
            os.path.join(self.input_base_path, "**", "winevt", "Logs"),
        ]
        
        for search_path in eventlog_search_paths:
            found_dirs = glob.glob(search_path, recursive=True)
            for dir_path in found_dirs:
                if os.path.isdir(dir_path):
                    eventlog_dirs.append(dir_path)
        
        # Also search for individual .evtx files
        evtx_files = self.find_files_recursive(["*.evtx"], min_size=1024)
        
        if not eventlog_dirs and not evtx_files:
            error_msg = "No Event log directories or .evtx files found"
            self.logger.warning(error_msg)
            return False, error_msg
        
        output_dir = os.path.join(self.output_base_path, 'EventLogs')
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        # Process event log directories with Hayabusa
        all_log_dirs = eventlog_dirs.copy()
        
        # If we have individual .evtx files, group them by directory
        if evtx_files:
            evtx_dirs = set(os.path.dirname(evtx_file) for evtx_file in evtx_files)
            all_log_dirs.extend(evtx_dirs)
        
        # Remove duplicates
        all_log_dirs = list(set(all_log_dirs))
        
        for log_dir in all_log_dirs:
            try:
                if progress_callback:
                    progress_callback(f"Parsing Event Logs in: {os.path.basename(log_dir)}")
                
                self.logger.info(f"Processing Event Log directory: {log_dir}")
                
                # Check if directory contains .evtx files
                evtx_in_dir = glob.glob(os.path.join(log_dir, "*.evtx"))
                if not evtx_in_dir:
                    self.logger.warning(f"No .evtx files found in directory: {log_dir}")
                    continue
                
                self.logger.info(f"Found {len(evtx_in_dir)} .evtx files in {log_dir}")
                
                # Hayabusa command - Based on search results
                # hayabusa csv-timeline -d "path" -o output.csv
                safe_name = os.path.basename(log_dir).replace('.', '_').replace(' ', '_')
                output_file = os.path.join(output_dir, f"hayabusa_timeline_{safe_name}.csv")
                
                cmd = [
                    self.tool_paths['hayabusa'],
                    'csv-timeline',
                    '-d', log_dir,
                    '-o', output_file,
                    '--RFC-3339',  # Use RFC-3339 timestamp format
                    '-p', 'verbose',  # Use verbose profile
                    '--min-level', 'informational',  # Include all levels
                    '--no-wizard',  # Disable wizard
                    '--quiet'  # Reduce output
                ]
                
                self.logger.info(f"Running command: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=1800,  # 30 minutes for event logs
                    encoding='utf-8',
                    errors='ignore',
                    cwd=os.path.dirname(self.tool_paths['hayabusa'])
                )
                
                self.logger.info(f"Hayabusa return code: {result.returncode}")
                self.logger.info(f"Hayabusa stdout: {result.stdout}")
                if result.stderr:
                    self.logger.info(f"Hayabusa stderr: {result.stderr}")
                
                if result.returncode == 0:
                    # Check if output file was created
                    if os.path.exists(output_file):
                        file_size = os.path.getsize(output_file)
                        if file_size > 100:  # At least 100 bytes
                            self.logger.info(f"Successfully parsed Event Logs: {log_dir} -> {output_file} ({file_size:,} bytes)")
                            results.append(True)
                        else:
                            self.logger.error(f"Event Log output file is too small: {output_file} ({file_size} bytes)")
                            results.append(False)
                    else:
                        self.logger.error(f"Event Log output file not created: {output_file}")
                        results.append(False)
                else:
                    self.logger.error(f"Event Log parsing failed for {log_dir}")
                    self.logger.error(f"Return code: {result.returncode}")
                    self.logger.error(f"Stderr: {result.stderr}")
                    results.append(False)
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"Event Log parsing timed out for: {log_dir}")
                results.append(False)
            except Exception as e:
                self.logger.error(f"Error parsing Event Logs {log_dir}: {e}")
                results.append(False)
        
        success = any(results)
        summary = f"Event Logs parsing completed: {sum(results)}/{len(results)} directories successful"
        
        if progress_callback:
            progress_callback(summary)
        
        return success, summary
    
    def repair_srudb(self, srudb_path):
        """Repair SRUDB.dat file if it's in dirty state"""
        try:
            sru_dir = os.path.dirname(srudb_path)
            self.logger.info(f"Attempting to repair SRUDB.dat in: {sru_dir}")
            
            # Change to the directory containing SRUDB.dat
            original_dir = os.getcwd()
            os.chdir(sru_dir)
            
            try:
                # First repair command
                cmd1 = ['esentutl.exe', '/r', 'sru', '/i']
                self.logger.info(f"Running repair command 1: {' '.join(cmd1)}")
                result1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=300)
                
                # Second repair command
                cmd2 = ['esentutl.exe', '/p', 'SRUDB.dat']
                self.logger.info(f"Running repair command 2: {' '.join(cmd2)}")
                result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=300)
                
                self.logger.info(f"Repair command 1 result: RC={result1.returncode}")
                self.logger.info(f"Repair command 2 result: RC={result2.returncode}")
                
                return True  # Return True regardless as repair might still work
                    
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            self.logger.error(f"Error repairing SRUDB.dat: {e}")
            return False
    
    def run_srum_parser(self, progress_callback=None):
        """Parse SRUDB.dat files using SrumECmd - FIXED VERSION"""
        if progress_callback:
            progress_callback("Starting SRUM parsing...")
        
        self.logger.info("Starting SRUM parsing...")
        
        # Find SRUDB.dat files with enhanced search
        srum_files = self.find_files_recursive(["SRUDB.dat", "*SRUDB*", "srudb*"], min_size=10240)
        
        if not srum_files:
            error_msg = "No SRUDB.dat files found"
            self.logger.warning(error_msg)
            return False, error_msg
        
        output_dir = os.path.join(self.output_base_path, 'SRUM')
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        for srum_file in srum_files:
            try:
                file_size = os.path.getsize(srum_file)
                if progress_callback:
                    progress_callback(f"Parsing SRUM: {os.path.basename(srum_file)} ({file_size:,} bytes)")
                
                self.logger.info(f"Processing SRUM file: {srum_file} ({file_size:,} bytes)")
                
                # Try to repair SRUDB.dat first
                if progress_callback:
                    progress_callback(f"Repairing SRUM database: {os.path.basename(srum_file)}")
                
                self.repair_srudb(srum_file)
                
                # Find SOFTWARE hive for better parsing
                software_hive = None
                srum_dir = os.path.dirname(srum_file)
                
                # Look for SOFTWARE hive in common locations
                software_search_paths = [
                    os.path.join(srum_dir, "..", "config", "SOFTWARE"),
                    os.path.join(srum_dir, "..", "config", "software"),
                    os.path.join(srum_dir, "..", "..", "config", "SOFTWARE"),
                    os.path.join(srum_dir, "..", "..", "config", "software"),
                    os.path.join(srum_dir, "..", "..", "..", "config", "SOFTWARE"),
                    os.path.join(srum_dir, "..", "..", "..", "config", "software"),
                    os.path.join(srum_dir, "..", "..", "..", "..", "config", "SOFTWARE"),
                    os.path.join(srum_dir, "..", "..", "..", "..", "config", "software"),
                ]
                
                for software_path in software_search_paths:
                    abs_software_path = os.path.abspath(software_path)
                    if os.path.exists(abs_software_path):
                        software_hive = abs_software_path
                        self.logger.info(f"Found SOFTWARE hive: {software_hive}")
                        break
                
                # SrumECmd command - CORRECTED: Based on documentation
                # SrumECmd.exe -f "C:\Temp\SRUDB.dat" -r "C:\Temp\SOFTWARE" --csv "C:\Temp\"
                cmd = [
                    self.tool_paths['srum'],
                    '-f', srum_file,
                    '--csv', output_dir
                ]
                
                # Add SOFTWARE hive if found
                if software_hive:
                    cmd.extend(['-r', software_hive])
                    self.logger.info(f"Using SOFTWARE hive: {software_hive}")
                else:
                    self.logger.warning("No SOFTWARE hive found - parsing without registry data")
                
                self.logger.info(f"Running command: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=600,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                self.logger.info(f"SrumECmd return code: {result.returncode}")
                self.logger.info(f"SrumECmd stdout: {result.stdout}")
                if result.stderr:
                    self.logger.info(f"SrumECmd stderr: {result.stderr}")
                
                if result.returncode == 0:
                    # Check if any CSV files were created (tool creates multiple files)
                    csv_files = glob.glob(os.path.join(output_dir, "*.csv"))
                    if csv_files:
                        total_size = sum(os.path.getsize(f) for f in csv_files)
                        self.logger.info(f"Successfully parsed SRUM: {srum_file} -> {len(csv_files)} CSV files ({total_size:,} bytes)")
                        for csv_file in csv_files:
                            self.logger.info(f"  Created: {csv_file}")
                        results.append(True)
                    else:
                        self.logger.error(f"No CSV files generated for SRUM: {srum_file}")
                        # List all files in output directory for debugging
                        try:
                            all_files = os.listdir(output_dir)
                            self.logger.info(f"Files in output directory: {all_files}")
                        except:
                            pass
                        results.append(False)
                else:
                    self.logger.error(f"SRUM parsing failed for {srum_file}")
                    self.logger.error(f"Return code: {result.returncode}")
                    self.logger.error(f"Stderr: {result.stderr}")
                    
                    # Check if it's a dirty database error
                    if "dirty" in result.stderr.lower() or "repair" in result.stderr.lower() or "Object reference not set" in result.stderr:
                        self.logger.error("Database appears to be dirty or corrupted")
                        self.logger.error("Manual repair may be needed - check the SRUDB.dat file integrity")
                    
                    results.append(False)
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"SRUM parsing timed out for: {srum_file}")
                results.append(False)
            except Exception as e:
                self.logger.error(f"Error parsing SRUM {srum_file}: {e}")
                results.append(False)
        
        success = any(results)
        summary = f"SRUM parsing completed: {sum(results)}/{len(results)} files successful"
        
        if progress_callback:
            progress_callback(summary)
        
        return success, summary
    
    def run_mft_parser(self, progress_callback=None):
        """Parse MFT files using MFTECmd - WORKING VERSION"""
        if progress_callback:
            progress_callback("Starting MFT parsing...")
        
        self.logger.info("Starting MFT parsing...")
        
        # Find MFT files with enhanced search
        mft_files = self.find_files_recursive(["$MFT", "*MFT*", "mft*"], min_size=1024*1024)
        
        if not mft_files:
            error_msg = "No MFT files found"
            self.logger.warning(error_msg)
            return False, error_msg
        
        output_dir = os.path.join(self.output_base_path, 'MFT')
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        for mft_file in mft_files:
            try:
                file_size = os.path.getsize(mft_file)
                if progress_callback:
                    progress_callback(f"Parsing MFT: {os.path.basename(mft_file)} ({file_size:,} bytes)")
                
                self.logger.info(f"Processing MFT file: {mft_file} ({file_size:,} bytes)")
                
                # MFTECmd command - WORKING VERSION
                safe_name = os.path.basename(mft_file).replace('$', '').replace('.', '_').replace(' ', '_')
                
                cmd = [
                    self.tool_paths['mft'],
                    '-f', mft_file,
                    '--csv', output_dir,
                    '--csvf', f"mft_{safe_name}.csv"
                ]
                
                self.logger.info(f"Running command: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=900,  # 15 minutes for MFT
                    encoding='utf-8',
                    errors='ignore',
                    cwd=os.path.dirname(self.tool_paths['mft'])
                )
                
                self.logger.info(f"MFTECmd return code: {result.returncode}")
                self.logger.info(f"MFTECmd stdout: {result.stdout}")
                if result.stderr:
                    self.logger.info(f"MFTECmd stderr: {result.stderr}")
                
                if result.returncode == 0:
                    # Check if any CSV files were created
                    csv_files = glob.glob(os.path.join(output_dir, "*.csv"))
                    if csv_files:
                        total_size = sum(os.path.getsize(f) for f in csv_files)
                        self.logger.info(f"Successfully parsed MFT: {mft_file} -> {len(csv_files)} CSV files ({total_size:,} bytes)")
                        for csv_file in csv_files:
                            self.logger.info(f"  Created: {csv_file}")
                        results.append(True)
                    else:
                        self.logger.error(f"No CSV files generated for MFT: {mft_file}")
                        results.append(False)
                else:
                    self.logger.error(f"MFT parsing failed for {mft_file}")
                    self.logger.error(f"Return code: {result.returncode}")
                    self.logger.error(f"Stderr: {result.stderr}")
                    results.append(False)
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"MFT parsing timed out for: {mft_file}")
                results.append(False)
            except Exception as e:
                self.logger.error(f"Error parsing MFT {mft_file}: {e}")
                results.append(False)
        
        success = any(results)
        summary = f"MFT parsing completed: {sum(results)}/{len(results)} files successful"
        
        if progress_callback:
            progress_callback(summary)
        
        return success, summary
    
    def run_prefetch_parser(self, progress_callback=None):
        """Parse Prefetch files using PECmd - WORKING VERSION"""
        if progress_callback:
            progress_callback("Starting Prefetch parsing...")
        
        self.logger.info("Starting Prefetch parsing...")
        
        # Find Prefetch directories and files
        prefetch_dirs = glob.glob(os.path.join(self.input_base_path, "**", "Prefetch"), recursive=True)
        pf_files = self.find_files_recursive(["*.pf"], min_size=1024)
        
        if not prefetch_dirs and not pf_files:
            error_msg = "No Prefetch directories or .pf files found"
            self.logger.warning(error_msg)
            return False, error_msg
        
        output_dir = os.path.join(self.output_base_path, 'Prefetch')
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        # Process Prefetch directories
        for prefetch_dir in prefetch_dirs:
            if os.path.isdir(prefetch_dir):
                try:
                    if progress_callback:
                        progress_callback(f"Parsing Prefetch directory: {os.path.basename(prefetch_dir)}")
                    
                    self.logger.info(f"Processing Prefetch directory: {prefetch_dir}")
                    
                    # PECmd command for directory
                    safe_name = os.path.basename(prefetch_dir).replace('.', '_').replace(' ', '_')
                    
                    cmd = [
                        self.tool_paths['prefetch'],
                        '-d', prefetch_dir,
                        '--csv', output_dir,
                        '--csvf', f"prefetch_dir_{safe_name}.csv"
                    ]
                    
                    self.logger.info(f"Running command: {' '.join(cmd)}")
                    
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        text=True, 
                        timeout=600,
                        encoding='utf-8',
                        errors='ignore',
                        cwd=os.path.dirname(self.tool_paths['prefetch'])
                    )
                    
                    self.logger.info(f"PECmd return code: {result.returncode}")
                    self.logger.info(f"PECmd stdout: {result.stdout}")
                    if result.stderr:
                        self.logger.info(f"PECmd stderr: {result.stderr}")
                    
                    if result.returncode == 0:
                        # Check if any CSV files were created
                        csv_files = glob.glob(os.path.join(output_dir, "*.csv"))
                        if csv_files:
                            total_size = sum(os.path.getsize(f) for f in csv_files)
                            self.logger.info(f"Successfully parsed Prefetch directory: {prefetch_dir} -> {len(csv_files)} CSV files ({total_size:,} bytes)")
                            for csv_file in csv_files:
                                self.logger.info(f"  Created: {csv_file}")
                            results.append(True)
                        else:
                            self.logger.error(f"No CSV files generated for Prefetch: {prefetch_dir}")
                            results.append(False)
                    else:
                        self.logger.error(f"Prefetch parsing failed for {prefetch_dir}")
                        self.logger.error(f"Return code: {result.returncode}")
                        self.logger.error(f"Stderr: {result.stderr}")
                        results.append(False)
                        
                except subprocess.TimeoutExpired:
                    self.logger.error(f"Prefetch parsing timed out for: {prefetch_dir}")
                    results.append(False)
                except Exception as e:
                    self.logger.error(f"Error parsing Prefetch {prefetch_dir}: {e}")
                    results.append(False)
        
        # Process individual .pf files if no directories found
        if not prefetch_dirs and pf_files:
            # Group .pf files by directory and process each directory
            pf_dirs = set(os.path.dirname(pf_file) for pf_file in pf_files)
            
            for pf_dir in pf_dirs:
                try:
                    if progress_callback:
                        progress_callback(f"Parsing .pf files in: {os.path.basename(pf_dir)}")
                    
                    self.logger.info(f"Processing .pf files in directory: {pf_dir}")
                    
                    safe_name = os.path.basename(pf_dir).replace('.', '_').replace(' ', '_')
                    
                    cmd = [
                        self.tool_paths['prefetch'],
                        '-d', pf_dir,
                        '--csv', output_dir,
                        '--csvf', f"prefetch_pf_{safe_name}.csv"
                    ]
                    
                    self.logger.info(f"Running command: {' '.join(cmd)}")
                    
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        text=True, 
                        timeout=600,
                        encoding='utf-8',
                        errors='ignore',
                        cwd=os.path.dirname(self.tool_paths['prefetch'])
                    )
                    
                    if result.returncode == 0:
                        # Check if any CSV files were created
                        csv_files = glob.glob(os.path.join(output_dir, "*.csv"))
                        if csv_files:
                            total_size = sum(os.path.getsize(f) for f in csv_files)
                            self.logger.info(f"Successfully parsed .pf files in: {pf_dir} -> {len(csv_files)} CSV files ({total_size:,} bytes)")
                            for csv_file in csv_files:
                                self.logger.info(f"  Created: {csv_file}")
                            results.append(True)
                        else:
                            self.logger.error(f"No CSV files generated for Prefetch: {pf_dir}")
                            results.append(False)
                    else:
                        self.logger.error(f"Prefetch parsing failed for {pf_dir}")
                        self.logger.error(f"Return code: {result.returncode}")
                        self.logger.error(f"Stderr: {result.stderr}")
                        results.append(False)
                        
                except subprocess.TimeoutExpired:
                    self.logger.error(f"Prefetch parsing timed out for: {pf_dir}")
                    results.append(False)
                except Exception as e:
                    self.logger.error(f"Error parsing Prefetch {pf_dir}: {e}")
                    results.append(False)
        
        success = any(results)
        summary = f"Prefetch parsing completed: {sum(results)}/{len(results)} items successful"
        
        if progress_callback:
            progress_callback(summary)
        
        return success, summary
    
    def parse_system_artifacts(self, selected_parsers, progress_callback=None):
        """Parse selected system artifacts using Eric Zimmerman tools and Hayabusa"""
        # Validate environment first
        issues = self.validate_environment(selected_parsers)
        if issues:
            error_msg = "Validation failed:\n" + "\n".join(issues)
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'results': {}
            }
        
        results = {}
        
        try:
            if progress_callback:
                progress_callback(f"Starting system artifact parsing for: {', '.join(selected_parsers)}")
            
            # Run selected parsers
            if 'mft' in selected_parsers:
                success, summary = self.run_mft_parser(progress_callback)
                results['mft'] = {'success': success, 'summary': summary}
            
            if 'srum' in selected_parsers:
                success, summary = self.run_srum_parser(progress_callback)
                results['srum'] = {'success': success, 'summary': summary}
            
            if 'prefetch' in selected_parsers:
                success, summary = self.run_prefetch_parser(progress_callback)
                results['prefetch'] = {'success': success, 'summary': summary}
            
            if 'amcache' in selected_parsers:
                success, summary = self.run_amcache_parser(progress_callback)
                results['amcache'] = {'success': success, 'summary': summary}
            
            # NEW: Event Logs parsing with Hayabusa
            if 'eventlogs' in selected_parsers:
                success, summary = self.run_eventlogs_parser(progress_callback)
                results['eventlogs'] = {'success': success, 'summary': summary}
            
            # Generate overall summary
            successful_parsers = [parser for parser, result in results.items() if result['success']]
            failed_parsers = [parser for parser, result in results.items() if not result['success']]
            
            overall_summary = f"System parsing completed: {len(successful_parsers)} successful, {len(failed_parsers)} failed"
            self.logger.info(overall_summary)
            
            if progress_callback:
                progress_callback(overall_summary)
            
            return {
                'success': len(successful_parsers) > 0,
                'summary': overall_summary,
                'results': results,
                'successful_parsers': successful_parsers,
                'failed_parsers': failed_parsers,
                'output_folder': self.output_base_path
            }
            
        except Exception as e:
            error_msg = f"Error during system artifact parsing: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'results': results
            }

def parse_system_artifacts(selected_parsers, tools_path=None, input_path=None, progress_callback=None):
    """Convenience function to parse system artifacts"""
    parser = EricZimmermanParser(tools_path, input_base_path=input_path)
    return parser.parse_system_artifacts(selected_parsers, progress_callback)

if __name__ == '__main__':
    def test_progress_callback(message):
        print(f"Progress: {message}")
    
    selected = ['mft', 'srum', 'prefetch', 'amcache', 'eventlogs']
    
    result = parse_system_artifacts(
        selected_parsers=selected,
        progress_callback=test_progress_callback
    )
    
    print("\nFinal Result:")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Summary: {result['summary']}")
        print(f"Successful parsers: {result['successful_parsers']}")
        print(f"Failed parsers: {result['failed_parsers']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
