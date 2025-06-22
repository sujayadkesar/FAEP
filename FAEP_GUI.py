# import sys
# import os
# import logging
# import threading
# import sqlite3
# import json
# from datetime import datetime
# from PyQt5.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
#     QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QTreeWidget,
#     QTreeWidgetItem, QTabWidget, QProgressBar, QCheckBox, QGroupBox,
#     QSplitter, QFrame, QScrollArea, QFileDialog, QMessageBox, QComboBox,
#     QTableWidget, QTableWidgetItem, QStatusBar, QMenuBar, QAction,
#     QToolBar, QHeaderView, QListWidget, QListWidgetItem, QSpacerItem, QSizePolicy
# )
# from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
# from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap
# from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QScrollArea, QWidget
# from main import setup_database

# # Import your existing functions
# try:
#     from main import (
#         open_db, create_table, bulk_insert, EWFImgInfo, list_directory_tree,
#         extract_chrome_directory, extract_directory, extract_edge_directory,
#         extract_event_logs, extract_registry_hives, extract_sru_mft_pagefile,
#         extract_powershell_console_history, extract_prefetch_files, extract_activitiesCache_db
#     )
# except ImportError:
#     print("Warning: Main module functions not available")

# # Import parser functions
# try:
#     from registry_parser import parse_registry_artifacts
# except ImportError:
#     print("Warning: Registry parser not available")
#     parse_registry_artifacts = None

# try:
#     from browser_parser import parse_browser_artifacts
# except ImportError:
#     print("Warning: Browser parser not available")
#     parse_browser_artifacts = None

# try:
#     from mft_amcache_pf_sru_parser import parse_system_artifacts
# except ImportError:
#     print("Warning: System artifacts parser not available")
#     parse_system_artifacts = None

# try:
#     import pytsk3
#     import pyewf
#     import psycopg2
#     FORENSIC_LIBS_AVAILABLE = True
# except ImportError:
#     FORENSIC_LIBS_AVAILABLE = False
#     print("Warning: Forensic libraries not available")

# class CaseManager:
#     """Case management system for forensic investigations"""
    
#     def __init__(self):
#         self.case_file = "case_config.json"
#         self.current_case = None
        
#     def create_case(self, case_name, image_path, investigator=""):
#         """Create a new case"""
#         case_data = {
#             'case_name': case_name,
#             'image_path': image_path,
#             'investigator': investigator,
#             'created_date': datetime.now().isoformat(),
#             'last_modified': datetime.now().isoformat(),
#             'status': 'created',
#             'workflow_stage': 0,
#             'partitions': [],
#             'selected_partition': None,
#             'extracted_artifacts': [],
#             'parsed_artifacts': []
#         }
        
#         with open(self.case_file, 'w') as f:
#             json.dump(case_data, f, indent=4)
        
#         self.current_case = case_data
#         return case_data
    
#     def load_case(self):
#         """Load existing case"""
#         if os.path.exists(self.case_file):
#             try:
#                 with open(self.case_file, 'r') as f:
#                     self.current_case = json.load(f)
#                 return self.current_case
#             except Exception as e:
#                 print(f"Error loading case: {e}")
#                 return None
#         return None
    
#     def save_case(self):
#         """Save current case"""
#         if self.current_case:
#             self.current_case['last_modified'] = datetime.now().isoformat()
#             with open(self.case_file, 'w') as f:
#                 json.dump(self.current_case, f, indent=4)
    
#     def update_case_status(self, status, workflow_stage=None):
#         """Update case status"""
#         if self.current_case:
#             self.current_case['status'] = status
#             if workflow_stage is not None:
#                 self.current_case['workflow_stage'] = workflow_stage
#             self.save_case()
    
#     def set_partitions(self, partitions):
#         """Set partitions for the case (remove non-serializable objects)"""
#         if self.current_case:
#             # Create serializable partition data
#             serializable_partitions = []
#             for partition in partitions:
#                 serializable_partition = {
#                     'addr': partition['addr'],
#                     'start': partition['start'],
#                     'length': partition['length'],
#                     'description': partition['description'],
#                     'size_mb': partition['size_mb']
#                     # Note: We don't save 'partition_obj' as it's not JSON serializable
#                 }
#                 serializable_partitions.append(serializable_partition)
            
#             self.current_case['partitions'] = serializable_partitions
#             self.save_case()
    
#     def set_selected_partition(self, partition):
#         """Set selected partition (remove non-serializable objects)"""
#         if self.current_case:
#             # Create serializable partition data
#             serializable_partition = {
#                 'addr': partition['addr'],
#                 'start': partition['start'],
#                 'length': partition['length'],
#                 'description': partition['description'],
#                 'size_mb': partition['size_mb']
#             }
#             self.current_case['selected_partition'] = serializable_partition
#             self.save_case()
    
#     def add_extracted_artifact(self, artifact):
#         """Add extracted artifact"""
#         if self.current_case:
#             if 'extracted_artifacts' not in self.current_case:
#                 self.current_case['extracted_artifacts'] = []
#             self.current_case['extracted_artifacts'].append(artifact)
#             self.save_case()
    
#     def add_parsed_artifact(self, artifact):
#         """Add parsed artifact"""
#         if self.current_case:
#             if 'parsed_artifacts' not in self.current_case:
#                 self.current_case['parsed_artifacts'] = []
#             self.current_case['parsed_artifacts'].append(artifact)
#             self.save_case()

# class DatabaseConnectionThread(QThread):
#     """Thread for testing database connection"""
#     connection_result = pyqtSignal(bool, str)
    
#     def run(self):
#         try:
#             logging.info("Testing database connection...")
#             conn = open_db()
#             if conn:
#                 logging.info("Connection successful")
                
#                 with conn.cursor() as cursor:
#                     cursor.execute("SELECT version()")
#                     version = cursor.fetchone()[0]
#                     logging.info(f"PostgreSQL version: {version}")
                    
#                     # Test table creation
#                     create_table(conn)
#                     logging.info("Table creation successful")
                    
#                     # Test insertion
#                     test_record = [("/test_path", "test_file", "File", 0, None, None, None, "/")]
#                     logging.info("Testing record insertion...")
#                     bulk_insert(conn, test_record)
                    
#                     # Verify insertion
#                     cursor.execute("SELECT COUNT(*) FROM file_tree WHERE path = '/test_path'")
#                     count = cursor.fetchone()[0]
#                     logging.info(f"Test record found in database: {count > 0}")
                    
#                 conn.close()
#                 logging.info("Database test complete")
#                 self.connection_result.emit(True, "Database connection successful")
#             else:
#                 self.connection_result.emit(False, "Failed to connect to database")
#         except Exception as e:
#             logging.error(f"Database test failed: {str(e)}")
#             self.connection_result.emit(False, f"Database Error: {str(e)}")

# class ImageLoadingThread(QThread):
#     """Thread for loading evidence image"""
#     progress_update = pyqtSignal(str)
#     partitions_found = pyqtSignal(list)
#     loading_complete = pyqtSignal(bool, str)
    
#     def __init__(self, image_path):
#         super().__init__()
#         self.image_path = image_path
        
#     def run(self):
#         try:
#             if not FORENSIC_LIBS_AVAILABLE:
#                 self.loading_complete.emit(False, "Forensic libraries (pytsk3, pyewf) not available")
#                 return
                
#             self.progress_update.emit("Processing image...\nThis may take several minutes.")
            
#             # Validate file exists
#             if not os.path.exists(self.image_path):
#                 self.loading_complete.emit(False, f"File does not exist: {self.image_path}")
#                 return
            
#             logging.info(f"Processing image: {self.image_path}")
            
#             # Open EWF image
#             image_path = os.path.normpath(self.image_path)
#             filenames = pyewf.glob(image_path)
#             ewf_handle = pyewf.handle()
#             ewf_handle.open(filenames)
#             img_info = EWFImgInfo(ewf_handle)
#             logging.info("Image opened successfully")
            
#             self.progress_update.emit("Analyzing partition table...")
            
#             try:
#                 volume = pytsk3.Volume_Info(img_info)
#                 partitions = []
                
#                 for part in volume:
#                     desc = part.desc.decode('utf-8', 'ignore') if part.desc else "Unknown"
#                     part_info = {
#                         'addr': part.addr,
#                         'start': part.start,
#                         'length': part.len,
#                         'description': desc,
#                         'size_mb': (part.len * 512) // (1024 * 1024),
#                         'partition_obj': part  # Keep this for runtime use, but don't serialize
#                     }
#                     partitions.append(part_info)
#                     logging.info(f"Found partition {part.addr}: {desc}")
                
#                 if partitions:
#                     self.img_info = img_info
#                     self.partitions_found.emit(partitions)
#                     self.loading_complete.emit(True, "Image loaded successfully")
#                 else:
#                     self.loading_complete.emit(False, "No partitions found in the image.")
                    
#             except Exception as e:
#                 self.loading_complete.emit(False, f"Error processing volume: {str(e)}")
#                 logging.error(f"Error processing volume: {str(e)}")
                
#         except Exception as e:
#             self.loading_complete.emit(False, f"Error processing image: {str(e)}")
#             logging.error(f"Error processing image: {str(e)}")

# class FileSystemScanThread(QThread):
#     """Thread for scanning file system"""
#     progress_update = pyqtSignal(str)
#     scan_complete = pyqtSignal(bool, str, dict)
    
#     def __init__(self, img_info, partition, db_conn):
#         super().__init__()
#         self.img_info = img_info
#         self.partition = partition
#         self.db_conn = db_conn
        
#     def run(self):
#         try:
#             self.progress_update.emit(f"Initializing file system at offset {self.partition['start'] * 512}")
            
#             # Initialize file system information
#             fs_info = pytsk3.FS_Info(self.img_info, offset=self.partition['start'] * 512)
#             root_dir = fs_info.open_dir(path="/")
            
#             # List root directory contents
#             root_content = "\nRoot directory contents:\n"
#             for entry in root_dir:
#                 try:
#                     name = entry.info.name.name.decode('utf-8', errors='replace')
#                     root_content += f"- {name}\n"
#                 except Exception:
#                     continue
            
#             self.progress_update.emit(root_content)
            
#             # Scan the entire file system
#             self.progress_update.emit("Scanning file system...\nThis may take several minutes.")
            
#             logging.info("Starting full file system scan...")
#             counts, records = list_directory_tree(fs_info, root_dir, "/")
#             logging.info(f"Scan complete: Found {counts['directories']} directories and {counts['files']} files")
            
#             # Insert records into database
#             logging.info(f"Inserting {len(records)} records into database...")
#             bulk_insert(self.db_conn, records)
#             logging.info("Database insertion complete")
            
#             result_info = {
#                 'fs_info': fs_info,
#                 'counts': counts,
#                 'records_count': len(records)
#             }
            
#             self.scan_complete.emit(True, f"Scan complete!\n\nFound {counts['directories']} directories and {counts['files']} files", result_info)
            
#         except Exception as e:
#             self.scan_complete.emit(False, f"Error scanning file system: {str(e)}", {})
#             logging.error(f"Error scanning file system: {str(e)}")

# class ArtifactExtractionThread(QThread):
#     """Thread for extracting artifacts"""
#     progress_update = pyqtSignal(str)
#     extraction_complete = pyqtSignal(bool, str, list)
    
#     def __init__(self, fs_info, db_conn, selected_options):
#         super().__init__()
#         self.fs_info = fs_info
#         self.db_conn = db_conn
#         self.selected_options = selected_options
        
#     def run(self):
#         try:
#             results = []
            
#             for option in self.selected_options:
#                 if option == "1":  # Registry Hives
#                     self.progress_update.emit("Extracting Registry Hives...")
#                     reg_out = os.path.join("output", "registry")
#                     result = extract_registry_hives(self.fs_info, self.db_conn, reg_out)
#                     results.append(("Registry hives", result))
                    
#                 elif option == "2":  # Event Logs
#                     self.progress_update.emit("Extracting Event Logs...")
#                     logs_output = os.path.join("output", "eventlogs")
#                     result = extract_event_logs(self.fs_info, self.db_conn, logs_output)
#                     results.append(("Event logs", result))
                    
#                 elif option == "3":  # Edge
#                     self.progress_update.emit("Extracting Edge Browser Data...")
#                     edge_output = os.path.join("output", "browser", "edge")
#                     result = extract_edge_directory(self.fs_info, self.db_conn, edge_output)
#                     results.append(("Edge browser", result))
                    
#                 elif option == "4":  # Chrome
#                     self.progress_update.emit("Extracting Chrome Browser Data...")
#                     chrome_out = os.path.join("output", "browser", "chrome")
#                     result = extract_chrome_directory(self.fs_info, self.db_conn, chrome_out)
#                     results.append(("Chrome browser", result))
                    
#                 elif option == "5":  # MFT, Pagefile, SRUDB
#                     self.progress_update.emit("Extracting MFT, Pagefile, SRUDB...")
#                     mft_output = "output"
#                     result = extract_sru_mft_pagefile(self.fs_info, self.db_conn, mft_output)
#                     results.append(("MFT/Pagefile/SRUDB", result))
                    
#                 elif option == "6":  # PowerShell History
#                     self.progress_update.emit("Extracting PowerShell Console History...")
#                     consolehistory_output = "output"
#                     result = extract_powershell_console_history(self.fs_info, self.db_conn, consolehistory_output)
#                     results.append(("PowerShell history", result))
                    
#                 elif option == "7":  # Prefetch Files
#                     self.progress_update.emit("Extracting Prefetch Files...")
#                     prefetch_output = "output"
#                     result = extract_prefetch_files(self.fs_info, self.db_conn, prefetch_output)
#                     results.append(("Prefetch files", result))
                    
#                 elif option == "8":  # ActivityCache.db
#                     self.progress_update.emit("Extracting ActivityCache.db...")
#                     activecache_output = "output"
#                     result = extract_activitiesCache_db(self.fs_info, self.db_conn, activecache_output)
#                     results.append(("ActivityCache.db", result))
            
#             self.extraction_complete.emit(True, "Artifact extraction completed", results)
            
#         except Exception as e:
#             self.extraction_complete.emit(False, f"Extraction failed: {str(e)}", [])

# class ParsingThread(QThread):
#     """Enhanced thread for parsing artifacts with proper parser integration"""
#     progress_update = pyqtSignal(str)
#     parsing_complete = pyqtSignal(bool, str, list)
    
#     def __init__(self, selected_parsers):
#         super().__init__()
#         self.selected_parsers = selected_parsers
        
#     def run(self):
#         try:
#             results = []
#             overall_success = True
            
#             self.progress_update.emit(f"Starting parsing with selected parsers: {', '.join(self.selected_parsers)}")
            
#             # Registry Parser
#             if 'registry' in self.selected_parsers:
#                 try:
#                     self.progress_update.emit("Starting Registry parsing...")
                    
#                     if parse_registry_artifacts is None:
#                         raise ImportError("Registry parser not available")
                    
#                     result = parse_registry_artifacts(
#                         registry_folder="output/registry",
#                         progress_callback=self.progress_update.emit
#                     )
                    
#                     if result['success']:
#                         results.append(('registry', True, result['summary']))
#                         self.progress_update.emit(f"[SUCCESS] Registry parsing completed: {result['summary']}")
#                     else:
#                         results.append(('registry', False, result.get('error', 'Unknown error')))
#                         self.progress_update.emit(f"[FAILED] Registry parsing failed: {result.get('error', 'Unknown error')}")
#                         overall_success = False
                        
#                 except Exception as e:
#                     error_msg = f"Registry parsing error: {str(e)}"
#                     results.append(('registry', False, error_msg))
#                     self.progress_update.emit(f"[FAILED] {error_msg}")
#                     overall_success = False
            
#             # Browser Parser
#             if 'browser' in self.selected_parsers:
#                 try:
#                     self.progress_update.emit("Starting Browser parsing...")
                    
#                     if parse_browser_artifacts is None:
#                         raise ImportError("Browser parser not available")
                    
#                     result = parse_browser_artifacts(
#                         browser_folder="output/browser",
#                         progress_callback=self.progress_update.emit
#                     )
                    
#                     if result['success']:
#                         results.append(('browser', True, result['summary']))
#                         self.progress_update.emit(f"[SUCCESS] Browser parsing completed: {result['summary']}")
#                     else:
#                         results.append(('browser', False, result.get('error', 'Unknown error')))
#                         self.progress_update.emit(f"[FAILED] Browser parsing failed: {result.get('error', 'Unknown error')}")
#                         overall_success = False
                        
#                 except Exception as e:
#                     error_msg = f"Browser parsing error: {str(e)}"
#                     results.append(('browser', False, error_msg))
#                     self.progress_update.emit(f"[FAILED] {error_msg}")
#                     overall_success = False
            
#             # System Artifacts Parser (MFT, Amcache, Prefetch, SRUM)
#             system_parsers = []
#             if 'mft' in self.selected_parsers:
#                 system_parsers.append('mft')
#             if 'prefetch' in self.selected_parsers:
#                 system_parsers.append('prefetch')
#             if 'activities' in self.selected_parsers:  # This maps to amcache
#                 system_parsers.append('amcache')
#             if 'eventlogs' in self.selected_parsers:  # This maps to srum
#                 system_parsers.append('srum')
            
#             if system_parsers:
#                 try:
#                     self.progress_update.emit(f"Starting System artifacts parsing: {', '.join(system_parsers)}")
                    
#                     if parse_system_artifacts is None:
#                         raise ImportError("System artifacts parser not available")
                    
#                     result = parse_system_artifacts(
#                         selected_parsers=system_parsers,
#                         input_path="output",
#                         progress_callback=self.progress_update.emit
#                     )
                    
#                     if result['success']:
#                         # Add individual results for each system parser
#                         for parser in system_parsers:
#                             if parser in result['results']:
#                                 parser_result = result['results'][parser]
#                                 results.append((parser, parser_result['success'], parser_result['summary']))
#                                 status = "[SUCCESS]" if parser_result['success'] else "[FAILED]"
#                                 self.progress_update.emit(f"{status} {parser.upper()} parsing: {parser_result['summary']}")
#                     else:
#                         for parser in system_parsers:
#                             results.append((parser, False, result.get('error', 'Unknown error')))
#                             self.progress_update.emit(f"[FAILED] {parser.upper()} parsing failed: {result.get('error', 'Unknown error')}")
#                         overall_success = False
                        
#                 except Exception as e:
#                     error_msg = f"System artifacts parsing error: {str(e)}"
#                     for parser in system_parsers:
#                         results.append((parser, False, error_msg))
#                         self.progress_update.emit(f"[FAILED] {parser.upper()} parsing error: {str(e)}")
#                     overall_success = False
            
#             # PowerShell Parser (if selected separately)
#             if 'powershell' in self.selected_parsers:
#                 try:
#                     self.progress_update.emit("Starting PowerShell history parsing...")
                    
#                     # For now, we'll add a placeholder since PowerShell parsing might be part of system artifacts
#                     # You can implement a separate PowerShell parser if needed
#                     results.append(('powershell', True, 'PowerShell parsing completed (placeholder)'))
#                     self.progress_update.emit("[SUCCESS] PowerShell parsing completed")
                    
#                 except Exception as e:
#                     error_msg = f"PowerShell parsing error: {str(e)}"
#                     results.append(('powershell', False, error_msg))
#                     self.progress_update.emit(f"[FAILED] {error_msg}")
#                     overall_success = False
            
#             # Generate final summary
#             successful_count = sum(1 for _, success, _ in results if success)
#             total_count = len(results)
            
#             final_message = f"Parsing completed: {successful_count}/{total_count} parsers successful"
#             self.progress_update.emit(final_message)
            
#             self.parsing_complete.emit(overall_success, final_message, results)
            
#         except Exception as e:
#             error_msg = f"Parsing failed: {str(e)}"
#             self.progress_update.emit(error_msg)
#             self.parsing_complete.emit(False, error_msg, [])

# class AutoProcessingThread(QThread):
#     """Thread for automatic processing of everything"""
#     progress_update = pyqtSignal(str)
#     processing_complete = pyqtSignal(bool, str)
    
#     def __init__(self, img_info, partition, db_conn, fs_info):
#         super().__init__()
#         self.img_info = img_info
#         self.partition = partition
#         self.db_conn = db_conn
#         self.fs_info = fs_info
        
#     def run(self):
#         try:
#             self.progress_update.emit("Starting automatic processing...")
            
#             # Extract all artifacts
#             self.progress_update.emit("Extracting all artifacts...")
#             all_artifacts = ["1", "2", "3", "4", "5", "6", "7", "8"]
            
#             extraction_results = []
#             for option in all_artifacts:
#                 try:
#                     if option == "1":  # Registry Hives
#                         self.progress_update.emit("Auto-extracting Registry Hives...")
#                         reg_out = os.path.join("output", "registry")
#                         result = extract_registry_hives(self.fs_info, self.db_conn, reg_out)
#                         extraction_results.append(("Registry hives", result))
                        
#                     elif option == "2":  # Event Logs
#                         self.progress_update.emit("Auto-extracting Event Logs...")
#                         logs_output = os.path.join("output", "eventlogs")
#                         result = extract_event_logs(self.fs_info, self.db_conn, logs_output)
#                         extraction_results.append(("Event logs", result))
                        
#                     elif option == "3":  # Edge
#                         self.progress_update.emit("Auto-extracting Edge Browser Data...")
#                         edge_output = os.path.join("output", "browser", "edge")
#                         result = extract_edge_directory(self.fs_info, self.db_conn, edge_output)
#                         extraction_results.append(("Edge browser", result))
                        
#                     elif option == "4":  # Chrome
#                         self.progress_update.emit("Auto-extracting Chrome Browser Data...")
#                         chrome_out = os.path.join("output", "browser", "chrome")
#                         result = extract_chrome_directory(self.fs_info, self.db_conn, chrome_out)
#                         extraction_results.append(("Chrome browser", result))
                        
#                     elif option == "5":  # MFT, Pagefile, SRUDB
#                         self.progress_update.emit("Auto-extracting MFT, Pagefile, SRUDB...")
#                         mft_output = "output"
#                         result = extract_sru_mft_pagefile(self.fs_info, self.db_conn, mft_output)
#                         extraction_results.append(("MFT/Pagefile/SRUDB", result))
                        
#                     elif option == "6":  # PowerShell History
#                         self.progress_update.emit("Auto-extracting PowerShell Console History...")
#                         consolehistory_output = "output"
#                         result = extract_powershell_console_history(self.fs_info, self.db_conn, consolehistory_output)
#                         extraction_results.append(("PowerShell history", result))
                        
#                     elif option == "7":  # Prefetch Files
#                         self.progress_update.emit("Auto-extracting Prefetch Files...")
#                         prefetch_output = "output"
#                         result = extract_prefetch_files(self.fs_info, self.db_conn, prefetch_output)
#                         extraction_results.append(("Prefetch files", result))
                        
#                     elif option == "8":  # ActivityCache.db
#                         self.progress_update.emit("Auto-extracting ActivityCache.db...")
#                         activecache_output = "output"
#                         result = extract_activitiesCache_db(self.fs_info, self.db_conn, activecache_output)
#                         extraction_results.append(("ActivityCache.db", result))
                        
#                 except Exception as e:
#                     self.progress_update.emit(f"Error extracting {option}: {str(e)}")
            
#             # Parse all artifacts
#             self.progress_update.emit("Parsing all artifacts...")
#             all_parsers = ['registry', 'browser', 'mft', 'prefetch', 'activities', 'eventlogs']
            
#             parsing_results = []
            
#             # Registry Parser
#             if parse_registry_artifacts is not None:
#                 try:
#                     self.progress_update.emit("Auto-parsing Registry...")
#                     result = parse_registry_artifacts(
#                         registry_folder="output/registry",
#                         progress_callback=self.progress_update.emit
#                     )
#                     if result['success']:
#                         parsing_results.append(('registry', True, result['summary']))
#                     else:
#                         parsing_results.append(('registry', False, result.get('error', 'Unknown error')))
#                 except Exception as e:
#                     parsing_results.append(('registry', False, str(e)))
            
#             # Browser Parser
#             if parse_browser_artifacts is not None:
#                 try:
#                     self.progress_update.emit("Auto-parsing Browser...")
#                     result = parse_browser_artifacts(
#                         browser_folder="output/browser",
#                         progress_callback=self.progress_update.emit
#                     )
#                     if result['success']:
#                         parsing_results.append(('browser', True, result['summary']))
#                     else:
#                         parsing_results.append(('browser', False, result.get('error', 'Unknown error')))
#                 except Exception as e:
#                     parsing_results.append(('browser', False, str(e)))
            
#             # System Artifacts Parser
#             if parse_system_artifacts is not None:
#                 try:
#                     self.progress_update.emit("Auto-parsing System Artifacts...")
#                     system_parsers = ['mft', 'srum', 'prefetch', 'amcache']
#                     result = parse_system_artifacts(
#                         selected_parsers=system_parsers,
#                         input_path="output",
#                         progress_callback=self.progress_update.emit
#                     )
                    
#                     if result['success']:
#                         for parser in system_parsers:
#                             if parser in result['results']:
#                                 parser_result = result['results'][parser]
#                                 parsing_results.append((parser, parser_result['success'], parser_result['summary']))
#                     else:
#                         for parser in system_parsers:
#                             parsing_results.append((parser, False, result.get('error', 'Unknown error')))
#                 except Exception as e:
#                     for parser in ['mft', 'srum', 'prefetch', 'amcache']:
#                         parsing_results.append((parser, False, str(e)))
            
#             # Generate summary
#             extraction_success = sum(1 for _, success in extraction_results if success)
#             parsing_success = sum(1 for _, success, _ in parsing_results if success)
            
#             summary = f"Auto-processing completed!\nExtracted: {extraction_success}/{len(extraction_results)} artifacts\nParsed: {parsing_success}/{len(parsing_results)} parsers"
            
#             self.processing_complete.emit(True, summary)
            
#         except Exception as e:
#             self.processing_complete.emit(False, f"Auto-processing failed: {str(e)}")

# class WorkflowStepWidget(QFrame):
#     """Custom widget for workflow steps"""
#     def __init__(self, step_number, title, description, parent=None):
#         super().__init__(parent)
#         self.step_number = step_number
#         self.title = title
#         self.description = description
#         self.is_active = False
#         self.is_completed = False
#         self.init_ui()
        
#     def init_ui(self):
#         self.setFrameStyle(QFrame.StyledPanel)
#         layout = QHBoxLayout(self)
        
#         # Step number circle
#         self.step_label = QLabel(str(self.step_number))
#         self.step_label.setFixedSize(40, 40)
#         self.step_label.setAlignment(Qt.AlignCenter)
#         self.step_label.setStyleSheet("""
#             QLabel {
#                 background-color: #e9ecef;
#                 color: #6c757d;
#                 border-radius: 20px;
#                 font-weight: bold;
#                 font-size: 16px;
#             }
#         """)
        
#         # Step content
#         content_layout = QVBoxLayout()
#         self.title_label = QLabel(self.title)
#         self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #495057;")
        
#         self.desc_label = QLabel(self.description)
#         self.desc_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        
#         content_layout.addWidget(self.title_label)
#         content_layout.addWidget(self.desc_label)
        
#         layout.addWidget(self.step_label)
#         layout.addLayout(content_layout)
#         layout.addStretch()
        
#     def set_active(self):
#         self.is_active = True
#         self.step_label.setStyleSheet("""
#             QLabel {
#                 background-color: #007bff;
#                 color: white;
#                 border-radius: 20px;
#                 font-weight: bold;
#                 font-size: 16px;
#             }
#         """)
#         self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #007bff;")
        
#     def set_completed(self):
#         self.is_completed = True
#         self.is_active = False
#         self.step_label.setText("✓")
#         self.step_label.setStyleSheet("""
#             QLabel {
#                 background-color: #28a745;
#                 color: white;
#                 border-radius: 20px;
#                 font-weight: bold;
#                 font-size: 16px;
#             }
#         """)
#         self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #28a745;")

# class PartitionSelectionWidget(QGroupBox):
#     """Widget for selecting partition"""
#     def __init__(self):
#         super().__init__("Partition Selection")
#         self.partitions = []
#         self.init_ui()
        
#     def init_ui(self):
#         layout = QVBoxLayout()
        
#         self.partition_list = QListWidget()
#         self.partition_list.setAlternatingRowColors(True)
#         layout.addWidget(self.partition_list)
        
#         # Buttons
#         button_layout = QHBoxLayout()
#         self.select_btn = QPushButton("Select Partition")
#         self.select_btn.setEnabled(False)
#         self.refresh_btn = QPushButton("Refresh")
        
#         # NEW: Parse and Extract Everything button
#         self.auto_process_btn = QPushButton("Parse and Extract Everything")
#         self.auto_process_btn.setEnabled(False)
#         self.auto_process_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #28a745;
#                 color: white;
#                 border: none;
#                 padding: 10px 20px;
#                 border-radius: 6px;
#                 font-weight: bold;
#                 font-size: 13px;
#             }
#             QPushButton:hover {
#                 background-color: #218838;
#             }
#             QPushButton:pressed {
#                 background-color: #1e7e34;
#             }
#             QPushButton:disabled {
#                 background-color: #bdc3c7;
#                 color: #7f8c8d;
#             }
#         """)
        
#         button_layout.addWidget(self.select_btn)
#         button_layout.addWidget(self.auto_process_btn)
#         button_layout.addWidget(self.refresh_btn)
#         button_layout.addStretch()
        
#         layout.addLayout(button_layout)
#         self.setLayout(layout)
        
#         # Connect signals
#         self.partition_list.itemSelectionChanged.connect(self.on_selection_changed)
        
#     def update_partitions(self, partitions):
#         self.partitions = partitions
#         self.partition_list.clear()
        
#         for i, partition in enumerate(partitions):
#             item_text = f"{partition['description']} (Partition {partition['addr']}) - {partition['size_mb']} MB"
#             item = QListWidgetItem(item_text)
#             item.setData(Qt.UserRole, i)
#             self.partition_list.addItem(item)
            
#     def on_selection_changed(self):
#         has_selection = len(self.partition_list.selectedItems()) > 0
#         self.select_btn.setEnabled(has_selection)
#         self.auto_process_btn.setEnabled(has_selection)
        
#     def get_selected_partition(self):
#         selected_items = self.partition_list.selectedItems()
#         if selected_items:
#             index = selected_items[0].data(Qt.UserRole)
#             return self.partitions[index]
#         return None

# class ArtifactSelectionWidget(QGroupBox):
#     """Enhanced widget for selecting artifacts to extract with better spacing"""
#     def __init__(self):
#         super().__init__("Artifact Selection")
#         self.init_ui()
        
#     def init_ui(self):
#         layout = QVBoxLayout()
#         layout.setSpacing(20)  # Add more spacing between sections
        
#         # Artifact categories with better spacing
#         categories = {
#             "System Artifacts": {
#                 '1': ('Registry Hives', 'Windows Registry files containing system and user settings'),
#                 '2': ('Event Logs', 'Windows Event Logs for system activity tracking'),
#                 '5': ('MFT, Pagefile, SRUDB', 'Master File Table, Pagefile, and SRUDB'),
#                 '7': ('Prefetch Files', 'Application execution artifacts')
#             },
#             "User Activity": {
#                 '4': ('Chrome Browser Data', 'Browsing history, downloads, and cache'),
#                 '3': ('Edge Browser Data', 'Microsoft Edge browsing artifacts'),
#                 '6': ('PowerShell Console History', 'PowerShell console command history'),
#                 '8': ('ActivityCache.db', 'Windows Timeline and activity data')
#             }
#         }
        
#         self.artifacts = {}
        
#         for category, items in categories.items():
#             category_group = QGroupBox(category)
#             category_group.setStyleSheet("""
#                 QGroupBox {
#                     font-weight: bold;
#                     font-size: 14px;
#                     color: #2c3e50;
#                     border: 2px solid #bdc3c7;
#                     border-radius: 8px;
#                     margin-top: 15px;
#                     padding-top: 15px;
#                 }
#                 QGroupBox::title {
#                     subcontrol-origin: margin;
#                     left: 15px;
#                     padding: 0 10px;
#                     background-color: #ffffff;
#                 }
#             """)
            
#             category_layout = QGridLayout()
#             category_layout.setSpacing(15)  # More spacing between checkboxes
#             category_layout.setContentsMargins(20, 20, 20, 20)  # More padding
            
#             row = 0
#             col = 0
#             for key, (name, desc) in items.items():
#                 checkbox = QCheckBox(name)
#                 checkbox.setToolTip(desc)
#                 checkbox.setStyleSheet("""
#                     QCheckBox {
#                         font-size: 13px;
#                         font-weight: 500;
#                         color: #34495e;
#                         spacing: 10px;
#                         padding: 8px;
#                     }
#                     QCheckBox::indicator {
#                         width: 20px;
#                         height: 20px;
#                         border-radius: 4px;
#                         border: 2px solid #bdc3c7;
#                         background-color: #ffffff;
#                     }
#                     QCheckBox::indicator:hover {
#                         border-color: #3498db;
#                         background-color: #ecf0f1;
#                     }
#                     QCheckBox::indicator:checked {
#                         background-color: #3498db;
#                         border-color: #3498db;
#                         image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjIgNy44TDEuNCA1IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
#                     }
#                     QCheckBox::indicator:checked:hover {
#                         background-color: #2980b9;
#                         border-color: #2980b9;
#                     }
#                 """)
                
#                 self.artifacts[key] = checkbox
                
#                 category_layout.addWidget(checkbox, row, col)
#                 col += 1
#                 if col > 1:
#                     col = 0
#                     row += 1
                    
#             category_group.setLayout(category_layout)
#             layout.addWidget(category_group)
        
#         # Control buttons with better styling
#         button_layout = QHBoxLayout()
#         button_layout.setSpacing(15)
#         button_layout.setContentsMargins(20, 20, 20, 20)
        
#         self.select_all_btn = QPushButton("Select All")
#         self.clear_all_btn = QPushButton("Clear All")
#         self.extract_btn = QPushButton("Extract Selected Artifacts")
#         self.extract_btn.setEnabled(False)
        
#         # Style buttons
#         button_style = """
#             QPushButton {
#                 background-color: #3498db;
#                 color: white;
#                 border: none;
#                 padding: 10px 20px;
#                 border-radius: 6px;
#                 font-weight: bold;
#                 font-size: 13px;
#             }
#             QPushButton:hover {
#                 background-color: #2980b9;
#             }
#             QPushButton:pressed {
#                 background-color: #21618c;
#             }
#             QPushButton:disabled {
#                 background-color: #bdc3c7;
#                 color: #7f8c8d;
#             }
#         """
        
#         self.select_all_btn.setStyleSheet(button_style)
#         self.clear_all_btn.setStyleSheet(button_style)
#         self.extract_btn.setStyleSheet(button_style.replace("#3498db", "#27ae60").replace("#2980b9", "#229954").replace("#21618c", "#1e8449"))
        
#         self.select_all_btn.clicked.connect(self.select_all)
#         self.clear_all_btn.clicked.connect(self.clear_all)
        
#         # Connect checkboxes to update extract button
#         for checkbox in self.artifacts.values():
#             checkbox.toggled.connect(self.update_extract_button)
        
#         button_layout.addWidget(self.select_all_btn)
#         button_layout.addWidget(self.clear_all_btn)
#         button_layout.addStretch()
#         button_layout.addWidget(self.extract_btn)
        
#         layout.addLayout(button_layout)
#         self.setLayout(layout)
    
#     def select_all(self):
#         for checkbox in self.artifacts.values():
#             checkbox.setChecked(True)
    
#     def clear_all(self):
#         for checkbox in self.artifacts.values():
#             checkbox.setChecked(False)
            
#     def update_extract_button(self):
#         has_selection = any(checkbox.isChecked() for checkbox in self.artifacts.values())
#         self.extract_btn.setEnabled(has_selection)
    
#     def get_selected_artifacts(self):
#         return [key for key, checkbox in self.artifacts.items() if checkbox.isChecked()]

# class ParsingSelectionWidget(QGroupBox):
#     """Widget for selecting parsers to run"""
#     def __init__(self):
#         super().__init__("Parser Selection")
#         self.init_ui()
        
#     def init_ui(self):
#         layout = QVBoxLayout()
#         layout.setSpacing(20)
        
#         # Parser categories with better spacing
#         categories = {
#             "System Parsers": {
#                 'registry': ('Registry Parser', 'Parse Windows Registry files for system configuration and user activity'),
#                 'eventlogs': ('Event Log Parser', 'Parse Windows Event Logs for system events and security incidents'),
#                 'mft': ('MFT Parser', 'Parse Master File Table for file system timeline'),
#                 'prefetch': ('Prefetch Parser', 'Parse Prefetch files for application execution artifacts')
#             },
#             "User Activity Parsers": {
#                 'browser': ('Browser Parser', 'Parse browser artifacts for web activity'),
#                 'powershell': ('PowerShell Parser', 'Parse PowerShell console history'),
#                 'activities': ('Activities Parser', 'Parse Windows Timeline and activity data')
#             }
#         }
        
#         self.parsers = {}
        
#         for category, items in categories.items():
#             category_group = QGroupBox(category)
#             category_group.setStyleSheet("""
#                 QGroupBox {
#                     font-weight: bold;
#                     font-size: 14px;
#                     color: #2c3e50;
#                     border: 2px solid #e67e22;
#                     border-radius: 8px;
#                     margin-top: 15px;
#                     padding-top: 15px;
#                 }
#                 QGroupBox::title {
#                     subcontrol-origin: margin;
#                     left: 15px;
#                     padding: 0 10px;
#                     background-color: #ffffff;
#                 }
#             """)
            
#             category_layout = QGridLayout()
#             category_layout.setSpacing(15)
#             category_layout.setContentsMargins(20, 20, 20, 20)
            
#             row = 0
#             col = 0
#             for key, (name, desc) in items.items():
#                 checkbox = QCheckBox(name)
#                 checkbox.setToolTip(desc)
#                 checkbox.setStyleSheet("""
#                     QCheckBox {
#                         font-size: 13px;
#                         font-weight: 500;
#                         color: #34495e;
#                         spacing: 10px;
#                         padding: 8px;
#                     }
#                     QCheckBox::indicator {
#                         width: 20px;
#                         height: 20px;
#                         border-radius: 4px;
#                         border: 2px solid #e67e22;
#                         background-color: #ffffff;
#                     }
#                     QCheckBox::indicator:hover {
#                         border-color: #e67e22;
#                         background-color: #fdf2e9;
#                     }
#                     QCheckBox::indicator:checked {
#                         background-color: #e67e22;
#                         border-color: #e67e22;
#                         image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjIgNy44TDEuNCA1IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
#                     }
#                     QCheckBox::indicator:checked:hover {
#                         background-color: #d35400;
#                         border-color: #d35400;
#                     }
#                 """)
                
#                 self.parsers[key] = checkbox
                
#                 category_layout.addWidget(checkbox, row, col)
#                 col += 1
#                 if col > 1:
#                     col = 0
#                     row += 1
                    
#             category_group.setLayout(category_layout)
#             layout.addWidget(category_group)
        
#         # Control buttons
#         button_layout = QHBoxLayout()
#         button_layout.setSpacing(15)
#         button_layout.setContentsMargins(20, 20, 20, 20)
        
#         self.select_all_btn = QPushButton("Select All")
#         self.clear_all_btn = QPushButton("Clear All")
#         self.parse_btn = QPushButton("Parse Selected Artifacts")
#         self.parse_btn.setEnabled(False)
        
#         # Style buttons
#         button_style = """
#             QPushButton {
#                 background-color: #e67e22;
#                 color: white;
#                 border: none;
#                 padding: 10px 20px;
#                 border-radius: 6px;
#                 font-weight: bold;
#                 font-size: 13px;
#             }
#             QPushButton:hover {
#                 background-color: #d35400;
#             }
#             QPushButton:pressed {
#                 background-color: #ba4a00;
#             }
#             QPushButton:disabled {
#                 background-color: #bdc3c7;
#                 color: #7f8c8d;
#             }
#         """
        
#         self.select_all_btn.setStyleSheet(button_style)
#         self.clear_all_btn.setStyleSheet(button_style)
#         self.parse_btn.setStyleSheet(button_style.replace("#e67e22", "#8e44ad").replace("#d35400", "#7d3c98").replace("#ba4a00", "#6c3483"))
        
#         self.select_all_btn.clicked.connect(self.select_all)
#         self.clear_all_btn.clicked.connect(self.clear_all)
        
#         # Connect checkboxes to update parse button
#         for checkbox in self.parsers.values():
#             checkbox.toggled.connect(self.update_parse_button)
        
#         button_layout.addWidget(self.select_all_btn)
#         button_layout.addWidget(self.clear_all_btn)
#         button_layout.addStretch()
#         button_layout.addWidget(self.parse_btn)
        
#         layout.addLayout(button_layout)
#         self.setLayout(layout)
    
#     def select_all(self):
#         for checkbox in self.parsers.values():
#             checkbox.setChecked(True)
    
#     def clear_all(self):
#         for checkbox in self.parsers.values():
#             checkbox.setChecked(False)
            
#     def update_parse_button(self):
#         has_selection = any(checkbox.isChecked() for checkbox in self.parsers.values())
#         self.parse_btn.setEnabled(has_selection)
    
#     def get_selected_parsers(self):
#         return [key for key, checkbox in self.parsers.items() if checkbox.isChecked()]

# class ForensicMainWindow(QMainWindow):
#     """Main application window with professional forensic workflow"""
    
#     def __init__(self):
#         super().__init__()
#         self.current_image_path = None
#         self.current_partition = None
#         self.db_connected = False
#         self.workflow_step = 0
#         self.image_thread = None
#         self.db_conn = None
#         self.img_info = None
#         self.fs_info = None
#         self.partitions = []
#         self.auto_process = False
        
#         # Initialize case manager
#         self.case_manager = CaseManager()
        
#         # Configure logging with UTF-8 encoding
#         logging.basicConfig(
#             level=logging.INFO,
#             format='%(asctime)s - %(levelname)s - %(message)s',
#             handlers=[
#                 logging.FileHandler("forensic_tool.log", encoding='utf-8'),
#                 logging.StreamHandler(sys.stdout)
#             ]
#         )
        
#         self.init_ui()
#         self.apply_professional_style()
        
#         # Check for existing case
#         self.check_existing_case()
        
#         if not self.case_manager.current_case:
#             self.check_database_connection()
    
#     def check_existing_case(self):
#         """Check for existing case and load if available"""
#         existing_case = self.case_manager.load_case()
#         if existing_case:
#             reply = QMessageBox.question(
#                 self,
#                 "Existing Case Found",
#                 f"Found existing case: {existing_case['case_name']}\n"
#                 f"Created: {existing_case['created_date']}\n"
#                 f"Status: {existing_case['status']}\n"
#                 f"Workflow Stage: {existing_case['workflow_stage']}\n\n"
#                 "Do you want to continue with this case?",
#                 QMessageBox.Yes | QMessageBox.No
#             )
            
#             if reply == QMessageBox.Yes:
#                 self.load_existing_case(existing_case)
#             else:
#                 self.new_investigation()
    
#     def load_existing_case(self, case_data):
#         """Load existing case and resume from last stage"""
#         self.current_image_path = case_data['image_path']
#         self.image_path_edit.setText(self.current_image_path)
        
#         # Update workflow to last completed stage
#         workflow_stage = case_data.get('workflow_stage', 0)
#         self.update_workflow_step(workflow_stage)
        
#         # Set status based on workflow stage
#         if workflow_stage >= 1:
#             self.db_connected = True
#             self.db_status_label.setText("Connected")
#             self.db_status_label.setStyleSheet("color: #28a745; font-weight: bold;")
#             self.db_status_indicator.setText("DB: Connected")
#             self.db_status_indicator.setStyleSheet("color: #28a745; font-weight: bold;")
        
#         if workflow_stage >= 2 and 'partitions' in case_data:
#             self.partitions = case_data['partitions']
#             self.partition_widget.update_partitions(self.partitions)
            
#         if workflow_stage >= 3 and 'selected_partition' in case_data:
#             self.current_partition = case_data['selected_partition']
            
#         # Set appropriate status message
#         if workflow_stage == 0:
#             self.current_status_label.setText("Case loaded - Check database connection")
#         elif workflow_stage == 1:
#             self.current_status_label.setText("Case loaded - Load evidence image")
#         elif workflow_stage == 2:
#             self.current_status_label.setText("Case loaded - Select partition")
#         elif workflow_stage == 3:
#             self.current_status_label.setText("Case loaded - Scan file system")
#         elif workflow_stage >= 4:
#             self.current_status_label.setText("Case loaded - Ready for artifact extraction")
#             self.tab_widget.setCurrentIndex(2)  # Go to artifact tab
        
#         self.log_message(f"Loaded existing case: {case_data['case_name']}")
    
#     def init_ui(self):
#         """Initialize the user interface"""
#         self.setWindowTitle("Forensic Artifact Extractor & Parser v2.1.0")
#         self.setGeometry(100, 100, 1600, 1000)
        
#         # Create menu bar
#         self.create_menu_bar()
        
#         # Create central widget
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
        
#         # Main layout
#         main_layout = QHBoxLayout(central_widget)
        
#         # Create main splitter
#         main_splitter = QSplitter(Qt.Horizontal)
#         main_layout.addWidget(main_splitter)
        
#         # Left panel - Workflow
#         left_panel = self.create_workflow_panel()
#         main_splitter.addWidget(left_panel)
        
#         # Right panel - Content
#         right_panel = self.create_content_panel()
#         main_splitter.addWidget(right_panel)
        
#         # Set splitter proportions
#         main_splitter.setSizes([400, 1200])
        
#         # Create status bar
#         self.create_status_bar()
    
#     def create_menu_bar(self):
#         """Create professional menu bar"""
#         menubar = self.menuBar()
        
#         # File menu
#         file_menu = menubar.addMenu('&File')
        
#         new_case_action = QAction('&New Investigation', self)
#         new_case_action.setShortcut('Ctrl+N')
#         new_case_action.triggered.connect(self.new_investigation)
#         file_menu.addAction(new_case_action)
        
#         load_image_action = QAction('&Load Evidence Image', self)
#         load_image_action.setShortcut('Ctrl+O')
#         load_image_action.triggered.connect(self.load_evidence_image)
#         file_menu.addAction(load_image_action)
        
#         file_menu.addSeparator()
        
#         save_case_action = QAction('&Save Case', self)
#         save_case_action.setShortcut('Ctrl+S')
#         save_case_action.triggered.connect(self.save_case)
#         file_menu.addAction(save_case_action)
        
#         file_menu.addSeparator()
        
#         exit_action = QAction('E&xit', self)
#         exit_action.setShortcut('Ctrl+Q')
#         exit_action.triggered.connect(self.close)
#         file_menu.addAction(exit_action)
        
#         # Tools menu
#         tools_menu = menubar.addMenu('&Tools')
        
#         db_test_action = QAction('Test &Database Connection', self)
#         db_test_action.triggered.connect(self.check_database_connection)
#         tools_menu.addAction(db_test_action)
        
#         libs_check_action = QAction('Check &Libraries', self)
#         libs_check_action.triggered.connect(self.check_libraries)
#         tools_menu.addAction(libs_check_action)
        
#         # Help menu
#         help_menu = menubar.addMenu('&Help')
        
#         about_action = QAction('&About', self)
#         about_action.triggered.connect(self.show_about)
#         help_menu.addAction(about_action)
    
#     def create_workflow_panel(self):
#         """Create left panel with workflow steps"""
#         workflow_widget = QWidget()
#         layout = QVBoxLayout(workflow_widget)
        
#         # Workflow title
#         title_label = QLabel("Investigation Workflow")
#         title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px;")
#         layout.addWidget(title_label)
        
#         # Case information
#         case_group = QGroupBox("Case Information")
#         case_layout = QVBoxLayout()
        
#         self.case_info_label = QLabel("No case loaded")
#         self.case_info_label.setStyleSheet("color: #6c757d; font-size: 12px;")
#         case_layout.addWidget(self.case_info_label)
        
#         case_group.setLayout(case_layout)
#         layout.addWidget(case_group)
        
#         # Library status
#         lib_status_group = QGroupBox("System Status")
#         lib_layout = QVBoxLayout()
        
#         self.lib_status_label = QLabel("Checking libraries...")
#         lib_layout.addWidget(self.lib_status_label)
        
#         lib_status_group.setLayout(lib_layout)
#         layout.addWidget(lib_status_group)
        
#         # Workflow steps
#         self.workflow_steps = []
        
#         steps = [
#             ("Database Connection", "Verify database connectivity"),
#             ("Load Evidence Image", "Load forensic image file"),
#             ("Select Partition", "Choose partition to analyze"),
#             ("Scan File System", "Scan and ingest file system data"),
#             ("Select Artifacts", "Choose artifacts to extract"),
#             ("Extract Artifacts", "Perform artifact extraction"),
#             ("Parse Artifacts", "Parse extracted artifacts")
#         ]
        
#         for i, (title, desc) in enumerate(steps, 1):
#             step_widget = WorkflowStepWidget(i, title, desc)
#             self.workflow_steps.append(step_widget)
#             layout.addWidget(step_widget)
        
#         layout.addStretch()
        
#         # Current status
#         status_group = QGroupBox("Current Status")
#         status_layout = QVBoxLayout()
        
#         self.current_status_label = QLabel("Ready to start investigation")
#         self.current_status_label.setStyleSheet("font-weight: bold; color: #495057;")
#         status_layout.addWidget(self.current_status_label)
        
#         status_group.setLayout(status_layout)
#         layout.addWidget(status_group)
        
#         # Update library status
#         self.update_library_status()
        
#         return workflow_widget
    
#     def update_library_status(self):
#         """Update library status display"""
#         if FORENSIC_LIBS_AVAILABLE:
#             self.lib_status_label.setText("✓ All forensic libraries available")
#             self.lib_status_label.setStyleSheet("color: #28a745; font-weight: bold;")
#         else:
#             self.lib_status_label.setText("⚠ Some forensic libraries missing")
#             self.lib_status_label.setStyleSheet("color: #ffc107; font-weight: bold;")
    
#     def create_content_panel(self):
#         """Create right panel with content tabs"""
#         self.tab_widget = QTabWidget()
        
#         # Set tab bar style for better visibility
#         self.tab_widget.setStyleSheet("""
#             QTabWidget::pane {
#                 border: 1px solid #dee2e6;
#                 background-color: #ffffff;
#                 border-radius: 4px;
#             }
            
#             QTabBar::tab {
#                 background-color: #f8f9fa;
#                 color: #495057;
#                 padding: 12px 25px;
#                 margin-right: 3px;
#                 border-top-left-radius: 6px;
#                 border-top-right-radius: 6px;
#                 border: 1px solid #dee2e6;
#                 border-bottom: none;
#                 font-weight: 600;
#                 font-size: 14px;
#                 min-width: 120px;
#             }
            
#             QTabBar::tab:selected {
#                 background-color: #ffffff;
#                 color: #1976d2;
#                 border-bottom: 3px solid #1976d2;
#                 font-weight: bold;
#             }
            
#             QTabBar::tab:hover:!selected {
#                 background-color: #e9ecef;
#                 color: #495057;
#             }
#         """)
        
#         # Main Control Tab
#         self.create_main_control_tab()
        
#         # Partition Selection Tab
#         self.create_partition_tab()
        
#         # Artifact Selection Tab
#         self.create_artifact_tab()
        
#         # Processing Log Tab
#         self.create_log_tab()
        
#         # Results Tab
#         self.create_results_tab()
        
#         # Parsing Tab
#         self.create_parsing_tab()
        
#         return self.tab_widget
    
#     def create_main_control_tab(self):
#         """Create main control tab"""
#         main_widget = QWidget()
#         layout = QVBoxLayout(main_widget)
        
#         # Case management section
#         case_group = QGroupBox("Case Management")
#         case_layout = QVBoxLayout()
        
#         # Case name input
#         case_name_layout = QHBoxLayout()
#         case_name_layout.addWidget(QLabel("Case Name:"))
#         self.case_name_edit = QLineEdit()
#         self.case_name_edit.setPlaceholderText("Enter case name...")
#         case_name_layout.addWidget(self.case_name_edit)
        
#         # Investigator input
#         investigator_layout = QHBoxLayout()
#         investigator_layout.addWidget(QLabel("Investigator:"))
#         self.investigator_edit = QLineEdit()
#         self.investigator_edit.setPlaceholderText("Enter investigator name...")
#         investigator_layout.addWidget(self.investigator_edit)
        
#         case_layout.addLayout(case_name_layout)
#         case_layout.addLayout(investigator_layout)
        
#         case_group.setLayout(case_layout)
#         layout.addWidget(case_group)
        
#         # Database status
#         db_group = QGroupBox("Database Connection")
#         db_layout = QHBoxLayout()
        
#         self.db_status_label = QLabel("Checking...")
#         self.db_test_btn = QPushButton("Test Connection")
#         self.db_test_btn.clicked.connect(self.check_database_connection)
        
#         db_layout.addWidget(QLabel("Status:"))
#         db_layout.addWidget(self.db_status_label)
#         db_layout.addStretch()
#         db_layout.addWidget(self.db_test_btn)
        
#         db_group.setLayout(db_layout)
#         layout.addWidget(db_group)
        
#         # Evidence image loading
#         image_group = QGroupBox("Evidence Image")
#         image_layout = QVBoxLayout()
        
#         # File selection
#         file_layout = QHBoxLayout()
#         self.image_path_edit = QLineEdit()
#         self.image_path_edit.setPlaceholderText("Select E01 evidence image file...")
#         self.image_path_edit.textChanged.connect(self.on_image_path_changed)
#         self.browse_btn = QPushButton("Browse")
#         self.browse_btn.clicked.connect(self.browse_image_file)
        
#         file_layout.addWidget(self.image_path_edit)
#         file_layout.addWidget(self.browse_btn)
        
#         # Auto-processing checkbox
#         self.auto_process_checkbox = QCheckBox("Parse and extract everything automatically")
#         self.auto_process_checkbox.setToolTip("If checked, the tool will automatically extract and parse all artifacts without user intervention")
#         self.auto_process_checkbox.toggled.connect(self.on_auto_process_toggled)
        
#         # Load button
#         self.load_image_btn = QPushButton("Process Image")
#         self.load_image_btn.setEnabled(False)
#         self.load_image_btn.clicked.connect(self.load_evidence_image)
        
#         # File info label
#         self.file_info_label = QLabel("")
#         self.file_info_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        
#         image_layout.addLayout(file_layout)
#         image_layout.addWidget(self.auto_process_checkbox)
#         image_layout.addWidget(self.file_info_label)
#         image_layout.addWidget(self.load_image_btn)
        
#         image_group.setLayout(image_layout)
#         layout.addWidget(image_group)
        
#         # Progress section
#         progress_group = QGroupBox("Processing Progress")
#         progress_layout = QVBoxLayout()
        
#         self.main_progress_bar = QProgressBar()
#         self.main_progress_bar.setVisible(False)
        
#         self.progress_label = QLabel("Ready")
        
#         progress_layout.addWidget(self.progress_label)
#         progress_layout.addWidget(self.main_progress_bar)
        
#         progress_group.setLayout(progress_layout)
#         layout.addWidget(progress_group)
        
#         layout.addStretch()
        
#         self.tab_widget.addTab(main_widget, "Main Control")
    
#     def create_partition_tab(self):
#         """Create partition selection tab"""
#         self.partition_widget = PartitionSelectionWidget()
#         self.partition_widget.select_btn.clicked.connect(self.select_partition)
#         self.partition_widget.auto_process_btn.clicked.connect(self.auto_process_from_partition)
#         self.tab_widget.addTab(self.partition_widget, "Select Partition")
    
#     def create_artifact_tab(self):
#         """Create artifact selection tab"""
#         self.artifact_widget = ArtifactSelectionWidget()
#         self.artifact_widget.extract_btn.clicked.connect(self.extract_artifacts)
#         self.tab_widget.addTab(self.artifact_widget, "Artifact Selection")
    
#     def create_log_tab(self):
#         """Create processing log tab"""
#         self.log_text = QTextEdit()
#         self.log_text.setReadOnly(True)
#         self.log_text.setFont(QFont("Consolas", 10))
#         self.tab_widget.addTab(self.log_text, "Processing Log")
    
#     def create_results_tab(self):
#         """Create results tab"""
#         results_widget = QWidget()
#         layout = QVBoxLayout(results_widget)
        
#         # Results table
#         self.results_table = QTableWidget()
#         self.results_table.setColumnCount(4)
#         self.results_table.setHorizontalHeaderLabels(['Artifact', 'Status', 'Location', 'Details'])
        
#         layout.addWidget(self.results_table)
        
#         # self.tab_widget.addTab(results_widget, "Extraction Results")
    
#     def create_parsing_tab(self):
#         """Create parsing tab"""
#         self.parsing_widget = ParsingSelectionWidget()
#         self.parsing_widget.parse_btn.clicked.connect(self.parse_artifacts)
#         self.tab_widget.addTab(self.parsing_widget, "Artifact Parsing")
    
#     def create_status_bar(self):
#         """Create professional status bar"""
#         self.status_bar = QStatusBar()
#         self.setStatusBar(self.status_bar)
        
#         # Status label
#         self.status_label = QLabel("Ready")
#         self.status_bar.addWidget(self.status_label)
        
#         # Progress bar
#         self.status_progress_bar = QProgressBar()
#         self.status_progress_bar.setVisible(False)
#         self.status_progress_bar.setMaximumWidth(200)
#         self.status_bar.addPermanentWidget(self.status_progress_bar)
        
#         # Database status
#         self.db_status_indicator = QLabel("DB: Disconnected")
#         self.status_bar.addPermanentWidget(self.db_status_indicator)
        
#         # Library status
#         self.lib_status_indicator = QLabel("Libs: Checking")
#         self.status_bar.addPermanentWidget(self.lib_status_indicator)
        
#         # Update library indicator
#         if FORENSIC_LIBS_AVAILABLE:
#             self.lib_status_indicator.setText("Libs: OK")
#             self.lib_status_indicator.setStyleSheet("color: #28a745; font-weight: bold;")
#         else:
#             self.lib_status_indicator.setText("Libs: Missing")
#             self.lib_status_indicator.setStyleSheet("color: #ffc107; font-weight: bold;")
    
#     def apply_professional_style(self):
#         """Apply professional light theme"""
#         self.setStyleSheet("""
#             QMainWindow {
#                 background-color: #ffffff;
#                 color: #2c3e50;
#                 font-family: 'Segoe UI', Arial, sans-serif;
#             }
            
#             QMenuBar {
#                 background-color: #f8f9fa;
#                 color: #2c3e50;
#                 border-bottom: 1px solid #dee2e6;
#                 padding: 2px;
#                 font-weight: 500;
#             }
            
#             QMenuBar::item {
#                 background-color: transparent;
#                 padding: 6px 12px;
#                 border-radius: 3px;
#                 margin: 2px;
#             }
            
#             QMenuBar::item:selected {
#                 background-color: #e9ecef;
#                 color: #495057;
#             }
            
#             QMenu {
#                 background-color: #ffffff;
#                 color: #2c3e50;
#                 border: 1px solid #dee2e6;
#                 border-radius: 4px;
#                 padding: 4px;
#             }
            
#             QMenu::item {
#                 padding: 6px 20px;
#                 border-radius: 3px;
#             }
            
#             QMenu::item:selected {
#                 background-color: #e3f2fd;
#                 color: #1976d2;
#             }
#             QPushButton {
#                 background-color: #1d4ed8; /* Tailwind's bg-blue-700 */
#                 color: white;              /* text-white */
#                 border: none;
#                 padding: 10px 20px;        /* similar to px-5 py-2.5 */
#                 border-radius: 8px;        /* rounded-lg */
#                 font-weight: 500;          /* font-medium */
#                 font-size: 14px;           /* text-sm */
#                 min-width: 80px;
#             }

#             QPushButton:hover {
#                 background-color: #1e40af; /* Tailwind's hover:bg-blue-800 */
#             }

#             QPushButton:pressed {
#                 background-color: #1e3a8a; /* A bit darker for press */
#             }

#             QPushButton:focus {
#                 outline: none;
#                 border: 2px solid #93c5fd; /* focus:ring-blue-300 */
#             }

#             QPushButton:disabled {
#                 background-color: #e5e7eb; /* Tailwind's bg-gray-200 */
#                 color: #9ca3af;            /* Tailwind's text-gray-400 */
#             }

#             # QPushButton {
#             #     background-color: #0468BF;
#             #     color: #049DD9;
#             #     border: 1px solid #ced4da;
#             #     padding: 8px 16px;
#             #     border-radius: 4px;
#             #     font-weight: 500;
#             #     min-width: 80px;
#             # }
            
#             # QPushButton:hover {
#             #     background-color: #049DD9;
#             #     border-color: #adb5bd;
#             #     color: #212529;
#             # }
            
#             # QPushButton:pressed {
#             #     background-color: #dee2e6;
#             #     border-color: #6c757d;
#             # }
            
#             # QPushButton:disabled {
#             #     background-color: #f8f9fa;
#             #     color: #6c757d;
#             #     border-color: #dee2e6;
#             # }
            
#             QGroupBox {
#                 color: #495057;
#                 border: 2px solid #dee2e6;
#                 border-radius: 6px;
#                 margin-top: 12px;
#                 font-weight: 600;
#                 padding-top: 8px;
#             }
            
#             QGroupBox::title {
#                 subcontrol-origin: margin;
#                 left: 12px;
#                 padding: 0 8px;
#                 background-color: #ffffff;
#                 color: #495057;
#             }
            
#             QTreeWidget, QTableWidget, QListWidget {
#                 background-color: #ffffff;
#                 color: #495057;
#                 border: 1px solid #dee2e6;
#                 alternate-background-color: #f8f9fa;
#                 gridline-color: #e9ecef;
#                 border-radius: 4px;
#             }
            
#             QTreeWidget::item, QTableWidget::item, QListWidget::item {
#                 padding: 4px;
#                 border-bottom: 1px solid #f1f3f4;
#             }
            
#             QTreeWidget::item:selected, QTableWidget::item:selected, QListWidget::item:selected {
#                 background-color: #e3f2fd;
#                 color: #1976d2;
#             }
            
#             QHeaderView::section {
#                 background-color: #f8f9fa;
#                 color: #495057;
#                 padding: 8px 12px;
#                 border: none;
#                 border-right: 1px solid #dee2e6;
#                 border-bottom: 1px solid #dee2e6;
#                 font-weight: 600;
#             }
            
#             QLineEdit, QTextEdit {
#                 background-color: #ffffff;
#                 color: #495057;
#                 border: 1px solid #ced4da;
#                 padding: 6px 12px;
#                 border-radius: 4px;
#                 font-size: 14px;
#             }
            
#             QProgressBar {
#                 border: 1px solid #dee2e6;
#                 border-radius: 4px;
#                 text-align: center;
#                 background-color: #f8f9fa;
#                 color: #495057;
#                 font-weight: 500;
#             }
            
#             QProgressBar::chunk {
#                 background-color: #28a745;
#                 border-radius: 3px;
#             }
            
#             QStatusBar {
#                 background-color: #f8f9fa;
#                 color: #495057;
#                 border-top: 1px solid #dee2e6;
#                 padding: 4px;
#             }
            
#             QSplitter::handle {
#                 background-color: #dee2e6;
#                 width: 2px;
#                 height: 2px;
#             }
#         """)
    
#     def update_workflow_step(self, step):
#         """Update workflow step indicator"""
#         # Mark previous steps as completed
#         for i in range(step):
#             if i < len(self.workflow_steps):
#                 self.workflow_steps[i].set_completed()
        
#         # Mark current step as active
#         if step < len(self.workflow_steps):
#             self.workflow_steps[step].set_active()
        
#         self.workflow_step = step
        
#         # Update case manager
#         if self.case_manager.current_case:
#             self.case_manager.update_case_status(f"workflow_step_{step}", step)
    
#     def log_message(self, message):
#         """Add message to log with proper Unicode handling"""
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
#         # Replace Unicode characters that cause issues
#         safe_message = message.replace('✓', '[SUCCESS]').replace('✗', '[FAILED]')
#         log_entry = f"[{timestamp}] {safe_message}"
        
#         self.log_text.append(log_entry)
#         self.progress_label.setText(safe_message)
#         self.status_label.setText(safe_message)
        
#         # Use safe logging
#         try:
#             logging.info(safe_message)
#         except UnicodeEncodeError:
#             # Fallback for problematic characters
#             ascii_message = safe_message.encode('ascii', errors='ignore').decode('ascii')
#             logging.info(ascii_message)
        
#         QApplication.processEvents()
    
#     def check_database_connection(self):
#         """Check database connection"""
#         self.log_message("Testing database connection...")
#         self.db_test_btn.setEnabled(False)
        
#         self.db_thread = DatabaseConnectionThread()
#         self.db_thread.connection_result.connect(self.on_database_result)
#         self.db_thread.start()
    
#     def on_database_result(self, success, message):
#         """Handle database connection result"""
#         self.db_test_btn.setEnabled(True)
        
#         if success:
#             self.db_connected = True
#             self.db_status_label.setText("Connected")
#             self.db_status_label.setStyleSheet("color: #28a745; font-weight: bold;")
#             self.db_status_indicator.setText("DB: Connected")
#             self.db_status_indicator.setStyleSheet("color: #28a745; font-weight: bold;")
#             self.update_workflow_step(1)
#             self.current_status_label.setText("Database connected - Ready to load evidence")
#         else:
#             self.db_connected = False
#             self.db_status_label.setText("Failed")
#             self.db_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
#             self.db_status_indicator.setText("DB: Failed")
#             self.db_status_indicator.setStyleSheet("color: #dc3545; font-weight: bold;")
        
#         self.log_message(message)
    
#     def check_libraries(self):
#         """Check forensic libraries"""
#         libs_info = []
        
#         try:
#             import pytsk3
#             libs_info.append("✓ pytsk3: Available")
#         except ImportError:
#             libs_info.append("✗ pytsk3: Missing")
        
#         try:
#             import pyewf
#             libs_info.append("✓ pyewf: Available")
#         except ImportError:
#             libs_info.append("✗ pyewf: Missing")
        
#         try:
#             import psycopg2
#             libs_info.append("✓ psycopg2: Available")
#         except ImportError:
#             libs_info.append("✗ psycopg2: Missing")
        
#         # Check parser availability
#         libs_info.append("")  # Add separator
#         libs_info.append("Parser Scripts:")
        
#         if parse_registry_artifacts is not None:
#             libs_info.append("✓ Registry Parser: Available")
#         else:
#             libs_info.append("✗ Registry Parser: Missing")
        
#         if parse_browser_artifacts is not None:
#             libs_info.append("✓ Browser Parser: Available")
#         else:
#             libs_info.append("✗ Browser Parser: Missing")
        
#         if parse_system_artifacts is not None:
#             libs_info.append("✓ System Artifacts Parser: Available")
#         else:
#             libs_info.append("✗ System Artifacts Parser: Missing")
        
#         QMessageBox.information(
#             self,
#             "Library Status",
#             "Forensic Libraries and Parsers Status:\n\n" + "\n".join(libs_info)
#         )
    
#     def on_auto_process_toggled(self, checked):
#         """Handle auto-processing checkbox toggle"""
#         self.auto_process = checked
#         if checked:
#             self.log_message("Auto-processing enabled: Will extract and parse all artifacts automatically")
#         else:
#             self.log_message("Auto-processing disabled: Manual workflow enabled")
    
#     def on_image_path_changed(self):
#         """Handle image path change"""
#         path = self.image_path_edit.text()
#         self.load_image_btn.setEnabled(bool(path and os.path.exists(path)))
        
#         if path and os.path.exists(path):
#             try:
#                 file_size = os.path.getsize(path)
#                 size_mb = file_size / (1024 * 1024)
#                 self.file_info_label.setText(f"File size: {size_mb:.2f} MB")
#             except:
#                 self.file_info_label.setText("File information unavailable")
#         else:
#             self.file_info_label.setText("")
    
#     def browse_image_file(self):
#         """Browse for evidence image file"""
#         file_path, _ = QFileDialog.getOpenFileName(
#             self,
#             "Select E01 Evidence Image",
#             "",
#             "E01 Files (*.E01);;All Files (*)"
#         )
        
#         if file_path:
#             self.image_path_edit.setText(file_path)
#             self.current_image_path = file_path
#             logging.info(f"Selected image file: {file_path}")
    
#     def load_evidence_image(self):
#         """Load evidence image"""
#         if not FORENSIC_LIBS_AVAILABLE:
#             QMessageBox.warning(
#                 self, 
#                 "Warning", 
#                 "Forensic libraries (pytsk3, pyewf) are not available.\n\n"
#                 "Please install them using:\n"
#                 "pip install pytsk3 pyewf"
#             )
#             return
            
#         if not self.db_connected:
#             QMessageBox.warning(self, "Warning", "Database connection required before loading image")
#             return
        
#         image_path = self.image_path_edit.text()
#         if not image_path or not os.path.exists(image_path):
#             QMessageBox.warning(self, "Warning", "Please select a valid E01 image file")
#             return
        
#         # Create new case if not exists
#         if not self.case_manager.current_case:
#             case_name = self.case_name_edit.text() or f"Case_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
#             investigator = self.investigator_edit.text() or "Unknown"
#             self.case_manager.create_case(case_name, image_path, investigator)
#             self.update_case_info()
        
#         self.current_image_path = image_path
#         self.log_message(f"Processing image: {os.path.basename(image_path)}")
        
#         # Initialize database connection
#         try:
#             self.db_conn = open_db()
#             create_table(self.db_conn)
#             logging.info("Database initialized")
#         except Exception as e:
#             QMessageBox.critical(self, "Database Error", f"Failed to initialize database: {str(e)}")
#             return
        
#         # Show progress
#         self.main_progress_bar.setVisible(True)
#         self.main_progress_bar.setRange(0, 0)
#         self.status_progress_bar.setVisible(True)
#         self.status_progress_bar.setRange(0, 0)
        
#         # Disable controls
#         self.load_image_btn.setEnabled(False)
#         self.browse_btn.setEnabled(False)
        
#         # Start loading thread
#         self.image_thread = ImageLoadingThread(image_path)
#         self.image_thread.progress_update.connect(self.log_message)
#         self.image_thread.partitions_found.connect(self.on_partitions_found)
#         self.image_thread.loading_complete.connect(self.on_image_loaded)
#         self.image_thread.start()
    
#     def update_case_info(self):
#         """Update case information display"""
#         if self.case_manager.current_case:
#             case_info = f"Case: {self.case_manager.current_case['case_name']}\n"
#             case_info += f"Investigator: {self.case_manager.current_case['investigator']}\n"
#             case_info += f"Created: {self.case_manager.current_case['created_date'][:10]}"
#             self.case_info_label.setText(case_info)
#         else:
#             self.case_info_label.setText("No case loaded")
    
#     def on_partitions_found(self, partitions):
#         """Handle partitions found - FIXED: No auto-selection"""
#         self.partitions = partitions
#         self.img_info = self.image_thread.img_info
#         self.partition_widget.update_partitions(partitions)
        
#         # Save partitions to case (without non-serializable objects)
#         self.case_manager.set_partitions(partitions)
        
#         # REMOVED AUTO-PROCESSING - Always go to partition tab
#         self.tab_widget.setCurrentIndex(1)  # Switch to partition tab
        
#         # Update info display
#         partition_info = "Available Partitions:\n\n"
#         for part in partitions:
#             partition_info += f"- Partition {part['addr']}\n"
#             partition_info += f"  Type: {part['description']}\n"
#             partition_info += f"  Size: {part['size_mb']} MB\n\n"
        
#         self.log_message(partition_info)
#         self.log_message("Please select a partition to continue")
    
#     def on_image_loaded(self, success, message):
#         """Handle image loading completion"""
#         # Hide progress
#         self.main_progress_bar.setVisible(False)
#         self.status_progress_bar.setVisible(False)
        
#         # Re-enable controls
#         self.load_image_btn.setEnabled(True)
#         self.browse_btn.setEnabled(True)
        
#         if success:
#             self.update_workflow_step(2)
#             self.current_status_label.setText("Image loaded - Select partition to analyze")
#             self.log_message("Evidence image loaded successfully - Please select a partition")
#         else:
#             QMessageBox.critical(self, "Error", f"Failed to load image:\n\n{message}")
        
#         self.log_message(message)
    
#     def auto_process_from_partition(self):
#         """Auto-process everything from partition selection with UI improvements"""
#         selected_partition = self.partition_widget.get_selected_partition()
#         if not selected_partition:
#             QMessageBox.warning(self, "Warning", "Please select a partition first")
#             return
        
#         self.current_partition = selected_partition
#         self.case_manager.set_selected_partition(selected_partition)
#         self.log_message(f"Starting auto-processing for partition: {selected_partition['description']}")
        
#         # Switch to Processing Log tab immediately
#         self.tab_widget.setCurrentIndex(3)  # Processing Log tab
        
#         # Disable artifact and parsing selection tabs
#         self.artifact_widget.setEnabled(False)
#         self.parsing_widget.setEnabled(False)
        
#         # Start auto file system scan
#         self.auto_scan_file_system()
    
#     def auto_scan_file_system(self):
#         """Automatically scan file system for auto-processing"""
#         self.log_message("Auto-processing: Starting file system scan...")
#         self.update_workflow_step(3)
        
#         # Show progress
#         self.main_progress_bar.setVisible(True)
#         self.main_progress_bar.setRange(0, 0)
#         self.status_progress_bar.setVisible(True)
#         self.status_progress_bar.setRange(0, 0)
        
#         # Start scanning thread
#         self.scan_thread = FileSystemScanThread(self.img_info, self.current_partition, self.db_conn)
#         self.scan_thread.progress_update.connect(self.log_message)
#         self.scan_thread.scan_complete.connect(self.on_auto_scan_complete)
#         self.scan_thread.start()
    
#     def on_auto_scan_complete(self, success, message, result_info):
#         """Handle auto scan completion"""
#         # Hide progress
#         self.main_progress_bar.setVisible(False)
#         self.status_progress_bar.setVisible(False)
        
#         if success:
#             self.fs_info = result_info['fs_info']
#             self.update_workflow_step(4)
#             self.log_message("Auto-processing: File system scan completed, starting automatic processing...")
            
#             # Start auto-processing
#             self.auto_processing_thread = AutoProcessingThread(
#                 self.img_info, self.current_partition, self.db_conn, self.fs_info
#             )
#             self.auto_processing_thread.progress_update.connect(self.log_message)
#             self.auto_processing_thread.processing_complete.connect(self.on_auto_processing_complete)
#             self.auto_processing_thread.start()
#         else:
#             QMessageBox.critical(self, "Error", f"Auto scan failed: {message}")
        
#         self.log_message(message)
    
#     def on_auto_processing_complete(self, success, message):
#         """Handle auto-processing completion with UI cleanup"""
#         # Re-enable tabs
#         self.artifact_widget.setEnabled(True)
#         self.parsing_widget.setEnabled(True)
        
#         if success:
#             self.update_workflow_step(7)
#             self.current_status_label.setText("Auto-processing completed - Investigation finished")
#             self.tab_widget.setCurrentIndex(4)  # Switch to results tab
#             QMessageBox.information(self, "Auto-Processing Complete", message)
#         else:
#             QMessageBox.critical(self, "Auto-Processing Failed", message)
        
#         self.log_message(message)
    
#     def select_partition(self):
#         """Select partition for analysis"""
#         selected_partition = self.partition_widget.get_selected_partition()
#         if not selected_partition:
#             QMessageBox.warning(self, "Warning", "Please select a partition")
#             return
        
#         self.current_partition = selected_partition
#         self.case_manager.set_selected_partition(selected_partition)
#         self.log_message(f"Selected partition {selected_partition['addr']}: {selected_partition['description']}")
        
#         # Start file system scanning
#         reply = QMessageBox.question(
#             self, 
#             "Confirm Scan", 
#             f"Scan partition '{selected_partition['description']}'?\n\nThis may take several minutes.",
#             QMessageBox.Yes | QMessageBox.No
#         )
        
#         if reply == QMessageBox.Yes:
#             self.scan_file_system()
    
#     def scan_file_system(self):
#         """Scan file system"""
#         self.log_message("Starting file system scan...")
#         self.update_workflow_step(3)
        
#         # Show progress
#         self.main_progress_bar.setVisible(True)
#         self.main_progress_bar.setRange(0, 0)
#         self.status_progress_bar.setVisible(True)
#         self.status_progress_bar.setRange(0, 0)
        
#         # Start scanning thread
#         self.scan_thread = FileSystemScanThread(self.img_info, self.current_partition, self.db_conn)
#         self.scan_thread.progress_update.connect(self.log_message)
#         self.scan_thread.scan_complete.connect(self.on_scan_complete)
#         self.scan_thread.start()
    
#     def on_scan_complete(self, success, message, result_info):
#         """Handle scan completion"""
#         # Hide progress
#         self.main_progress_bar.setVisible(False)
#         self.status_progress_bar.setVisible(False)
        
#         if success:
#             self.fs_info = result_info['fs_info']
#             self.update_workflow_step(4)
#             self.current_status_label.setText("File system scanned - Select artifacts to extract")
#             self.tab_widget.setCurrentIndex(2)  # Switch to artifact tab
#             QMessageBox.information(self, "Success", "File system scan completed successfully")
#         else:
#             QMessageBox.critical(self, "Error", f"Scan failed: {message}")
        
#         self.log_message(message)
    
#     def extract_artifacts(self):
#         """Extract selected artifacts"""
#         selected_artifacts = self.artifact_widget.get_selected_artifacts()
        
#         if not selected_artifacts:
#             QMessageBox.warning(self, "Warning", "Please select artifacts to extract")
#             return
        
#         if not self.fs_info or not self.db_conn:
#             QMessageBox.warning(self, "Warning", "File system must be scanned first")
#             return
        
#         self.log_message(f"Starting extraction of: {', '.join(selected_artifacts)}")
#         self.update_workflow_step(5)
        
#         # Show progress
#         self.main_progress_bar.setVisible(True)
#         self.main_progress_bar.setRange(0, 0)
#         self.status_progress_bar.setVisible(True)
#         self.status_progress_bar.setRange(0, 0)
        
#         # Disable extract button
#         self.artifact_widget.extract_btn.setEnabled(False)
        
#         # Start extraction thread
#         self.extraction_thread = ArtifactExtractionThread(self.fs_info, self.db_conn, selected_artifacts)
#         self.extraction_thread.progress_update.connect(self.log_message)
#         self.extraction_thread.extraction_complete.connect(self.on_extraction_complete)
#         self.extraction_thread.start()
    
#     def on_extraction_complete(self, success, message, results):
#         """Handle extraction completion"""
#         # Hide progress
#         self.main_progress_bar.setVisible(False)
#         self.status_progress_bar.setVisible(False)
        
#         # Re-enable extract button
#         self.artifact_widget.extract_btn.setEnabled(True)
        
#         if success:
#             self.update_workflow_step(6)
#             self.current_status_label.setText("Artifacts extracted - Ready for parsing")
#             self.update_results_table(results)
#             self.tab_widget.setCurrentIndex(4)  # Switch to results tab
            
#             # Save extracted artifacts to case
#             for name, success_status in results:
#                 self.case_manager.add_extracted_artifact({'name': name, 'success': success_status})
            
#             # Show results
#             result_text = "Extraction Results:\n\n"
#             for name, success_status in results:
#                 status = "Success" if success_status else "Failed"
#                 result_text += f"- {name}: {status}\n"
            
#             self.log_message(result_text)
#             QMessageBox.information(self, "Success", "Artifact extraction completed")
#         else:
#             QMessageBox.critical(self, "Error", f"Extraction failed: {message}")
        
#         self.log_message(message)
    
#     def update_results_table(self, results):
#         """Update results table with extraction results"""
#         self.results_table.setRowCount(len(results))
        
#         for i, (artifact, status) in enumerate(results):
#             self.results_table.setItem(i, 0, QTableWidgetItem(artifact))
            
#             if status:
#                 status_item = QTableWidgetItem("✓ Success")
#                 status_item.setBackground(QColor("#d4edda"))
#             else:
#                 status_item = QTableWidgetItem("✗ Failed")
#                 status_item.setBackground(QColor("#f8d7da"))
            
#             self.results_table.setItem(i, 1, status_item)
#             self.results_table.setItem(i, 2, QTableWidgetItem(f"output/{artifact.lower().replace(' ', '_')}"))
#             self.results_table.setItem(i, 3, QTableWidgetItem("Extracted successfully" if status else "Extraction failed"))
        
#         # Resize columns
#         self.results_table.resizeColumnsToContents()
    
#     def parse_artifacts(self):
#         """Parse selected artifacts using the integrated parser scripts"""
#         selected_parsers = self.parsing_widget.get_selected_parsers()
        
#         if not selected_parsers:
#             QMessageBox.warning(self, "Warning", "Please select parsers to run")
#             return
        
#         self.log_message(f"Starting parsing with: {', '.join(selected_parsers)}")
#         self.update_workflow_step(7)
        
#         # Show progress
#         self.main_progress_bar.setVisible(True)
#         self.main_progress_bar.setRange(0, 0)
#         self.status_progress_bar.setVisible(True)
#         self.status_progress_bar.setRange(0, 0)
        
#         # Disable parse button
#         self.parsing_widget.parse_btn.setEnabled(False)
        
#         # Start parsing thread with integrated parsers
#         self.parsing_thread = ParsingThread(selected_parsers)
#         self.parsing_thread.progress_update.connect(self.log_message)
#         self.parsing_thread.parsing_complete.connect(self.on_parsing_complete)
#         self.parsing_thread.start()
    
#     def on_parsing_complete(self, success, message, results):
#         """Handle parsing completion"""
#         # Hide progress
#         self.main_progress_bar.setVisible(False)
#         self.status_progress_bar.setVisible(False)
        
#         # Re-enable parse button
#         self.parsing_widget.parse_btn.setEnabled(True)
        
#         if success:
#             self.update_workflow_step(7)
#             self.current_status_label.setText("Parsing completed - Investigation finished")
            
#             # Save parsed artifacts to case
#             for parser, success_status, output in results:
#                 self.case_manager.add_parsed_artifact({'parser': parser, 'success': success_status, 'output': output})
            
#             # Update results in a table format
#             self.update_parsing_results_table(results)
            
#             # Show parsing results summary
#             successful_parsers = [parser for parser, success_status, _ in results if success_status]
#             failed_parsers = [parser for parser, success_status, _ in results if not success_status]
            
#             result_text = f"Parsing Results Summary:\n\n"
#             result_text += f"[SUCCESS] Successful: {len(successful_parsers)} parsers\n"
#             result_text += f"[FAILED] Failed: {len(failed_parsers)} parsers\n\n"
            
#             if successful_parsers:
#                 result_text += f"Successful parsers: {', '.join(successful_parsers)}\n"
#             if failed_parsers:
#                 result_text += f"Failed parsers: {', '.join(failed_parsers)}\n"
            
#             self.log_message(result_text)
#             QMessageBox.information(self, "Success", "Artifact parsing completed successfully!")
#         else:
#             QMessageBox.critical(self, "Error", f"Parsing failed: {message}")
        
#         self.log_message(message)
    
#     def update_parsing_results_table(self, results):
#         """Update results table with parsing results"""
#         # Add parsing results to the existing results table
#         current_rows = self.results_table.rowCount()
        
#         for parser, success_status, output in results:
#             row = current_rows
#             self.results_table.insertRow(row)
            
#             # Parser name
#             self.results_table.setItem(row, 0, QTableWidgetItem(f"{parser.title()} Parser"))
            
#             # Status
#             if success_status:
#                 status_item = QTableWidgetItem("✓ Parsed")
#                 status_item.setBackground(QColor("#d1ecf1"))
#             else:
#                 status_item = QTableWidgetItem("✗ Parse Failed")
#                 status_item.setBackground(QColor("#f8d7da"))
            
#             self.results_table.setItem(row, 1, status_item)
            
#             # Location
#             self.results_table.setItem(row, 2, QTableWidgetItem(f"parsed_artifacts/{parser}"))
            
#             # Details
#             details = output if len(output) < 100 else output[:100] + "..."
#             self.results_table.setItem(row, 3, QTableWidgetItem(details))
            
#             current_rows += 1
        
#         # Resize columns
#         self.results_table.resizeColumnsToContents()
    
#     def save_case(self):
#         """Save current case"""
#         if self.case_manager.current_case:
#             self.case_manager.save_case()
#             QMessageBox.information(self, "Case Saved", "Case has been saved successfully")
#             self.log_message("Case saved successfully")
#         else:
#             QMessageBox.warning(self, "No Case", "No active case to save")
    
#     def new_investigation(self):
#         """Start new investigation"""
#         reply = QMessageBox.question(
#             self, 
#             "New Investigation", 
#             "Start a new investigation? This will reset all current progress.",
#             QMessageBox.Yes | QMessageBox.No
#         )
        
#         if reply == QMessageBox.Yes:
#             # Close any open resources
#             if self.db_conn:
#                 try:
#                     self.db_conn.close()
#                 except:
#                     pass
            
#             # Reset case manager
#             self.case_manager.current_case = None
            
#             # Reset all workflow steps
#             for step in self.workflow_steps:
#                 step.is_active = False
#                 step.is_completed = False
#                 step.step_label.setText(str(step.step_number))
#                 step.step_label.setStyleSheet("""
#                     QLabel {
#                         background-color: #e9ecef;
#                         color: #6c757d;
#                         border-radius: 20px;
#                         font-weight: bold;
#                         font-size: 16px;
#                     }
#                 """)
#                 step.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #495057;")
            
#             # Reset variables
#             self.current_image_path = None
#             self.current_partition = None
#             self.workflow_step = 0
#             self.db_conn = None
#             self.img_info = None
#             self.fs_info = None
#             self.partitions = []
#             self.auto_process = False
            
#             # Clear UI
#             self.case_name_edit.clear()
#             self.investigator_edit.clear()
#             self.image_path_edit.clear()
#             self.file_info_label.clear()
#             self.partition_widget.partition_list.clear()
#             self.artifact_widget.clear_all()
#             self.parsing_widget.clear_all()
#             self.results_table.setRowCount(0)
#             self.log_text.clear()
#             self.auto_process_checkbox.setChecked(False)
            
#             # Reset status
#             self.current_status_label.setText("Ready to start new investigation")
#             self.update_case_info()
#             self.log_message("New investigation started")
            
#             # Check database connection
#             self.check_database_connection()
    
# #     def show_about(self):
# #         """Show about dialog"""
# #         about_text = """
# # Professional Forensic Artifact Extractor v4.0 Complete

# # A comprehensive digital forensics tool with guided workflow, case management, and integrated parsing capabilities.

# # Features:
# # • Step-by-step investigation workflow
# # • Professional user interface with enhanced checkboxes
# # • Case management with automatic save/resume
# # • Auto-processing mode for hands-free operation
# # • Parse and Extract Everything button for quick processing
# # • Enhanced E01 file support
# # • Real-time progress tracking
# # • Comprehensive artifact extraction
# # • Integrated artifact parsing with multiple parsers:
# #   - Registry Parser (RegRipper integration)
# #   - Browser Parser (Hindsight integration)
# #   - System Artifacts Parser (Eric Zimmerman tools)
# # • Database integration
# # • Multi-threaded processing
# # • Robust error handling and recovery

# # Auto-Processing Mode:
# # • Extract and parse all artifacts automatically
# # • Hands-free operation after partition selection
# # • Intelligent workflow management
# # • Complete automation with user control

# # Integrated Parsers:
# # • Registry Parser: Uses RegRipper for Windows Registry analysis
# # • Browser Parser: Uses Hindsight for Chrome/Edge artifact analysis
# # • MFT Parser: Uses MFTECmd for Master File Table analysis
# # • SRUM Parser: Uses SrumECmd for SRUM database analysis
# # • Prefetch Parser: Uses PECmd for Prefetch file analysis
# # • Amcache Parser: Uses AmcacheParser for Amcache.hve analysis

# # System Requirements:
# # • Python 3.6+
# # • PyQt5
# # • pytsk3 (for file system analysis)
# # • pyewf (for E01 support)
# # • psycopg2 (for PostgreSQL support)

# # Installation:
# # pip install PyQt5 pytsk3 pyewf psycopg2

# # Built with PyQt5 for professional forensic investigations.
# #         """
        
# #         QMessageBox.about(self, "About", about_text)
#     def show_about(self):
#         """Show enhanced About dialog with scroll and styling"""

#         about_text = """
#         <h2 style='color:#2E86C1;'>Forensic Artifact Extractor & Parser v2.1.0 Complete</h2>
#         <p><i>A comprehensive digital forensics tool with guided workflow, case management, and integrated parsing capabilities.</i></p>
        
#         <h3>🚀 Features:</h3>
#         <ul>
#             <li>Step-by-step investigation workflow</li>
#             <li>Professional user interface with enhanced checkboxes</li>
#             <li>Case management with automatic save/resume</li>
#             <li>Auto-processing mode for hands-free operation</li>
#             <li>“Parse and Extract Everything” button for quick processing</li>
#             <li>Enhanced E01 file support</li>
#             <li>Real-time progress tracking</li>
#             <li>Comprehensive artifact extraction</li>
#             <li>Integrated parsing with multiple tools (RegRipper, Hindsight, etc.)</li>
#             <li>Database integration and multi-threading</li>
#             <li>Robust error handling and recovery</li>
#         </ul>

#         <h3>⚙️ Auto-Processing Mode:</h3>
#         <ul>
#             <li>Extract and parse all artifacts automatically</li>
#             <li>Hands-free operation after partition selection</li>
#             <li>Intelligent workflow management</li>
#             <li>Complete automation with user control</li>
#         </ul>

#         <h3>🧩 Integrated Parsers:</h3>
#         <ul>
#             <li><b>Registry Parser:</b> RegRipper</li>
#             <li><b>Browser Parser:</b> Hindsight (Chrome/Edge)</li>
#             <li><b>MFT Parser:</b> MFTECmd</li>
#             <li><b>SRUM Parser:</b> SrumECmd</li>
#             <li><b>Prefetch Parser:</b> PECmd</li>
#             <li><b>Amcache Parser:</b> AmcacheParser</li>
#         </ul>

#         <h3>🖥️ Requirements:</h3>
#         <ul>
#             <li>Python 3.6+</li>
#             <li>PyQt5</li>
#             <li>pytsk3</li>
#             <li>pyewf</li>
#             <li>psycopg2</li>
#         </ul>
#         """

#         dialog = QDialog(self)
#         dialog.setWindowTitle("About")
#         dialog.setMinimumSize(600, 500)

#         layout = QVBoxLayout(dialog)

#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)

#         content = QWidget()
#         content_layout = QVBoxLayout(content)

#         label = QLabel()
#         label.setTextFormat(Qt.RichText)
#         label.setText(about_text)
#         label.setWordWrap(True)

#         content_layout.addWidget(label)
#         scroll.setWidget(content)

#         layout.addWidget(scroll)

#         btn_close = QPushButton("Close")
#         btn_close.clicked.connect(dialog.accept)
#         layout.addWidget(btn_close)

#         dialog.exec_()
# def main():
#     """Main application entry point"""
#     app = QApplication(sys.argv)
    
#     # Set application properties
#     app.setApplicationName("Forensic Artifact Extractor & Parser")
#     app.setApplicationVersion("v2.1.0")
#     # app.setOrganizationName("Digital Forensics Solutions")
    
#     try:
#         window = ForensicMainWindow()
#         window.show()
        
#         logging.info("Forensic Artifact Extractor & Parser v2.1.0 started successfully")
#         sys.exit(app.exec_())
        
#     except Exception as e:
#         error_msg = f"Failed to start application: {str(e)}"
#         print(error_msg)
#         logging.error(error_msg)
        
#         try:
#             QMessageBox.critical(None, "Startup Error", error_msg)
#         except:
#             pass
        
#         sys.exit(1)

# if __name__ == "__main__":
#     # Set up exception handling
#     app = QApplication(sys.argv)
    
#     # Setup database first
#     if not setup_database():
#         sys.exit("Database setup required to continue")
    
#     # Now start the main GUI
#     window = ForensicMainWindow()
#     window.show()
#     sys.exit(app.exec_())

#     def handle_exception(exc_type, exc_value, exc_traceback):
#         if issubclass(exc_type, KeyboardInterrupt):
#             sys.__excepthook__(exc_type, exc_value, exc_traceback)
#             return
        
#         error_msg = f"Uncaught exception: {exc_type.__name__}: {exc_value}"
#         logging.error(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
        
#         # Show error dialog if GUI is available
#         try:
#             app = QApplication.instance()
#             if app:
#                 QMessageBox.critical(None, "Unexpected Error", error_msg)
#         except:
#             pass
    
#     sys.excepthook = handle_exception
    
#     # Run the application
#     main()



import sys
import os
import logging
import threading
import sqlite3
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QTreeWidget,
    QTreeWidgetItem, QTabWidget, QProgressBar, QCheckBox, QGroupBox,
    QSplitter, QFrame, QScrollArea, QFileDialog, QMessageBox, QComboBox,
    QTableWidget, QTableWidgetItem, QStatusBar, QMenuBar, QAction,
    QToolBar, QHeaderView, QListWidget, QListWidgetItem, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QScrollArea, QWidget

# Import your existing functions
try:
    from main import (
        open_db, create_table, bulk_insert, EWFImgInfo, list_directory_tree,
        extract_chrome_directory, extract_directory, extract_edge_directory,
        extract_event_logs, extract_registry_hives, extract_sru_mft_pagefile,
        extract_powershell_console_history, extract_prefetch_files, extract_activitiesCache_db
    )
except ImportError:
    print("Warning: Main module functions not available")

# Import parser functions
try:
    from registry_parser import parse_registry_artifacts
except ImportError:
    print("Warning: Registry parser not available")
    parse_registry_artifacts = None

try:
    from browser_parser import parse_browser_artifacts
except ImportError:
    print("Warning: Browser parser not available")
    parse_browser_artifacts = None

try:
    from mft_amcache_pf_sru_parser import parse_system_artifacts
except ImportError:
    print("Warning: System artifacts parser not available")
    parse_system_artifacts = None

try:
    import pytsk3
    import pyewf
    import psycopg2
    FORENSIC_LIBS_AVAILABLE = True
except ImportError:
    FORENSIC_LIBS_AVAILABLE = False
    print("Warning: Forensic libraries not available")

class CaseManager:
    """Case management system for forensic investigations"""
    
    def __init__(self):
        self.case_file = "case_config.json"
        self.current_case = None
        
    def create_case(self, case_name, image_path, investigator=""):
        """Create a new case"""
        case_data = {
            'case_name': case_name,
            'image_path': image_path,
            'investigator': investigator,
            'created_date': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'status': 'created',
            'workflow_stage': 0,
            'partitions': [],
            'selected_partition': None,
            'extracted_artifacts': [],
            'parsed_artifacts': []
        }
        
        with open(self.case_file, 'w') as f:
            json.dump(case_data, f, indent=4)
        
        self.current_case = case_data
        return case_data
    
    def load_case(self):
        """Load existing case"""
        if os.path.exists(self.case_file):
            try:
                with open(self.case_file, 'r') as f:
                    self.current_case = json.load(f)
                return self.current_case
            except Exception as e:
                print(f"Error loading case: {e}")
                return None
        return None
    
    def save_case(self):
        """Save current case"""
        if self.current_case:
            self.current_case['last_modified'] = datetime.now().isoformat()
            with open(self.case_file, 'w') as f:
                json.dump(self.current_case, f, indent=4)
    
    def update_case_status(self, status, workflow_stage=None):
        """Update case status"""
        if self.current_case:
            self.current_case['status'] = status
            if workflow_stage is not None:
                self.current_case['workflow_stage'] = workflow_stage
            self.save_case()
    
    def set_partitions(self, partitions):
        """Set partitions for the case (remove non-serializable objects)"""
        if self.current_case:
            # Create serializable partition data
            serializable_partitions = []
            for partition in partitions:
                serializable_partition = {
                    'addr': partition['addr'],
                    'start': partition['start'],
                    'length': partition['length'],
                    'description': partition['description'],
                    'size_mb': partition['size_mb']
                    # Note: We don't save 'partition_obj' as it's not JSON serializable
                }
                serializable_partitions.append(serializable_partition)
            
            self.current_case['partitions'] = serializable_partitions
            self.save_case()
    
    def set_selected_partition(self, partition):
        """Set selected partition (remove non-serializable objects)"""
        if self.current_case:
            # Create serializable partition data
            serializable_partition = {
                'addr': partition['addr'],
                'start': partition['start'],
                'length': partition['length'],
                'description': partition['description'],
                'size_mb': partition['size_mb']
            }
            self.current_case['selected_partition'] = serializable_partition
            self.save_case()
    
    def add_extracted_artifact(self, artifact):
        """Add extracted artifact"""
        if self.current_case:
            if 'extracted_artifacts' not in self.current_case:
                self.current_case['extracted_artifacts'] = []
            self.current_case['extracted_artifacts'].append(artifact)
            self.save_case()
    
    def add_parsed_artifact(self, artifact):
        """Add parsed artifact"""
        if self.current_case:
            if 'parsed_artifacts' not in self.current_case:
                self.current_case['parsed_artifacts'] = []
            self.current_case['parsed_artifacts'].append(artifact)
            self.save_case()

class DatabaseConnectionThread(QThread):
    """Thread for testing database connection"""
    connection_result = pyqtSignal(bool, str)
    
    def run(self):
        try:
            logging.info("Testing database connection...")
            conn = open_db()
            if conn:
                logging.info("Connection successful")
                
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()[0]
                    logging.info(f"PostgreSQL version: {version}")
                    
                    # Test table creation
                    create_table(conn)
                    logging.info("Table creation successful")
                    
                    # Test insertion
                    test_record = [("/test_path", "test_file", "File", 0, None, None, None, "/")]
                    logging.info("Testing record insertion...")
                    bulk_insert(conn, test_record)
                    
                    # Verify insertion
                    cursor.execute("SELECT COUNT(*) FROM file_tree WHERE path = '/test_path'")
                    count = cursor.fetchone()[0]
                    logging.info(f"Test record found in database: {count > 0}")
                    
                conn.close()
                logging.info("Database test complete")
                self.connection_result.emit(True, "Database connection successful")
            else:
                self.connection_result.emit(False, "Failed to connect to database")
        except Exception as e:
            logging.error(f"Database test failed: {str(e)}")
            self.connection_result.emit(False, f"Database Error: {str(e)}")

class ImageLoadingThread(QThread):
    """Thread for loading evidence image"""
    progress_update = pyqtSignal(str)
    partitions_found = pyqtSignal(list)
    loading_complete = pyqtSignal(bool, str)
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        
    def run(self):
        try:
            if not FORENSIC_LIBS_AVAILABLE:
                self.loading_complete.emit(False, "Forensic libraries (pytsk3, pyewf) not available")
                return
                
            self.progress_update.emit("Processing image...\nThis may take several minutes.")
            
            # Validate file exists
            if not os.path.exists(self.image_path):
                self.loading_complete.emit(False, f"File does not exist: {self.image_path}")
                return
            
            logging.info(f"Processing image: {self.image_path}")
            
            # Open EWF image
            image_path = os.path.normpath(self.image_path)
            filenames = pyewf.glob(image_path)
            ewf_handle = pyewf.handle()
            ewf_handle.open(filenames)
            img_info = EWFImgInfo(ewf_handle)
            logging.info("Image opened successfully")
            
            self.progress_update.emit("Analyzing partition table...")
            
            try:
                volume = pytsk3.Volume_Info(img_info)
                partitions = []
                
                for part in volume:
                    desc = part.desc.decode('utf-8', 'ignore') if part.desc else "Unknown"
                    part_info = {
                        'addr': part.addr,
                        'start': part.start,
                        'length': part.len,
                        'description': desc,
                        'size_mb': (part.len * 512) // (1024 * 1024),
                        'partition_obj': part  # Keep this for runtime use, but don't serialize
                    }
                    partitions.append(part_info)
                    logging.info(f"Found partition {part.addr}: {desc}")
                
                if partitions:
                    self.img_info = img_info
                    self.partitions_found.emit(partitions)
                    self.loading_complete.emit(True, "Image loaded successfully")
                else:
                    self.loading_complete.emit(False, "No partitions found in the image.")
                    
            except Exception as e:
                self.loading_complete.emit(False, f"Error processing volume: {str(e)}")
                logging.error(f"Error processing volume: {str(e)}")
                
        except Exception as e:
            self.loading_complete.emit(False, f"Error processing image: {str(e)}")
            logging.error(f"Error processing image: {str(e)}")

class FileSystemScanThread(QThread):
    """Thread for scanning file system"""
    progress_update = pyqtSignal(str)
    scan_complete = pyqtSignal(bool, str, dict)
    
    def __init__(self, img_info, partition, db_conn):
        super().__init__()
        self.img_info = img_info
        self.partition = partition
        self.db_conn = db_conn
        
    def run(self):
        try:
            self.progress_update.emit(f"Initializing file system at offset {self.partition['start'] * 512}")
            
            # Initialize file system information
            fs_info = pytsk3.FS_Info(self.img_info, offset=self.partition['start'] * 512)
            root_dir = fs_info.open_dir(path="/")
            
            # List root directory contents
            root_content = "\nRoot directory contents:\n"
            for entry in root_dir:
                try:
                    name = entry.info.name.name.decode('utf-8', errors='replace')
                    root_content += f"- {name}\n"
                except Exception:
                    continue
            
            self.progress_update.emit(root_content)
            
            # Scan the entire file system
            self.progress_update.emit("Scanning file system...\nThis may take several minutes.")
            
            logging.info("Starting full file system scan...")
            counts, records = list_directory_tree(fs_info, root_dir, "/")
            logging.info(f"Scan complete: Found {counts['directories']} directories and {counts['files']} files")
            
            # Insert records into database
            logging.info(f"Inserting {len(records)} records into database...")
            bulk_insert(self.db_conn, records)
            logging.info("Database insertion complete")
            
            result_info = {
                'fs_info': fs_info,
                'counts': counts,
                'records_count': len(records)
            }
            
            self.scan_complete.emit(True, f"Scan complete!\n\nFound {counts['directories']} directories and {counts['files']} files", result_info)
            
        except Exception as e:
            self.scan_complete.emit(False, f"Error scanning file system: {str(e)}", {})
            logging.error(f"Error scanning file system: {str(e)}")

class ArtifactExtractionThread(QThread):
    """Thread for extracting artifacts"""
    progress_update = pyqtSignal(str)
    extraction_complete = pyqtSignal(bool, str, list)
    
    def __init__(self, fs_info, db_conn, selected_options):
        super().__init__()
        self.fs_info = fs_info
        self.db_conn = db_conn
        self.selected_options = selected_options
        
    def run(self):
        try:
            results = []
            
            for option in self.selected_options:
                if option == "1":  # Registry Hives
                    self.progress_update.emit("Extracting Registry Hives...")
                    reg_out = os.path.join("output", "registry")
                    result = extract_registry_hives(self.fs_info, self.db_conn, reg_out)
                    results.append(("Registry hives", result))
                    
                elif option == "2":  # Event Logs
                    self.progress_update.emit("Extracting Event Logs...")
                    logs_output = os.path.join("output", "eventlogs")
                    result = extract_event_logs(self.fs_info, self.db_conn, logs_output)
                    results.append(("Event logs", result))
                    
                elif option == "3":  # Edge
                    self.progress_update.emit("Extracting Edge Browser Data...")
                    edge_output = os.path.join("output", "browser", "edge")
                    result = extract_edge_directory(self.fs_info, self.db_conn, edge_output)
                    results.append(("Edge browser", result))
                    
                elif option == "4":  # Chrome
                    self.progress_update.emit("Extracting Chrome Browser Data...")
                    chrome_out = os.path.join("output", "browser", "chrome")
                    result = extract_chrome_directory(self.fs_info, self.db_conn, chrome_out)
                    results.append(("Chrome browser", result))
                    
                elif option == "5":  # MFT, Pagefile, SRUDB
                    self.progress_update.emit("Extracting MFT, Pagefile, SRUDB...")
                    mft_output = "output"
                    result = extract_sru_mft_pagefile(self.fs_info, self.db_conn, mft_output)
                    results.append(("MFT/Pagefile/SRUDB", result))
                    
                elif option == "6":  # PowerShell History
                    self.progress_update.emit("Extracting PowerShell Console History...")
                    consolehistory_output = "output"
                    result = extract_powershell_console_history(self.fs_info, self.db_conn, consolehistory_output)
                    results.append(("PowerShell history", result))
                    
                elif option == "7":  # Prefetch Files
                    self.progress_update.emit("Extracting Prefetch Files...")
                    prefetch_output = "output"
                    result = extract_prefetch_files(self.fs_info, self.db_conn, prefetch_output)
                    results.append(("Prefetch files", result))
                    
                elif option == "8":  # ActivityCache.db
                    self.progress_update.emit("Extracting ActivityCache.db...")
                    activecache_output = "output"
                    result = extract_activitiesCache_db(self.fs_info, self.db_conn, activecache_output)
                    results.append(("ActivityCache.db", result))
            
            self.extraction_complete.emit(True, "Artifact extraction completed", results)
            
        except Exception as e:
            self.extraction_complete.emit(False, f"Extraction failed: {str(e)}", [])

class ParsingThread(QThread):
    """Enhanced thread for parsing artifacts with proper parser integration"""
    progress_update = pyqtSignal(str)
    parsing_complete = pyqtSignal(bool, str, list)
    
    def __init__(self, selected_parsers):
        super().__init__()
        self.selected_parsers = selected_parsers
        
    def run(self):
        try:
            results = []
            overall_success = True
            
            self.progress_update.emit(f"Starting parsing with selected parsers: {', '.join(self.selected_parsers)}")
            
            # Registry Parser
            if 'registry' in self.selected_parsers:
                try:
                    self.progress_update.emit("Starting Registry parsing...")
                    
                    if parse_registry_artifacts is None:
                        raise ImportError("Registry parser not available")
                    
                    result = parse_registry_artifacts(
                        registry_folder="output/registry",
                        progress_callback=self.progress_update.emit
                    )
                    
                    if result['success']:
                        results.append(('registry', True, result['summary']))
                        self.progress_update.emit(f"[SUCCESS] Registry parsing completed: {result['summary']}")
                    else:
                        results.append(('registry', False, result.get('error', 'Unknown error')))
                        self.progress_update.emit(f"[FAILED] Registry parsing failed: {result.get('error', 'Unknown error')}")
                        overall_success = False
                        
                except Exception as e:
                    error_msg = f"Registry parsing error: {str(e)}"
                    results.append(('registry', False, error_msg))
                    self.progress_update.emit(f"[FAILED] {error_msg}")
                    overall_success = False
            
            # Browser Parser
            if 'browser' in self.selected_parsers:
                try:
                    self.progress_update.emit("Starting Browser parsing...")
                    
                    if parse_browser_artifacts is None:
                        raise ImportError("Browser parser not available")
                    
                    result = parse_browser_artifacts(
                        browser_folder="output/browser",
                        progress_callback=self.progress_update.emit
                    )
                    
                    if result['success']:
                        results.append(('browser', True, result['summary']))
                        self.progress_update.emit(f"[SUCCESS] Browser parsing completed: {result['summary']}")
                    else:
                        results.append(('browser', False, result.get('error', 'Unknown error')))
                        self.progress_update.emit(f"[FAILED] Browser parsing failed: {result.get('error', 'Unknown error')}")
                        overall_success = False
                        
                except Exception as e:
                    error_msg = f"Browser parsing error: {str(e)}"
                    results.append(('browser', False, error_msg))
                    self.progress_update.emit(f"[FAILED] {error_msg}")
                    overall_success = False
            
            # System Artifacts Parser (MFT, Amcache, Prefetch, SRUM)
            system_parsers = []
            if 'mft' in self.selected_parsers:
                system_parsers.append('mft')
            if 'prefetch' in self.selected_parsers:
                system_parsers.append('prefetch')
            if 'activities' in self.selected_parsers:  # This maps to amcache
                system_parsers.append('amcache')
            if 'eventlogs' in self.selected_parsers:  # This maps to srum
                system_parsers.append('srum')
            
            if system_parsers:
                try:
                    self.progress_update.emit(f"Starting System artifacts parsing: {', '.join(system_parsers)}")
                    
                    if parse_system_artifacts is None:
                        raise ImportError("System artifacts parser not available")
                    
                    result = parse_system_artifacts(
                        selected_parsers=system_parsers,
                        input_path="output",
                        progress_callback=self.progress_update.emit
                    )
                    
                    if result['success']:
                        # Add individual results for each system parser
                        for parser in system_parsers:
                            if parser in result['results']:
                                parser_result = result['results'][parser]
                                results.append((parser, parser_result['success'], parser_result['summary']))
                                status = "[SUCCESS]" if parser_result['success'] else "[FAILED]"
                                self.progress_update.emit(f"{status} {parser.upper()} parsing: {parser_result['summary']}")
                    else:
                        for parser in system_parsers:
                            results.append((parser, False, result.get('error', 'Unknown error')))
                            self.progress_update.emit(f"[FAILED] {parser.upper()} parsing failed: {result.get('error', 'Unknown error')}")
                        overall_success = False
                        
                except Exception as e:
                    error_msg = f"System artifacts parsing error: {str(e)}"
                    for parser in system_parsers:
                        results.append((parser, False, error_msg))
                        self.progress_update.emit(f"[FAILED] {parser.upper()} parsing error: {str(e)}")
                    overall_success = False
            
            # PowerShell Parser (if selected separately)
            if 'powershell' in self.selected_parsers:
                try:
                    self.progress_update.emit("Starting PowerShell history parsing...")
                    
                    # For now, we'll add a placeholder since PowerShell parsing might be part of system artifacts
                    # You can implement a separate PowerShell parser if needed
                    results.append(('powershell', True, 'PowerShell parsing completed (placeholder)'))
                    self.progress_update.emit("[SUCCESS] PowerShell parsing completed")
                    
                except Exception as e:
                    error_msg = f"PowerShell parsing error: {str(e)}"
                    results.append(('powershell', False, error_msg))
                    self.progress_update.emit(f"[FAILED] {error_msg}")
                    overall_success = False
            
            # Generate final summary
            successful_count = sum(1 for _, success, _ in results if success)
            total_count = len(results)
            
            final_message = f"Parsing completed: {successful_count}/{total_count} parsers successful"
            self.progress_update.emit(final_message)
            
            self.parsing_complete.emit(overall_success, final_message, results)
            
        except Exception as e:
            error_msg = f"Parsing failed: {str(e)}"
            self.progress_update.emit(error_msg)
            self.parsing_complete.emit(False, error_msg, [])

class AutoProcessingThread(QThread):
    """Thread for automatic processing of everything"""
    progress_update = pyqtSignal(str)
    processing_complete = pyqtSignal(bool, str)
    
    def __init__(self, img_info, partition, db_conn, fs_info):
        super().__init__()
        self.img_info = img_info
        self.partition = partition
        self.db_conn = db_conn
        self.fs_info = fs_info
        
    def run(self):
        try:
            self.progress_update.emit("Starting automatic processing...")
            
            # Extract all artifacts
            self.progress_update.emit("Extracting all artifacts...")
            all_artifacts = ["1", "2", "3", "4", "5", "6", "7", "8"]
            
            extraction_results = []
            for option in all_artifacts:
                try:
                    if option == "1":  # Registry Hives
                        self.progress_update.emit("Auto-extracting Registry Hives...")
                        reg_out = os.path.join("output", "registry")
                        result = extract_registry_hives(self.fs_info, self.db_conn, reg_out)
                        extraction_results.append(("Registry hives", result))
                        
                    elif option == "2":  # Event Logs
                        self.progress_update.emit("Auto-extracting Event Logs...")
                        logs_output = os.path.join("output", "eventlogs")
                        result = extract_event_logs(self.fs_info, self.db_conn, logs_output)
                        extraction_results.append(("Event logs", result))
                        
                    elif option == "3":  # Edge
                        self.progress_update.emit("Auto-extracting Edge Browser Data...")
                        edge_output = os.path.join("output", "browser", "edge")
                        result = extract_edge_directory(self.fs_info, self.db_conn, edge_output)
                        extraction_results.append(("Edge browser", result))
                        
                    elif option == "4":  # Chrome
                        self.progress_update.emit("Auto-extracting Chrome Browser Data...")
                        chrome_out = os.path.join("output", "browser", "chrome")
                        result = extract_chrome_directory(self.fs_info, self.db_conn, chrome_out)
                        extraction_results.append(("Chrome browser", result))
                        
                    elif option == "5":  # MFT, Pagefile, SRUDB
                        self.progress_update.emit("Auto-extracting MFT, Pagefile, SRUDB...")
                        mft_output = "output"
                        result = extract_sru_mft_pagefile(self.fs_info, self.db_conn, mft_output)
                        extraction_results.append(("MFT/Pagefile/SRUDB", result))
                        
                    elif option == "6":  # PowerShell History
                        self.progress_update.emit("Auto-extracting PowerShell Console History...")
                        consolehistory_output = "output"
                        result = extract_powershell_console_history(self.fs_info, self.db_conn, consolehistory_output)
                        extraction_results.append(("PowerShell history", result))
                        
                    elif option == "7":  # Prefetch Files
                        self.progress_update.emit("Auto-extracting Prefetch Files...")
                        prefetch_output = "output"
                        result = extract_prefetch_files(self.fs_info, self.db_conn, prefetch_output)
                        extraction_results.append(("Prefetch files", result))
                        
                    elif option == "8":  # ActivityCache.db
                        self.progress_update.emit("Auto-extracting ActivityCache.db...")
                        activecache_output = "output"
                        result = extract_activitiesCache_db(self.fs_info, self.db_conn, activecache_output)
                        extraction_results.append(("ActivityCache.db", result))
                        
                except Exception as e:
                    self.progress_update.emit(f"Error extracting {option}: {str(e)}")
            
            # Parse all artifacts
            self.progress_update.emit("Parsing all artifacts...")
            all_parsers = ['registry', 'browser', 'mft', 'prefetch', 'activities', 'eventlogs']
            
            parsing_results = []
            
            # Registry Parser
            if parse_registry_artifacts is not None:
                try:
                    self.progress_update.emit("Auto-parsing Registry...")
                    result = parse_registry_artifacts(
                        registry_folder="output/registry",
                        progress_callback=self.progress_update.emit
                    )
                    if result['success']:
                        parsing_results.append(('registry', True, result['summary']))
                    else:
                        parsing_results.append(('registry', False, result.get('error', 'Unknown error')))
                except Exception as e:
                    parsing_results.append(('registry', False, str(e)))
            
            # Browser Parser
            if parse_browser_artifacts is not None:
                try:
                    self.progress_update.emit("Auto-parsing Browser...")
                    result = parse_browser_artifacts(
                        browser_folder="output/browser",
                        progress_callback=self.progress_update.emit
                    )
                    if result['success']:
                        parsing_results.append(('browser', True, result['summary']))
                    else:
                        parsing_results.append(('browser', False, result.get('error', 'Unknown error')))
                except Exception as e:
                    parsing_results.append(('browser', False, str(e)))
            
            # System Artifacts Parser
            if parse_system_artifacts is not None:
                try:
                    self.progress_update.emit("Auto-parsing System Artifacts...")
                    system_parsers = ['mft', 'srum', 'prefetch', 'amcache']
                    result = parse_system_artifacts(
                        selected_parsers=system_parsers,
                        input_path="output",
                        progress_callback=self.progress_update.emit
                    )
                    
                    if result['success']:
                        for parser in system_parsers:
                            if parser in result['results']:
                                parser_result = result['results'][parser]
                                parsing_results.append((parser, parser_result['success'], parser_result['summary']))
                    else:
                        for parser in system_parsers:
                            parsing_results.append((parser, False, result.get('error', 'Unknown error')))
                except Exception as e:
                    for parser in ['mft', 'srum', 'prefetch', 'amcache']:
                        parsing_results.append((parser, False, str(e)))
            
            # Generate summary
            extraction_success = sum(1 for _, success in extraction_results if success)
            parsing_success = sum(1 for _, success, _ in parsing_results if success)
            
            summary = f"Auto-processing completed!\nExtracted: {extraction_success}/{len(extraction_results)} artifacts\nParsed: {parsing_success}/{len(parsing_results)} parsers"
            
            self.processing_complete.emit(True, summary)
            
        except Exception as e:
            self.processing_complete.emit(False, f"Auto-processing failed: {str(e)}")

class WorkflowStepWidget(QFrame):
    """Custom widget for workflow steps"""
    def __init__(self, step_number, title, description, parent=None):
        super().__init__(parent)
        self.step_number = step_number
        self.title = title
        self.description = description
        self.is_active = False
        self.is_completed = False
        self.init_ui()
        
    def init_ui(self):
        self.setFrameStyle(QFrame.StyledPanel)
        layout = QHBoxLayout(self)
        
        # Step number circle
        self.step_label = QLabel(str(self.step_number))
        self.step_label.setFixedSize(40, 40)
        self.step_label.setAlignment(Qt.AlignCenter)
        self.step_label.setStyleSheet("""
            QLabel {
                background-color: #e9ecef;
                color: #6c757d;
                border-radius: 20px;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        
        # Step content
        content_layout = QVBoxLayout()
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #495057;")
        
        self.desc_label = QLabel(self.description)
        self.desc_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        
        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.desc_label)
        
        layout.addWidget(self.step_label)
        layout.addLayout(content_layout)
        layout.addStretch()
        
    def set_active(self):
        self.is_active = True
        self.step_label.setStyleSheet("""
            QLabel {
                background-color: #007bff;
                color: white;
                border-radius: 20px;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #007bff;")
        
    def set_completed(self):
        self.is_completed = True
        self.is_active = False
        self.step_label.setText("✓")
        self.step_label.setStyleSheet("""
            QLabel {
                background-color: #28a745;
                color: white;
                border-radius: 20px;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #28a745;")

class PartitionSelectionWidget(QGroupBox):
    """Widget for selecting partition"""
    def __init__(self):
        super().__init__("Partition Selection")
        self.partitions = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.partition_list = QListWidget()
        self.partition_list.setAlternatingRowColors(True)
        layout.addWidget(self.partition_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.select_btn = QPushButton("Select Partition")
        self.select_btn.setEnabled(False)
        self.refresh_btn = QPushButton("Refresh")
        
        # NEW: Parse and Extract Everything button
        self.auto_process_btn = QPushButton("Parse and Extract Everything")
        self.auto_process_btn.setEnabled(False)
        self.auto_process_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.auto_process_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Connect signals
        self.partition_list.itemSelectionChanged.connect(self.on_selection_changed)
        
    def update_partitions(self, partitions):
        self.partitions = partitions
        self.partition_list.clear()
        
        for i, partition in enumerate(partitions):
            item_text = f"{partition['description']} (Partition {partition['addr']}) - {partition['size_mb']} MB"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i)
            self.partition_list.addItem(item)
            
    def on_selection_changed(self):
        has_selection = len(self.partition_list.selectedItems()) > 0
        self.select_btn.setEnabled(has_selection)
        self.auto_process_btn.setEnabled(has_selection)
        
    def get_selected_partition(self):
        selected_items = self.partition_list.selectedItems()
        if selected_items:
            index = selected_items[0].data(Qt.UserRole)
            return self.partitions[index]
        return None

class ArtifactSelectionWidget(QGroupBox):
    """Enhanced widget for selecting artifacts to extract with better spacing"""
    def __init__(self):
        super().__init__("Artifact Selection")
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)  # Add more spacing between sections
        
        # Artifact categories with better spacing
        categories = {
            "System Artifacts": {
                '1': ('Registry Hives', 'Windows Registry files containing system and user settings'),
                '2': ('Event Logs', 'Windows Event Logs for system activity tracking'),
                '5': ('MFT, Pagefile, SRUDB', 'Master File Table, Pagefile, and SRUDB'),
                '7': ('Prefetch Files', 'Application execution artifacts')
            },
            "User Activity": {
                '4': ('Chrome Browser Data', 'Browsing history, downloads, and cache'),
                '3': ('Edge Browser Data', 'Microsoft Edge browsing artifacts'),
                '6': ('PowerShell Console History', 'PowerShell console command history'),
                '8': ('ActivityCache.db', 'Windows Timeline and activity data')
            }
        }
        
        self.artifacts = {}
        
        for category, items in categories.items():
            category_group = QGroupBox(category)
            category_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    font-size: 14px;
                    color: #2c3e50;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    margin-top: 15px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 10px;
                    background-color: #ffffff;
                }
            """)
            
            category_layout = QGridLayout()
            category_layout.setSpacing(15)  # More spacing between checkboxes
            category_layout.setContentsMargins(20, 20, 20, 20)  # More padding
            
            row = 0
            col = 0
            for key, (name, desc) in items.items():
                checkbox = QCheckBox(name)
                checkbox.setToolTip(desc)
                checkbox.setStyleSheet("""
                    QCheckBox {
                        font-size: 13px;
                        font-weight: 500;
                        color: #34495e;
                        spacing: 10px;
                        padding: 8px;
                    }
                    QCheckBox::indicator {
                        width: 20px;
                        height: 20px;
                        border-radius: 4px;
                        border: 2px solid #bdc3c7;
                        background-color: #ffffff;
                    }
                    QCheckBox::indicator:hover {
                        border-color: #3498db;
                        background-color: #ecf0f1;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #3498db;
                        border-color: #3498db;
                        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjIgNy44TDEuNCA1IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
                    }
                    QCheckBox::indicator:checked:hover {
                        background-color: #2980b9;
                        border-color: #2980b9;
                    }
                """)
                
                self.artifacts[key] = checkbox
                
                category_layout.addWidget(checkbox, row, col)
                col += 1
                if col > 1:
                    col = 0
                    row += 1
                    
            category_group.setLayout(category_layout)
            layout.addWidget(category_group)
        
        # Control buttons with better styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(20, 20, 20, 20)
        
        self.select_all_btn = QPushButton("Select All")
        self.clear_all_btn = QPushButton("Clear All")
        self.extract_btn = QPushButton("Extract Selected Artifacts")
        self.extract_btn.setEnabled(False)
        
        # Style buttons
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        
        self.select_all_btn.setStyleSheet(button_style)
        self.clear_all_btn.setStyleSheet(button_style)
        self.extract_btn.setStyleSheet(button_style.replace("#3498db", "#27ae60").replace("#2980b9", "#229954").replace("#21618c", "#1e8449"))
        
        self.select_all_btn.clicked.connect(self.select_all)
        self.clear_all_btn.clicked.connect(self.clear_all)
        
        # Connect checkboxes to update extract button
        for checkbox in self.artifacts.values():
            checkbox.toggled.connect(self.update_extract_button)
        
        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.clear_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.extract_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def select_all(self):
        for checkbox in self.artifacts.values():
            checkbox.setChecked(True)
    
    def clear_all(self):
        for checkbox in self.artifacts.values():
            checkbox.setChecked(False)
            
    def update_extract_button(self):
        has_selection = any(checkbox.isChecked() for checkbox in self.artifacts.values())
        self.extract_btn.setEnabled(has_selection)
    
    def get_selected_artifacts(self):
        return [key for key, checkbox in self.artifacts.items() if checkbox.isChecked()]

class ParsingSelectionWidget(QGroupBox):
    """Widget for selecting parsers to run"""
    def __init__(self):
        super().__init__("Parser Selection")
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Parser categories with better spacing
        categories = {
            "System Parsers": {
                'registry': ('Registry Parser', 'Parse Windows Registry files for system configuration and user activity'),
                'eventlogs': ('Event Log Parser', 'Parse Windows Event Logs for system events and security incidents'),
                'mft': ('MFT Parser', 'Parse Master File Table for file system timeline'),
                'prefetch': ('Prefetch Parser', 'Parse Prefetch files for application execution artifacts')
            },
            "User Activity Parsers": {
                'browser': ('Browser Parser', 'Parse browser artifacts for web activity'),
                'powershell': ('PowerShell Parser', 'Parse PowerShell console history'),
                'activities': ('Activities Parser', 'Parse Windows Timeline and activity data')
            }
        }
        
        self.parsers = {}
        
        for category, items in categories.items():
            category_group = QGroupBox(category)
            category_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    font-size: 14px;
                    color: #2c3e50;
                    border: 2px solid #e67e22;
                    border-radius: 8px;
                    margin-top: 15px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 10px;
                    background-color: #ffffff;
                }
            """)
            
            category_layout = QGridLayout()
            category_layout.setSpacing(15)
            category_layout.setContentsMargins(20, 20, 20, 20)
            
            row = 0
            col = 0
            for key, (name, desc) in items.items():
                checkbox = QCheckBox(name)
                checkbox.setToolTip(desc)
                checkbox.setStyleSheet("""
                    QCheckBox {
                        font-size: 13px;
                        font-weight: 500;
                        color: #34495e;
                        spacing: 10px;
                        padding: 8px;
                    }
                    QCheckBox::indicator {
                        width: 20px;
                        height: 20px;
                        border-radius: 4px;
                        border: 2px solid #e67e22;
                        background-color: #ffffff;
                    }
                    QCheckBox::indicator:hover {
                        border-color: #e67e22;
                        background-color: #fdf2e9;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #e67e22;
                        border-color: #e67e22;
                        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjIgNy44TDEuNCA1IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
                    }
                    QCheckBox::indicator:checked:hover {
                        background-color: #d35400;
                        border-color: #d35400;
                    }
                """)
                
                self.parsers[key] = checkbox
                
                category_layout.addWidget(checkbox, row, col)
                col += 1
                if col > 1:
                    col = 0
                    row += 1
                    
            category_group.setLayout(category_layout)
            layout.addWidget(category_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(20, 20, 20, 20)
        
        self.select_all_btn = QPushButton("Select All")
        self.clear_all_btn = QPushButton("Clear All")
        self.parse_btn = QPushButton("Parse Selected Artifacts")
        self.parse_btn.setEnabled(False)
        
        # Style buttons
        button_style = """
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        
        self.select_all_btn.setStyleSheet(button_style)
        self.clear_all_btn.setStyleSheet(button_style)
        self.parse_btn.setStyleSheet(button_style.replace("#e67e22", "#8e44ad").replace("#d35400", "#7d3c98").replace("#ba4a00", "#6c3483"))
        
        self.select_all_btn.clicked.connect(self.select_all)
        self.clear_all_btn.clicked.connect(self.clear_all)
        
        # Connect checkboxes to update parse button
        for checkbox in self.parsers.values():
            checkbox.toggled.connect(self.update_parse_button)
        
        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.clear_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.parse_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def select_all(self):
        for checkbox in self.parsers.values():
            checkbox.setChecked(True)
    
    def clear_all(self):
        for checkbox in self.parsers.values():
            checkbox.setChecked(False)
            
    def update_parse_button(self):
        has_selection = any(checkbox.isChecked() for checkbox in self.parsers.values())
        self.parse_btn.setEnabled(has_selection)
    
    def get_selected_parsers(self):
        return [key for key, checkbox in self.parsers.items() if checkbox.isChecked()]

class ForensicMainWindow(QMainWindow):
    """Main application window with professional forensic workflow"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.current_partition = None
        self.db_connected = False
        self.workflow_step = 0
        self.image_thread = None
        self.db_conn = None
        self.img_info = None
        self.fs_info = None
        self.partitions = []
        self.auto_process = False
        
        # Initialize case manager
        self.case_manager = CaseManager()
        
        # Configure logging with UTF-8 encoding
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("forensic_tool.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.init_ui()
        self.apply_professional_style()
        
        # Check for existing case
        self.check_existing_case()
        
        if not self.case_manager.current_case:
            self.check_database_connection()
    
    def check_existing_case(self):
        """Check for existing case and load if available"""
        existing_case = self.case_manager.load_case()
        if existing_case:
            reply = QMessageBox.question(
                self,
                "Existing Case Found",
                f"Found existing case: {existing_case['case_name']}\n"
                f"Created: {existing_case['created_date']}\n"
                f"Status: {existing_case['status']}\n"
                f"Workflow Stage: {existing_case['workflow_stage']}\n\n"
                "Do you want to continue with this case?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.load_existing_case(existing_case)
            else:
                self.new_investigation()
    
    def load_existing_case(self, case_data):
        """Load existing case and resume from last stage"""
        self.current_image_path = case_data['image_path']
        self.image_path_edit.setText(self.current_image_path)
        
        # Update workflow to last completed stage
        workflow_stage = case_data.get('workflow_stage', 0)
        self.update_workflow_step(workflow_stage)
        
        # Set status based on workflow stage
        if workflow_stage >= 1:
            self.db_connected = True
            self.db_status_label.setText("Connected")
            self.db_status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            self.db_status_indicator.setText("DB: Connected")
            self.db_status_indicator.setStyleSheet("color: #28a745; font-weight: bold;")
        
        if workflow_stage >= 2 and 'partitions' in case_data:
            self.partitions = case_data['partitions']
            self.partition_widget.update_partitions(self.partitions)
            
        if workflow_stage >= 3 and 'selected_partition' in case_data:
            self.current_partition = case_data['selected_partition']
            
        # Set appropriate status message
        if workflow_stage == 0:
            self.current_status_label.setText("Case loaded - Check database connection")
        elif workflow_stage == 1:
            self.current_status_label.setText("Case loaded - Load evidence image")
        elif workflow_stage == 2:
            self.current_status_label.setText("Case loaded - Select partition")
        elif workflow_stage == 3:
            self.current_status_label.setText("Case loaded - Scan file system")
        elif workflow_stage >= 4:
            self.current_status_label.setText("Case loaded - Ready for artifact extraction")
            self.tab_widget.setCurrentIndex(2)  # Go to artifact tab
        
        self.log_message(f"Loaded existing case: {case_data['case_name']}")
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Forensic Artifact Extractor & Parser v2.1.0")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left panel - Workflow
        left_panel = self.create_workflow_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel - Content
        right_panel = self.create_content_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([400, 1200])
        
        # Create status bar
        self.create_status_bar()
    
    def create_menu_bar(self):
        """Create professional menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_case_action = QAction('&New Investigation', self)
        new_case_action.setShortcut('Ctrl+N')
        new_case_action.triggered.connect(self.new_investigation)
        file_menu.addAction(new_case_action)
        
        load_image_action = QAction('&Load Evidence Image', self)
        load_image_action.setShortcut('Ctrl+O')
        load_image_action.triggered.connect(self.load_evidence_image)
        file_menu.addAction(load_image_action)
        
        file_menu.addSeparator()
        
        save_case_action = QAction('&Save Case', self)
        save_case_action.setShortcut('Ctrl+S')
        save_case_action.triggered.connect(self.save_case)
        file_menu.addAction(save_case_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        db_test_action = QAction('Test &Database Connection', self)
        db_test_action.triggered.connect(self.check_database_connection)
        tools_menu.addAction(db_test_action)
        
        libs_check_action = QAction('Check &Libraries', self)
        libs_check_action.triggered.connect(self.check_libraries)
        tools_menu.addAction(libs_check_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_workflow_panel(self):
        """Create left panel with workflow steps"""
        workflow_widget = QWidget()
        layout = QVBoxLayout(workflow_widget)
        
        # Workflow title
        title_label = QLabel("Investigation Workflow")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px;")
        layout.addWidget(title_label)
        
        # Case information
        case_group = QGroupBox("Case Information")
        case_layout = QVBoxLayout()
        
        self.case_info_label = QLabel("No case loaded")
        self.case_info_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        case_layout.addWidget(self.case_info_label)
        
        case_group.setLayout(case_layout)
        layout.addWidget(case_group)
        
        # Library status
        lib_status_group = QGroupBox("System Status")
        lib_layout = QVBoxLayout()
        
        self.lib_status_label = QLabel("Checking libraries...")
        lib_layout.addWidget(self.lib_status_label)
        
        lib_status_group.setLayout(lib_layout)
        layout.addWidget(lib_status_group)
        
        # Workflow steps
        self.workflow_steps = []
        
        steps = [
            ("Database Connection", "Verify database connectivity"),
            ("Load Evidence Image", "Load forensic image file"),
            ("Select Partition", "Choose partition to analyze"),
            ("Scan File System", "Scan and ingest file system data"),
            ("Select Artifacts", "Choose artifacts to extract"),
            ("Extract Artifacts", "Perform artifact extraction"),
            ("Parse Artifacts", "Parse extracted artifacts")
        ]
        
        for i, (title, desc) in enumerate(steps, 1):
            step_widget = WorkflowStepWidget(i, title, desc)
            self.workflow_steps.append(step_widget)
            layout.addWidget(step_widget)
        
        layout.addStretch()
        
        # Current status
        status_group = QGroupBox("Current Status")
        status_layout = QVBoxLayout()
        
        self.current_status_label = QLabel("Ready to start investigation")
        self.current_status_label.setStyleSheet("font-weight: bold; color: #495057;")
        status_layout.addWidget(self.current_status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Update library status
        self.update_library_status()
        
        return workflow_widget
    
    def update_library_status(self):
        """Update library status display"""
        if FORENSIC_LIBS_AVAILABLE:
            self.lib_status_label.setText("✓ All forensic libraries available")
            self.lib_status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.lib_status_label.setText("⚠ Some forensic libraries missing")
            self.lib_status_label.setStyleSheet("color: #ffc107; font-weight: bold;")
    
    def create_content_panel(self):
        """Create right panel with content tabs"""
        self.tab_widget = QTabWidget()
        
        # Set tab bar style for better visibility
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: #ffffff;
                border-radius: 4px;
            }
            
            QTabBar::tab {
                background-color: #f8f9fa;
                color: #495057;
                padding: 12px 25px;
                margin-right: 3px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid #dee2e6;
                border-bottom: none;
                font-weight: 600;
                font-size: 14px;
                min-width: 120px;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #1976d2;
                border-bottom: 3px solid #1976d2;
                font-weight: bold;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #e9ecef;
                color: #495057;
            }
        """)
        
        # Main Control Tab
        self.create_main_control_tab()
        
        # Partition Selection Tab
        self.create_partition_tab()
        
        # Artifact Selection Tab
        self.create_artifact_tab()
        
        # Processing Log Tab
        self.create_log_tab()
        
        # Results Tab
        self.create_results_tab()
        
        # Parsing Tab
        self.create_parsing_tab()
        
        return self.tab_widget
    
    def create_main_control_tab(self):
        """Create main control tab"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Case management section
        case_group = QGroupBox("Case Management")
        case_layout = QVBoxLayout()
        
        # Case name input
        case_name_layout = QHBoxLayout()
        case_name_layout.addWidget(QLabel("Case Name:"))
        self.case_name_edit = QLineEdit()
        self.case_name_edit.setPlaceholderText("Enter case name...")
        case_name_layout.addWidget(self.case_name_edit)
        
        # Investigator input
        investigator_layout = QHBoxLayout()
        investigator_layout.addWidget(QLabel("Investigator:"))
        self.investigator_edit = QLineEdit()
        self.investigator_edit.setPlaceholderText("Enter investigator name...")
        investigator_layout.addWidget(self.investigator_edit)
        
        case_layout.addLayout(case_name_layout)
        case_layout.addLayout(investigator_layout)
        
        case_group.setLayout(case_layout)
        layout.addWidget(case_group)
        
        # Database status
        db_group = QGroupBox("Database Connection")
        db_layout = QHBoxLayout()
        
        self.db_status_label = QLabel("Checking...")
        self.db_test_btn = QPushButton("Test Connection")
        self.db_test_btn.clicked.connect(self.check_database_connection)
        
        db_layout.addWidget(QLabel("Status:"))
        db_layout.addWidget(self.db_status_label)
        db_layout.addStretch()
        db_layout.addWidget(self.db_test_btn)
        
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)
        
        # Evidence image loading
        image_group = QGroupBox("Evidence Image")
        image_layout = QVBoxLayout()
        
        # File selection
        file_layout = QHBoxLayout()
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("Select E01 evidence image file...")
        self.image_path_edit.textChanged.connect(self.on_image_path_changed)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_image_file)
        
        file_layout.addWidget(self.image_path_edit)
        file_layout.addWidget(self.browse_btn)
        
        # Auto-processing checkbox
        self.auto_process_checkbox = QCheckBox("Parse and extract everything automatically")
        self.auto_process_checkbox.setToolTip("If checked, the tool will automatically extract and parse all artifacts without user intervention")
        self.auto_process_checkbox.toggled.connect(self.on_auto_process_toggled)
        
        # Load button
        self.load_image_btn = QPushButton("Process Image")
        self.load_image_btn.setEnabled(False)
        self.load_image_btn.clicked.connect(self.load_evidence_image)
        
        # File info label
        self.file_info_label = QLabel("")
        self.file_info_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        
        image_layout.addLayout(file_layout)
        image_layout.addWidget(self.auto_process_checkbox)
        image_layout.addWidget(self.file_info_label)
        image_layout.addWidget(self.load_image_btn)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        # Progress section
        progress_group = QGroupBox("Processing Progress")
        progress_layout = QVBoxLayout()
        
        self.main_progress_bar = QProgressBar()
        self.main_progress_bar.setVisible(False)
        
        self.progress_label = QLabel("Ready")
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.main_progress_bar)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(main_widget, "Main Control")
    
    def create_partition_tab(self):
        """Create partition selection tab"""
        self.partition_widget = PartitionSelectionWidget()
        self.partition_widget.select_btn.clicked.connect(self.select_partition)
        self.partition_widget.auto_process_btn.clicked.connect(self.auto_process_from_partition)
        self.tab_widget.addTab(self.partition_widget, "Select Partition")
    
    def create_artifact_tab(self):
        """Create artifact selection tab"""
        self.artifact_widget = ArtifactSelectionWidget()
        self.artifact_widget.extract_btn.clicked.connect(self.extract_artifacts)
        self.tab_widget.addTab(self.artifact_widget, "Artifact Selection")
    
    def create_log_tab(self):
        """Create processing log tab"""
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.tab_widget.addTab(self.log_text, "Processing Log")
    
    def create_results_tab(self):
        """Create results tab"""
        results_widget = QWidget()
        layout = QVBoxLayout(results_widget)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(['Artifact', 'Status', 'Location', 'Details'])
        
        layout.addWidget(self.results_table)
        
        # self.tab_widget.addTab(results_widget, "Extraction Results")
    
    def create_parsing_tab(self):
        """Create parsing tab"""
        self.parsing_widget = ParsingSelectionWidget()
        self.parsing_widget.parse_btn.clicked.connect(self.parse_artifacts)
        self.tab_widget.addTab(self.parsing_widget, "Artifact Parsing")
    
    def create_status_bar(self):
        """Create professional status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar
        self.status_progress_bar = QProgressBar()
        self.status_progress_bar.setVisible(False)
        self.status_progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.status_progress_bar)
        
        # Database status
        self.db_status_indicator = QLabel("DB: Disconnected")
        self.status_bar.addPermanentWidget(self.db_status_indicator)
        
        # Library status
        self.lib_status_indicator = QLabel("Libs: Checking")
        self.status_bar.addPermanentWidget(self.lib_status_indicator)
        
        # Update library indicator
        if FORENSIC_LIBS_AVAILABLE:
            self.lib_status_indicator.setText("Libs: OK")
            self.lib_status_indicator.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.lib_status_indicator.setText("Libs: Missing")
            self.lib_status_indicator.setStyleSheet("color: #ffc107; font-weight: bold;")
    
    def apply_professional_style(self):
        """Apply professional light theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QMenuBar {
                background-color: #f8f9fa;
                color: #2c3e50;
                border-bottom: 1px solid #dee2e6;
                padding: 2px;
                font-weight: 500;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 3px;
                margin: 2px;
            }
            
            QMenuBar::item:selected {
                background-color: #e9ecef;
                color: #495057;
            }
            
            QMenu {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px;
            }
            
            QMenu::item {
                padding: 6px 20px;
                border-radius: 3px;
            }
            
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QPushButton {
                background-color: #1d4ed8; /* Tailwind's bg-blue-700 */
                color: white;              /* text-white */
                border: none;
                padding: 10px 20px;        /* similar to px-5 py-2.5 */
                border-radius: 8px;        /* rounded-lg */
                font-weight: 500;          /* font-medium */
                font-size: 14px;           /* text-sm */
                min-width: 80px;
            }

            QPushButton:hover {
                background-color: #1e40af; /* Tailwind's hover:bg-blue-800 */
            }

            QPushButton:pressed {
                background-color: #1e3a8a; /* A bit darker for press */
            }

            QPushButton:focus {
                outline: none;
                border: 2px solid #93c5fd; /* focus:ring-blue-300 */
            }

            QPushButton:disabled {
                background-color: #e5e7eb; /* Tailwind's bg-gray-200 */
                color: #9ca3af;            /* Tailwind's text-gray-400 */
            }

            # QPushButton {
            #     background-color: #0468BF;
            #     color: #049DD9;
            #     border: 1px solid #ced4da;
            #     padding: 8px 16px;
            #     border-radius: 4px;
            #     font-weight: 500;
            #     min-width: 80px;
            # }
            
            # QPushButton:hover {
            #     background-color: #049DD9;
            #     border-color: #adb5bd;
            #     color: #212529;
            # }
            
            # QPushButton:pressed {
            #     background-color: #dee2e6;
            #     border-color: #6c757d;
            # }
            
            # QPushButton:disabled {
            #     background-color: #f8f9fa;
            #     color: #6c757d;
            #     border-color: #dee2e6;
            # }
            
            QGroupBox {
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: 600;
                padding-top: 8px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                background-color: #ffffff;
                color: #495057;
            }
            
            QTreeWidget, QTableWidget, QListWidget {
                background-color: #ffffff;
                color: #495057;
                border: 1px solid #dee2e6;
                alternate-background-color: #f8f9fa;
                gridline-color: #e9ecef;
                border-radius: 4px;
            }
            
            QTreeWidget::item, QTableWidget::item, QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #f1f3f4;
            }
            
            QTreeWidget::item:selected, QTableWidget::item:selected, QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #495057;
                padding: 8px 12px;
                border: none;
                border-right: 1px solid #dee2e6;
                border-bottom: 1px solid #dee2e6;
                font-weight: 600;
            }
            
            QLineEdit, QTextEdit {
                background-color: #ffffff;
                color: #495057;
                border: 1px solid #ced4da;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 14px;
            }
            
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                text-align: center;
                background-color: #f8f9fa;
                color: #495057;
                font-weight: 500;
            }
            
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 3px;
            }
            
            QStatusBar {
                background-color: #f8f9fa;
                color: #495057;
                border-top: 1px solid #dee2e6;
                padding: 4px;
            }
            
            QSplitter::handle {
                background-color: #dee2e6;
                width: 2px;
                height: 2px;
            }
        """)
    
    def update_workflow_step(self, step):
        """Update workflow step indicator"""
        # Mark previous steps as completed
        for i in range(step):
            if i < len(self.workflow_steps):
                self.workflow_steps[i].set_completed()
        
        # Mark current step as active
        if step < len(self.workflow_steps):
            self.workflow_steps[step].set_active()
        
        self.workflow_step = step
        
        # Update case manager
        if self.case_manager.current_case:
            self.case_manager.update_case_status(f"workflow_step_{step}", step)
    
    def log_message(self, message):
        """Add message to log with proper Unicode handling"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Replace Unicode characters that cause issues
        safe_message = message.replace('✓', '[SUCCESS]').replace('✗', '[FAILED]')
        log_entry = f"[{timestamp}] {safe_message}"
        
        self.log_text.append(log_entry)
        self.progress_label.setText(safe_message)
        self.status_label.setText(safe_message)
        
        # Use safe logging
        try:
            logging.info(safe_message)
        except UnicodeEncodeError:
            # Fallback for problematic characters
            ascii_message = safe_message.encode('ascii', errors='ignore').decode('ascii')
            logging.info(ascii_message)
        
        QApplication.processEvents()
    
    def check_database_connection(self):
        """Check database connection"""
        self.log_message("Testing database connection...")
        self.db_test_btn.setEnabled(False)
        
        self.db_thread = DatabaseConnectionThread()
        self.db_thread.connection_result.connect(self.on_database_result)
        self.db_thread.start()
    
    def on_database_result(self, success, message):
        """Handle database connection result"""
        self.db_test_btn.setEnabled(True)
        
        if success:
            self.db_connected = True
            self.db_status_label.setText("Connected")
            self.db_status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            self.db_status_indicator.setText("DB: Connected")
            self.db_status_indicator.setStyleSheet("color: #28a745; font-weight: bold;")
            self.update_workflow_step(1)
            self.current_status_label.setText("Database connected - Ready to load evidence")
        else:
            self.db_connected = False
            self.db_status_label.setText("Failed")
            self.db_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            self.db_status_indicator.setText("DB: Failed")
            self.db_status_indicator.setStyleSheet("color: #dc3545; font-weight: bold;")
        
        self.log_message(message)
    
    def check_libraries(self):
        """Check forensic libraries"""
        libs_info = []
        
        try:
            import pytsk3
            libs_info.append("✓ pytsk3: Available")
        except ImportError:
            libs_info.append("✗ pytsk3: Missing")
        
        try:
            import pyewf
            libs_info.append("✓ pyewf: Available")
        except ImportError:
            libs_info.append("✗ pyewf: Missing")
        
        try:
            import psycopg2
            libs_info.append("✓ psycopg2: Available")
        except ImportError:
            libs_info.append("✗ psycopg2: Missing")
        
        # Check parser availability
        libs_info.append("")  # Add separator
        libs_info.append("Parser Scripts:")
        
        if parse_registry_artifacts is not None:
            libs_info.append("✓ Registry Parser: Available")
        else:
            libs_info.append("✗ Registry Parser: Missing")
        
        if parse_browser_artifacts is not None:
            libs_info.append("✓ Browser Parser: Available")
        else:
            libs_info.append("✗ Browser Parser: Missing")
        
        if parse_system_artifacts is not None:
            libs_info.append("✓ System Artifacts Parser: Available")
        else:
            libs_info.append("✗ System Artifacts Parser: Missing")
        
        QMessageBox.information(
            self,
            "Library Status",
            "Forensic Libraries and Parsers Status:\n\n" + "\n".join(libs_info)
        )
    
    def on_auto_process_toggled(self, checked):
        """Handle auto-processing checkbox toggle"""
        self.auto_process = checked
        if checked:
            self.log_message("Auto-processing enabled: Will extract and parse all artifacts automatically")
        else:
            self.log_message("Auto-processing disabled: Manual workflow enabled")
    
    def on_image_path_changed(self):
        """Handle image path change"""
        path = self.image_path_edit.text()
        self.load_image_btn.setEnabled(bool(path and os.path.exists(path)))
        
        if path and os.path.exists(path):
            try:
                file_size = os.path.getsize(path)
                size_mb = file_size / (1024 * 1024)
                self.file_info_label.setText(f"File size: {size_mb:.2f} MB")
            except:
                self.file_info_label.setText("File information unavailable")
        else:
            self.file_info_label.setText("")
    
    def browse_image_file(self):
        """Browse for evidence image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select E01 Evidence Image",
            "",
            "E01 Files (*.E01);;All Files (*)"
        )
        
        if file_path:
            self.image_path_edit.setText(file_path)
            self.current_image_path = file_path
            logging.info(f"Selected image file: {file_path}")
    
    def load_evidence_image(self):
        """Load evidence image"""
        if not FORENSIC_LIBS_AVAILABLE:
            QMessageBox.warning(
                self, 
                "Warning", 
                "Forensic libraries (pytsk3, pyewf) are not available.\n\n"
                "Please install them using:\n"
                "pip install pytsk3 pyewf"
            )
            return
            
        if not self.db_connected:
            QMessageBox.warning(self, "Warning", "Database connection required before loading image")
            return
        
        image_path = self.image_path_edit.text()
        if not image_path or not os.path.exists(image_path):
            QMessageBox.warning(self, "Warning", "Please select a valid E01 image file")
            return
        
        # Create new case if not exists
        if not self.case_manager.current_case:
            case_name = self.case_name_edit.text() or f"Case_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            investigator = self.investigator_edit.text() or "Unknown"
            self.case_manager.create_case(case_name, image_path, investigator)
            self.update_case_info()
        
        self.current_image_path = image_path
        self.log_message(f"Processing image: {os.path.basename(image_path)}")
        
        # Initialize database connection
        try:
            self.db_conn = open_db()
            create_table(self.db_conn)
            logging.info("Database initialized")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to initialize database: {str(e)}")
            return
        
        # Show progress
        self.main_progress_bar.setVisible(True)
        self.main_progress_bar.setRange(0, 0)
        self.status_progress_bar.setVisible(True)
        self.status_progress_bar.setRange(0, 0)
        
        # Disable controls
        self.load_image_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        
        # Start loading thread
        self.image_thread = ImageLoadingThread(image_path)
        self.image_thread.progress_update.connect(self.log_message)
        self.image_thread.partitions_found.connect(self.on_partitions_found)
        self.image_thread.loading_complete.connect(self.on_image_loaded)
        self.image_thread.start()
    
    def update_case_info(self):
        """Update case information display"""
        if self.case_manager.current_case:
            case_info = f"Case: {self.case_manager.current_case['case_name']}\n"
            case_info += f"Investigator: {self.case_manager.current_case['investigator']}\n"
            case_info += f"Created: {self.case_manager.current_case['created_date'][:10]}"
            self.case_info_label.setText(case_info)
        else:
            self.case_info_label.setText("No case loaded")
    
    def on_partitions_found(self, partitions):
        """Handle partitions found - FIXED: No auto-selection"""
        self.partitions = partitions
        self.img_info = self.image_thread.img_info
        self.partition_widget.update_partitions(partitions)
        
        # Save partitions to case (without non-serializable objects)
        self.case_manager.set_partitions(partitions)
        
        # REMOVED AUTO-PROCESSING - Always go to partition tab
        self.tab_widget.setCurrentIndex(1)  # Switch to partition tab
        
        # Update info display
        partition_info = "Available Partitions:\n\n"
        for part in partitions:
            partition_info += f"- Partition {part['addr']}\n"
            partition_info += f"  Type: {part['description']}\n"
            partition_info += f"  Size: {part['size_mb']} MB\n\n"
        
        self.log_message(partition_info)
        self.log_message("Please select a partition to continue")
    
    def on_image_loaded(self, success, message):
        """Handle image loading completion"""
        # Hide progress
        self.main_progress_bar.setVisible(False)
        self.status_progress_bar.setVisible(False)
        
        # Re-enable controls
        self.load_image_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        
        if success:
            self.update_workflow_step(2)
            self.current_status_label.setText("Image loaded - Select partition to analyze")
            self.log_message("Evidence image loaded successfully - Please select a partition")
        else:
            QMessageBox.critical(self, "Error", f"Failed to load image:\n\n{message}")
        
        self.log_message(message)
    
    def auto_process_from_partition(self):
        """Auto-process everything from partition selection with UI improvements"""
        selected_partition = self.partition_widget.get_selected_partition()
        if not selected_partition:
            QMessageBox.warning(self, "Warning", "Please select a partition first")
            return
        
        self.current_partition = selected_partition
        self.case_manager.set_selected_partition(selected_partition)
        self.log_message(f"Starting auto-processing for partition: {selected_partition['description']}")
        
        # Switch to Processing Log tab immediately
        self.tab_widget.setCurrentIndex(3)  # Processing Log tab
        
        # Disable artifact and parsing selection tabs
        self.artifact_widget.setEnabled(False)
        self.parsing_widget.setEnabled(False)
        
        # Start auto file system scan
        self.auto_scan_file_system()
    
    def auto_scan_file_system(self):
        """Automatically scan file system for auto-processing"""
        self.log_message("Auto-processing: Starting file system scan...")
        self.update_workflow_step(3)
        
        # Show progress
        self.main_progress_bar.setVisible(True)
        self.main_progress_bar.setRange(0, 0)
        self.status_progress_bar.setVisible(True)
        self.status_progress_bar.setRange(0, 0)
        
        # Start scanning thread
        self.scan_thread = FileSystemScanThread(self.img_info, self.current_partition, self.db_conn)
        self.scan_thread.progress_update.connect(self.log_message)
        self.scan_thread.scan_complete.connect(self.on_auto_scan_complete)
        self.scan_thread.start()
    
    def on_auto_scan_complete(self, success, message, result_info):
        """Handle auto scan completion"""
        # Hide progress
        self.main_progress_bar.setVisible(False)
        self.status_progress_bar.setVisible(False)
        
        if success:
            self.fs_info = result_info['fs_info']
            self.update_workflow_step(4)
            self.log_message("Auto-processing: File system scan completed, starting automatic processing...")
            
            # Start auto-processing
            self.auto_processing_thread = AutoProcessingThread(
                self.img_info, self.current_partition, self.db_conn, self.fs_info
            )
            self.auto_processing_thread.progress_update.connect(self.log_message)
            self.auto_processing_thread.processing_complete.connect(self.on_auto_processing_complete)
            self.auto_processing_thread.start()
        else:
            QMessageBox.critical(self, "Error", f"Auto scan failed: {message}")
        
        self.log_message(message)
    
    def on_auto_processing_complete(self, success, message):
        """Handle auto-processing completion with UI cleanup"""
        # Re-enable tabs
        self.artifact_widget.setEnabled(True)
        self.parsing_widget.setEnabled(True)
        
        if success:
            self.update_workflow_step(7)
            self.current_status_label.setText("Auto-processing completed - Investigation finished")
            self.tab_widget.setCurrentIndex(4)  # Switch to results tab
            QMessageBox.information(self, "Auto-Processing Complete", message)
        else:
            QMessageBox.critical(self, "Auto-Processing Failed", message)
        
        self.log_message(message)
    
    def select_partition(self):
        """Select partition for analysis"""
        selected_partition = self.partition_widget.get_selected_partition()
        if not selected_partition:
            QMessageBox.warning(self, "Warning", "Please select a partition")
            return
        
        self.current_partition = selected_partition
        self.case_manager.set_selected_partition(selected_partition)
        self.log_message(f"Selected partition {selected_partition['addr']}: {selected_partition['description']}")
        
        # Start file system scanning
        reply = QMessageBox.question(
            self, 
            "Confirm Scan", 
            f"Scan partition '{selected_partition['description']}'?\n\nThis may take several minutes.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.scan_file_system()
    
    def scan_file_system(self):
        """Scan file system"""
        self.log_message("Starting file system scan...")
        self.update_workflow_step(3)
        
        # Show progress
        self.main_progress_bar.setVisible(True)
        self.main_progress_bar.setRange(0, 0)
        self.status_progress_bar.setVisible(True)
        self.status_progress_bar.setRange(0, 0)
        
        # Start scanning thread
        self.scan_thread = FileSystemScanThread(self.img_info, self.current_partition, self.db_conn)
        self.scan_thread.progress_update.connect(self.log_message)
        self.scan_thread.scan_complete.connect(self.on_scan_complete)
        self.scan_thread.start()
    
    def on_scan_complete(self, success, message, result_info):
        """Handle scan completion"""
        # Hide progress
        self.main_progress_bar.setVisible(False)
        self.status_progress_bar.setVisible(False)
        
        if success:
            self.fs_info = result_info['fs_info']
            self.update_workflow_step(4)
            self.current_status_label.setText("File system scanned - Select artifacts to extract")
            self.tab_widget.setCurrentIndex(2)  # Switch to artifact tab
            QMessageBox.information(self, "Success", "File system scan completed successfully")
        else:
            QMessageBox.critical(self, "Error", f"Scan failed: {message}")
        
        self.log_message(message)
    
    def extract_artifacts(self):
        """Extract selected artifacts"""
        selected_artifacts = self.artifact_widget.get_selected_artifacts()
        
        if not selected_artifacts:
            QMessageBox.warning(self, "Warning", "Please select artifacts to extract")
            return
        
        if not self.fs_info or not self.db_conn:
            QMessageBox.warning(self, "Warning", "File system must be scanned first")
            return
        
        self.log_message(f"Starting extraction of: {', '.join(selected_artifacts)}")
        self.update_workflow_step(5)
        
        # Show progress
        self.main_progress_bar.setVisible(True)
        self.main_progress_bar.setRange(0, 0)
        self.status_progress_bar.setVisible(True)
        self.status_progress_bar.setRange(0, 0)
        
        # Disable extract button
        self.artifact_widget.extract_btn.setEnabled(False)
        
        # Start extraction thread
        self.extraction_thread = ArtifactExtractionThread(self.fs_info, self.db_conn, selected_artifacts)
        self.extraction_thread.progress_update.connect(self.log_message)
        self.extraction_thread.extraction_complete.connect(self.on_extraction_complete)
        self.extraction_thread.start()
    
    def on_extraction_complete(self, success, message, results):
        """Handle extraction completion"""
        # Hide progress
        self.main_progress_bar.setVisible(False)
        self.status_progress_bar.setVisible(False)
        
        # Re-enable extract button
        self.artifact_widget.extract_btn.setEnabled(True)
        
        if success:
            self.update_workflow_step(6)
            self.current_status_label.setText("Artifacts extracted - Ready for parsing")
            self.update_results_table(results)
            self.tab_widget.setCurrentIndex(4)  # Switch to results tab
            
            # Save extracted artifacts to case
            for name, success_status in results:
                self.case_manager.add_extracted_artifact({'name': name, 'success': success_status})
            
            # Show results
            result_text = "Extraction Results:\n\n"
            for name, success_status in results:
                status = "Success" if success_status else "Failed"
                result_text += f"- {name}: {status}\n"
            
            self.log_message(result_text)
            QMessageBox.information(self, "Success", "Artifact extraction completed")
        else:
            QMessageBox.critical(self, "Error", f"Extraction failed: {message}")
        
        self.log_message(message)
    
    def update_results_table(self, results):
        """Update results table with extraction results"""
        self.results_table.setRowCount(len(results))
        
        for i, (artifact, status) in enumerate(results):
            self.results_table.setItem(i, 0, QTableWidgetItem(artifact))
            
            if status:
                status_item = QTableWidgetItem("✓ Success")
                status_item.setBackground(QColor("#d4edda"))
            else:
                status_item = QTableWidgetItem("✗ Failed")
                status_item.setBackground(QColor("#f8d7da"))
            
            self.results_table.setItem(i, 1, status_item)
            self.results_table.setItem(i, 2, QTableWidgetItem(f"output/{artifact.lower().replace(' ', '_')}"))
            self.results_table.setItem(i, 3, QTableWidgetItem("Extracted successfully" if status else "Extraction failed"))
        
        # Resize columns
        self.results_table.resizeColumnsToContents()
    
    def parse_artifacts(self):
        """Parse selected artifacts using the integrated parser scripts"""
        selected_parsers = self.parsing_widget.get_selected_parsers()
        
        if not selected_parsers:
            QMessageBox.warning(self, "Warning", "Please select parsers to run")
            return
        
        self.log_message(f"Starting parsing with: {', '.join(selected_parsers)}")
        self.update_workflow_step(7)
        
        # Show progress
        self.main_progress_bar.setVisible(True)
        self.main_progress_bar.setRange(0, 0)
        self.status_progress_bar.setVisible(True)
        self.status_progress_bar.setRange(0, 0)
        
        # Disable parse button
        self.parsing_widget.parse_btn.setEnabled(False)
        
        # Start parsing thread with integrated parsers
        self.parsing_thread = ParsingThread(selected_parsers)
        self.parsing_thread.progress_update.connect(self.log_message)
        self.parsing_thread.parsing_complete.connect(self.on_parsing_complete)
        self.parsing_thread.start()
    
    def on_parsing_complete(self, success, message, results):
        """Handle parsing completion"""
        # Hide progress
        self.main_progress_bar.setVisible(False)
        self.status_progress_bar.setVisible(False)
        
        # Re-enable parse button
        self.parsing_widget.parse_btn.setEnabled(True)
        
        if success:
            self.update_workflow_step(7)
            self.current_status_label.setText("Parsing completed - Investigation finished")
            
            # Save parsed artifacts to case
            for parser, success_status, output in results:
                self.case_manager.add_parsed_artifact({'parser': parser, 'success': success_status, 'output': output})
            
            # Update results in a table format
            self.update_parsing_results_table(results)
            
            # Show parsing results summary
            successful_parsers = [parser for parser, success_status, _ in results if success_status]
            failed_parsers = [parser for parser, success_status, _ in results if not success_status]
            
            result_text = f"Parsing Results Summary:\n\n"
            result_text += f"[SUCCESS] Successful: {len(successful_parsers)} parsers\n"
            result_text += f"[FAILED] Failed: {len(failed_parsers)} parsers\n\n"
            
            if successful_parsers:
                result_text += f"Successful parsers: {', '.join(successful_parsers)}\n"
            if failed_parsers:
                result_text += f"Failed parsers: {', '.join(failed_parsers)}\n"
            
            self.log_message(result_text)
            QMessageBox.information(self, "Success", "Artifact parsing completed successfully!")
        else:
            QMessageBox.critical(self, "Error", f"Parsing failed: {message}")
        
        self.log_message(message)
    
    def update_parsing_results_table(self, results):
        """Update results table with parsing results"""
        # Add parsing results to the existing results table
        current_rows = self.results_table.rowCount()
        
        for parser, success_status, output in results:
            row = current_rows
            self.results_table.insertRow(row)
            
            # Parser name
            self.results_table.setItem(row, 0, QTableWidgetItem(f"{parser.title()} Parser"))
            
            # Status
            if success_status:
                status_item = QTableWidgetItem("✓ Parsed")
                status_item.setBackground(QColor("#d1ecf1"))
            else:
                status_item = QTableWidgetItem("✗ Parse Failed")
                status_item.setBackground(QColor("#f8d7da"))
            
            self.results_table.setItem(row, 1, status_item)
            
            # Location
            self.results_table.setItem(row, 2, QTableWidgetItem(f"parsed_artifacts/{parser}"))
            
            # Details
            details = output if len(output) < 100 else output[:100] + "..."
            self.results_table.setItem(row, 3, QTableWidgetItem(details))
            
            current_rows += 1
        
        # Resize columns
        self.results_table.resizeColumnsToContents()
    
    def save_case(self):
        """Save current case"""
        if self.case_manager.current_case:
            self.case_manager.save_case()
            QMessageBox.information(self, "Case Saved", "Case has been saved successfully")
            self.log_message("Case saved successfully")
        else:
            QMessageBox.warning(self, "No Case", "No active case to save")
    
    def new_investigation(self):
        """Start new investigation"""
        reply = QMessageBox.question(
            self, 
            "New Investigation", 
            "Start a new investigation? This will reset all current progress.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Close any open resources
            if self.db_conn:
                try:
                    self.db_conn.close()
                except:
                    pass
            
            # Reset case manager
            self.case_manager.current_case = None
            
            # Reset all workflow steps
            for step in self.workflow_steps:
                step.is_active = False
                step.is_completed = False
                step.step_label.setText(str(step.step_number))
                step.step_label.setStyleSheet("""
                    QLabel {
                        background-color: #e9ecef;
                        color: #6c757d;
                        border-radius: 20px;
                        font-weight: bold;
                        font-size: 16px;
                    }
                """)
                step.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #495057;")
            
            # Reset variables
            self.current_image_path = None
            self.current_partition = None
            self.workflow_step = 0
            self.db_conn = None
            self.img_info = None
            self.fs_info = None
            self.partitions = []
            self.auto_process = False
            
            # Clear UI
            self.case_name_edit.clear()
            self.investigator_edit.clear()
            self.image_path_edit.clear()
            self.file_info_label.clear()
            self.partition_widget.partition_list.clear()
            self.artifact_widget.clear_all()
            self.parsing_widget.clear_all()
            self.results_table.setRowCount(0)
            self.log_text.clear()
            self.auto_process_checkbox.setChecked(False)
            
            # Reset status
            self.current_status_label.setText("Ready to start new investigation")
            self.update_case_info()
            self.log_message("New investigation started")
            
            # Check database connection
            self.check_database_connection()
    
#     def show_about(self):
#         """Show about dialog"""
#         about_text = """
# Professional Forensic Artifact Extractor v4.0 Complete

# A comprehensive digital forensics tool with guided workflow, case management, and integrated parsing capabilities.

# Features:
# • Step-by-step investigation workflow
# • Professional user interface with enhanced checkboxes
# • Case management with automatic save/resume
# • Auto-processing mode for hands-free operation
# • Parse and Extract Everything button for quick processing
# • Enhanced E01 file support
# • Real-time progress tracking
# • Comprehensive artifact extraction
# • Integrated artifact parsing with multiple parsers:
#   - Registry Parser (RegRipper integration)
#   - Browser Parser (Hindsight integration)
#   - System Artifacts Parser (Eric Zimmerman tools)
# • Database integration
# • Multi-threaded processing
# • Robust error handling and recovery

# Auto-Processing Mode:
# • Extract and parse all artifacts automatically
# • Hands-free operation after partition selection
# • Intelligent workflow management
# • Complete automation with user control

# Integrated Parsers:
# • Registry Parser: Uses RegRipper for Windows Registry analysis
# • Browser Parser: Uses Hindsight for Chrome/Edge artifact analysis
# • MFT Parser: Uses MFTECmd for Master File Table analysis
# • SRUM Parser: Uses SrumECmd for SRUM database analysis
# • Prefetch Parser: Uses PECmd for Prefetch file analysis
# • Amcache Parser: Uses AmcacheParser for Amcache.hve analysis

# System Requirements:
# • Python 3.6+
# • PyQt5
# • pytsk3 (for file system analysis)
# • pyewf (for E01 support)
# • psycopg2 (for PostgreSQL support)

# Installation:
# pip install PyQt5 pytsk3 pyewf psycopg2

# Built with PyQt5 for professional forensic investigations.
#         """
        
#         QMessageBox.about(self, "About", about_text)
    def show_about(self):
        """Show enhanced About dialog with scroll and styling"""

        about_text = """
        <h2 style='color:#2E86C1;'>Forensic Artifact Extractor & Parser v2.1.0 Complete</h2>
        <p><i>A comprehensive digital forensics tool with guided workflow, case management, and integrated parsing capabilities.</i></p>
        
        <h3>🚀 Features:</h3>
        <ul>
            <li>Step-by-step investigation workflow</li>
            <li>Professional user interface with enhanced checkboxes</li>
            <li>Case management with automatic save/resume</li>
            <li>Auto-processing mode for hands-free operation</li>
            <li>“Parse and Extract Everything” button for quick processing</li>
            <li>Enhanced E01 file support</li>
            <li>Real-time progress tracking</li>
            <li>Comprehensive artifact extraction</li>
            <li>Integrated parsing with multiple tools (RegRipper, Hindsight, etc.)</li>
            <li>Database integration and multi-threading</li>
            <li>Robust error handling and recovery</li>
        </ul>

        <h3>⚙️ Auto-Processing Mode:</h3>
        <ul>
            <li>Extract and parse all artifacts automatically</li>
            <li>Hands-free operation after partition selection</li>
            <li>Intelligent workflow management</li>
            <li>Complete automation with user control</li>
        </ul>

        <h3>🧩 Integrated Parsers:</h3>
        <ul>
            <li><b>Registry Parser:</b> RegRipper</li>
            <li><b>Browser Parser:</b> Hindsight (Chrome/Edge)</li>
            <li><b>MFT Parser:</b> MFTECmd</li>
            <li><b>SRUM Parser:</b> SrumECmd</li>
            <li><b>Prefetch Parser:</b> PECmd</li>
            <li><b>Amcache Parser:</b> AmcacheParser</li>
        </ul>

        <h3>🖥️ Requirements:</h3>
        <ul>
            <li>Python 3.6+</li>
            <li>PyQt5</li>
            <li>pytsk3</li>
            <li>pyewf</li>
            <li>psycopg2</li>
        </ul>
        """

        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setMinimumSize(600, 500)

        layout = QVBoxLayout(dialog)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        label = QLabel()
        label.setTextFormat(Qt.RichText)
        label.setText(about_text)
        label.setWordWrap(True)

        content_layout.addWidget(label)
        scroll.setWidget(content)

        layout.addWidget(scroll)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)

        dialog.exec_()
def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Forensic Artifact Extractor & Parser")
    app.setApplicationVersion("v2.1.0")
    # app.setOrganizationName("Digital Forensics Solutions")
    
    try:
        window = ForensicMainWindow()
        window.show()
        
        logging.info("Forensic Artifact Extractor & Parser v2.1.0 started successfully")
        sys.exit(app.exec_())
        
    except Exception as e:
        error_msg = f"Failed to start application: {str(e)}"
        print(error_msg)
        logging.error(error_msg)
        
        try:
            QMessageBox.critical(None, "Startup Error", error_msg)
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    # Set up exception handling
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = f"Uncaught exception: {exc_type.__name__}: {exc_value}"
        logging.error(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
        
        # Show error dialog if GUI is available
        try:
            app = QApplication.instance()
            if app:
                QMessageBox.critical(None, "Unexpected Error", error_msg)
        except:
            pass
    
    sys.excepthook = handle_exception
    
    # Run the application
    main()
