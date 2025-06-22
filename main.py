# import os
# import sys
# import pytsk3
# import pyewf
# import psycopg2
# import psycopg2.extras
# import logging
# from datetime import datetime
# from PyQt5.QtWidgets import (
#     QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
#     QLineEdit, QPushButton, QMessageBox, QGroupBox, QFormLayout,
#     QCheckBox, QProgressBar, QTextEdit
# )
# from PyQt5.QtCore import Qt, QThread, pyqtSignal
# from PyQt5.QtGui import QFont, QIcon

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("forensic_extractor.log"),
#         logging.StreamHandler()
#     ]
# )

# # Global database configuration with defaults
# DB_CONFIG = {
#     'host': 'localhost',
#     'database': 'forensic_FAEP_db',  # Auto-created database name
#     'user': 'postgres',
#     'password': '',
#     'port': 5432  # Default PostgreSQL port
# }

# class DatabaseTestThread(QThread):
#     """Thread for testing database connection and auto-creating database"""
#     connection_result = pyqtSignal(bool, str)
    
#     def __init__(self, config):
#         super().__init__()
#         self.config = config
        
#     def run(self):
#         try:
#             logging.info("Testing database connection and auto-creating database...")
            
#             # First, connect to template1 database to create our database
#             temp_config = self.config.copy()
#             temp_config['database'] = 'template1'  # Connect to template1 first
            
#             conn = psycopg2.connect(
#                 host=temp_config['host'],
#                 database=temp_config['database'],
#                 user=temp_config['user'],
#                 password=temp_config['password'],
#                 port=temp_config['port']
#             )
#             conn.autocommit = True  # Required for CREATE DATABASE
            
#             with conn.cursor() as cursor:
#                 # Check if our database exists
#                 cursor.execute(
#                     "SELECT 1 FROM pg_database WHERE datname = %s",
#                     (self.config['database'],)
#                 )
#                 exists = cursor.fetchone()
                
#                 if not exists:
#                     # Create the database
#                     logging.info(f"Creating database: {self.config['database']}")
#                     cursor.execute(f'CREATE DATABASE "{self.config["database"]}"')
#                     logging.info("Database created successfully")
#                 else:
#                     logging.info("Database already exists")
            
#             conn.close()
            
#             # Now connect to our actual database
#             logging.info(f"Connecting to database: {self.config['database']}")
#             conn = psycopg2.connect(
#                 host=self.config['host'],
#                 database=self.config['database'],
#                 user=self.config['user'],
#                 password=self.config['password'],
#                 port=self.config['port']
#             )
            
#             if conn:
#                 logging.info("Connection successful")
                
#                 with conn.cursor() as cursor:
#                     cursor.execute("SELECT version()")
#                     version = cursor.fetchone()[0]
#                     logging.info(f"PostgreSQL version: {version}")
                    
#                     # Create the file_tree table
#                     cursor.execute("""
#                         CREATE TABLE IF NOT EXISTS file_tree (
#                             id BIGSERIAL PRIMARY KEY,
#                             path TEXT UNIQUE NOT NULL,
#                             name TEXT,
#                             type TEXT,
#                             size BIGINT,
#                             created TIMESTAMP,
#                             modified TIMESTAMP,
#                             accessed TIMESTAMP,
#                             parent_path TEXT,
#                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#                         );
#                     """)
                    
#                     # Create indexes for better performance
#                     cursor.execute("""
#                         CREATE INDEX IF NOT EXISTS idx_file_tree_path ON file_tree(path);
#                         CREATE INDEX IF NOT EXISTS idx_file_tree_name ON file_tree(name);
#                         CREATE INDEX IF NOT EXISTS idx_file_tree_type ON file_tree(type);
#                         CREATE INDEX IF NOT EXISTS idx_file_tree_parent_path ON file_tree(parent_path);
#                     """)
                    
#                     # Create additional tables for forensic data
#                     cursor.execute("""
#                         CREATE TABLE IF NOT EXISTS extraction_sessions (
#                             id BIGSERIAL PRIMARY KEY,
#                             session_name TEXT NOT NULL,
#                             image_path TEXT,
#                             start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                             end_time TIMESTAMP,
#                             status TEXT DEFAULT 'running',
#                             total_files INTEGER DEFAULT 0,
#                             extracted_files INTEGER DEFAULT 0
#                         );
#                     """)
                    
#                     cursor.execute("""
#                         CREATE TABLE IF NOT EXISTS extraction_logs (
#                             id BIGSERIAL PRIMARY KEY,
#                             session_id BIGINT REFERENCES extraction_sessions(id),
#                             timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                             level TEXT,
#                             message TEXT
#                         );
#                     """)
                    
#                     conn.commit()
#                     logging.info("Database tables created successfully")
                    
#                     # Test insertion
#                     cursor.execute("""
#                         INSERT INTO file_tree
#                         (path, name, type, size, created, modified, accessed, parent_path)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                         ON CONFLICT (path) DO NOTHING
#                     """, ("/test_connection", "test_file", "File", 0, None, None, None, "/"))
#                     conn.commit()
                    
#                     # Verify insertion
#                     cursor.execute("SELECT COUNT(*) FROM file_tree WHERE path = '/test_connection'")
#                     count = cursor.fetchone()[0]
#                     logging.info(f"Test record verification: {count > 0}")
                    
#                     # Clean up test record
#                     cursor.execute("DELETE FROM file_tree WHERE path = '/test_connection'")
#                     conn.commit()
                    
#                 conn.close()
#                 logging.info("Database setup complete")
#                 self.connection_result.emit(True, f"✓ Database setup successful!\n✓ Database '{self.config['database']}' ready\n✓ Tables created\n✓ Connection verified")
#             else:
#                 self.connection_result.emit(False, "Failed to connect to database")
                
#         except psycopg2.OperationalError as e:
#             error_msg = str(e)
#             if "authentication failed" in error_msg.lower():
#                 self.connection_result.emit(False, f"Authentication Error: Invalid username or password.\nPlease check your PostgreSQL credentials.")
#             elif "connection refused" in error_msg.lower():
#                 self.connection_result.emit(False, f"Connection Error: PostgreSQL server is not running or not accessible.\nPlease ensure PostgreSQL is installed and running on port {self.config['port']}.")
#             elif "does not exist" in error_msg.lower():
#                 self.connection_result.emit(False, f"Database Error: PostgreSQL server found but connection failed.\nError: {error_msg}")
#             else:
#                 self.connection_result.emit(False, f"Connection Error: {error_msg}")
#         except Exception as e:
#             logging.error(f"Database setup failed: {str(e)}")
#             self.connection_result.emit(False, f"Setup Error: {str(e)}")

# class DatabaseSetupDialog(QDialog):
#     """Simplified database setup dialog"""
    
#     def __init__(self):
#         super().__init__()
#         self.connection_successful = False
#         self.init_ui()
#         self.apply_style()
        
#     def init_ui(self):
#         self.setWindowTitle("Forensic Tool - Database Setup")
#         self.setFixedSize(450, 700)
#         self.setModal(True)
        
#         layout = QVBoxLayout()
        
#         # Title
#         title_label = QLabel("PostgreSQL Database Setup")
#         title_label.setAlignment(Qt.AlignCenter)
#         title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px;")
#         layout.addWidget(title_label)
        
#         # Description
#         desc_label = QLabel("Enter your PostgreSQL credentials.\nThe database and tables will be created automatically.")
#         desc_label.setAlignment(Qt.AlignCenter)
#         desc_label.setStyleSheet("color: #6c757d; margin-bottom: 20px;")
#         layout.addWidget(desc_label)
        
#         # Auto-configuration info
#         info_group = QGroupBox("Auto-Configuration")
#         info_layout = QVBoxLayout()
        
#         info_text = QLabel("""
# • Host: localhost (default)
# • Port: 5432 (PostgreSQL default)
# • Database: forensic_tool_db (auto-created)
# • Tables: Created automatically with indexes
#         """)
#         info_text.setStyleSheet("color: #495057; font-size: 12px; padding: 10px;")
#         info_layout.addWidget(info_text)
#         info_group.setLayout(info_layout)
#         layout.addWidget(info_group)
        
#         # Credentials group
#         creds_group = QGroupBox("PostgreSQL Credentials")
#         creds_layout = QFormLayout()
        
#         # Username
#         self.user_edit = QLineEdit(DB_CONFIG['user'])
#         self.user_edit.setPlaceholderText("PostgreSQL username (usually 'postgres')")
#         creds_layout.addRow("Username:", self.user_edit)
        
#         # Password
#         self.password_edit = QLineEdit(DB_CONFIG['password'])
#         self.password_edit.setEchoMode(QLineEdit.Password)
#         self.password_edit.setPlaceholderText("PostgreSQL password")
#         creds_layout.addRow("Password:", self.password_edit)
        
#         # Show password checkbox
#         self.show_password_cb = QCheckBox("Show password")
#         self.show_password_cb.toggled.connect(self.toggle_password_visibility)
#         creds_layout.addRow("", self.show_password_cb)
        
#         creds_group.setLayout(creds_layout)
#         layout.addWidget(creds_group)
        
#         # Test connection section
#         test_group = QGroupBox("Setup & Test")
#         test_layout = QVBoxLayout()
        
#         # Test button
#         self.test_btn = QPushButton("Setup Database & Test Connection")
#         self.test_btn.clicked.connect(self.test_connection)
#         test_layout.addWidget(self.test_btn)
        
#         # Progress bar
#         self.progress_bar = QProgressBar()
#         self.progress_bar.setVisible(False)
#         test_layout.addWidget(self.progress_bar)
        
#         # Result text
#         self.result_text = QTextEdit()
#         self.result_text.setMaximumHeight(100)
#         self.result_text.setReadOnly(True)
#         self.result_text.setPlaceholderText("Setup results will appear here...")
#         test_layout.addWidget(self.result_text)
        
#         test_group.setLayout(test_layout)
#         layout.addWidget(test_group)
        
#         # Buttons
#         button_layout = QHBoxLayout()
        
#         self.proceed_btn = QPushButton("Proceed to Application")
#         self.proceed_btn.setEnabled(False)
#         self.proceed_btn.clicked.connect(self.accept)
        
#         self.cancel_btn = QPushButton("Cancel")
#         self.cancel_btn.clicked.connect(self.reject)
        
#         button_layout.addWidget(self.cancel_btn)
#         button_layout.addStretch()
#         button_layout.addWidget(self.proceed_btn)
        
#         layout.addLayout(button_layout)
        
#         # Status
#         self.status_label = QLabel("Please enter your PostgreSQL credentials and setup the database")
#         self.status_label.setStyleSheet("color: #6c757d; font-style: italic; margin: 10px;")
#         layout.addWidget(self.status_label)
        
#         self.setLayout(layout)
        
#         # Auto-focus on username if empty, otherwise password
#         if not self.user_edit.text():
#             self.user_edit.setFocus()
#         else:
#             self.password_edit.setFocus()
    
#     def apply_style(self):
#         """Apply professional styling"""
#         self.setStyleSheet("""
#             QDialog {
#                 background-color: #ffffff;
#                 color: #2c3e50;
#                 font-family: 'Segoe UI', Arial, sans-serif;
#             }
            
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
            
#             QLineEdit {
#                 background-color: #ffffff;
#                 color: #495057;
#                 border: 1px solid #ced4da;
#                 padding: 8px 12px;
#                 border-radius: 4px;
#                 font-size: 14px;
#             }
            
#             QLineEdit:focus {
#                 border-color: #1976d2;
#                 outline: none;
#             }
            
#             QPushButton {
#                 background-color: #1d4ed8;
#                 color: white;
#                 border: none;
#                 padding: 10px 20px;
#                 border-radius: 6px;
#                 font-weight: 500;
#                 font-size: 14px;
#                 min-width: 120px;
#             }
            
#             QPushButton:hover {
#                 background-color: #1e40af;
#             }
            
#             QPushButton:pressed {
#                 background-color: #1e3a8a;
#             }
            
#             QPushButton:disabled {
#                 background-color: #e5e7eb;
#                 color: #9ca3af;
#             }
            
#             QCheckBox {
#                 font-size: 13px;
#                 color: #495057;
#                 spacing: 8px;
#             }
            
#             QTextEdit {
#                 background-color: #f8f9fa;
#                 color: #495057;
#                 border: 1px solid #dee2e6;
#                 border-radius: 4px;
#                 padding: 8px;
#                 font-family: 'Consolas', monospace;
#                 font-size: 12px;
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
#         """)
    
#     def toggle_password_visibility(self, checked):
#         """Toggle password visibility"""
#         if checked:
#             self.password_edit.setEchoMode(QLineEdit.Normal)
#         else:
#             self.password_edit.setEchoMode(QLineEdit.Password)
    
#     def test_connection(self):
#         """Test database connection and setup"""
#         username = self.user_edit.text().strip()
#         password = self.password_edit.text()
        
#         if not username:
#             QMessageBox.warning(self, "Missing Information", "Please enter a PostgreSQL username")
#             self.user_edit.setFocus()
#             return
            
#         self.test_btn.setEnabled(False)
#         self.progress_bar.setVisible(True)
#         self.progress_bar.setRange(0, 0)
#         self.result_text.clear()
#         self.status_label.setText("Setting up database and testing connection...")
        
#         # Update configuration
#         config = DB_CONFIG.copy()
#         config['user'] = username
#         config['password'] = password
        
#         # Start test thread
#         self.test_thread = DatabaseTestThread(config)
#         self.test_thread.connection_result.connect(self.on_connection_result)
#         self.test_thread.start()
    
#     def on_connection_result(self, success, message):
#         """Handle connection test result"""
#         self.test_btn.setEnabled(True)
#         self.progress_bar.setVisible(False)
        
#         if success:
#             self.connection_successful = True
#             self.result_text.setStyleSheet("color: #28a745; background-color: #d4edda; border-color: #c3e6cb;")
#             self.result_text.setText(message)
#             self.proceed_btn.setEnabled(True)
#             self.status_label.setText("✓ Database ready! You can now proceed to the application.")
#             self.status_label.setStyleSheet("color: #28a745; font-weight: bold; margin: 10px;")
            
#             # Update global configuration
#             global DB_CONFIG
#             DB_CONFIG['user'] = self.user_edit.text().strip()
#             DB_CONFIG['password'] = self.password_edit.text()
            
#             # Save configuration (without password)
#             self.save_config()
            
#         else:
#             self.connection_successful = False
#             self.result_text.setStyleSheet("color: #dc3545; background-color: #f8d7da; border-color: #f5c6cb;")
#             self.result_text.setText(f"✗ SETUP FAILED\n{message}")
#             self.proceed_btn.setEnabled(False)
#             self.status_label.setText("✗ Setup failed. Please check credentials and try again.")
#             self.status_label.setStyleSheet("color: #dc3545; font-weight: bold; margin: 10px;")
    
#     def save_config(self):
#         """Save configuration for future use"""
#         try:
#             import json
#             config_file = "db_config.json"
#             safe_config = {
#                 'host': DB_CONFIG['host'],
#                 'port': DB_CONFIG['port'],
#                 'database': DB_CONFIG['database'],
#                 'user': DB_CONFIG['user']
#                 # Don't save password for security
#             }
#             with open(config_file, 'w') as f:
#                 json.dump(safe_config, f, indent=4)
#             logging.info(f"Database configuration saved to {config_file}")
#         except Exception as e:
#             logging.warning(f"Could not save config file: {e}")

# def load_saved_config():
#     """Load saved database configuration"""
#     try:
#         import json
#         config_file = "db_config.json"
#         if os.path.exists(config_file):
#             with open(config_file, 'r') as f:
#                 saved_config = json.load(f)
#                 # Update global config but keep default password
#                 for key, value in saved_config.items():
#                     if key != 'password' and value:
#                         DB_CONFIG[key] = value
#             logging.info("Loaded saved database configuration")
#     except Exception as e:
#         logging.warning(f"Could not load saved config: {e}")

# # ---------------- PostgreSQL Helper Functions ----------------

# def open_db():
#     try:
#         logging.info("Connecting to database...")
#         conn = psycopg2.connect(
#             host=DB_CONFIG['host'],
#             database=DB_CONFIG['database'],
#             user=DB_CONFIG['user'],
#             password=DB_CONFIG['password'],
#             port=DB_CONFIG['port']
#         )
#         logging.info("Database connection successful")
#         return conn
#     except Exception as e:
#         logging.error(f"Database connection error: {str(e)}")
#         raise

# def create_table(conn):
#     """This function is now handled in the setup dialog"""
#     logging.info("Tables already created during setup")
#     return True

# def bulk_insert(conn, records):
#     if not records:
#         logging.warning("No records to insert")
#         return
    
#     try:
#         logging.info(f"Inserting {len(records)} records into database")
#         # Split records into smaller batches to avoid memory issues
#         batch_size = 5000
#         for i in range(0, len(records), batch_size):
#             batch = records[i:i+batch_size]
#             with conn.cursor() as cursor:
#                 query = """
#                     INSERT INTO file_tree
#                     (path, name, type, size, created, modified, accessed, parent_path)
#                     VALUES %s
#                     ON CONFLICT (path) DO NOTHING
#                 """
#                 psycopg2.extras.execute_values(cursor, query, batch)
#             conn.commit()
#             logging.info(f"Inserted batch {i//batch_size + 1} ({len(batch)} records)")
        
#         # Verify insertion
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT COUNT(*) FROM file_tree")
#             count = cursor.fetchone()[0]
#             logging.info(f"Total records in database: {count}")
#     except Exception as e:
#         conn.rollback()
#         logging.error(f"Error inserting records: {str(e)}")
#         raise

# # ---------------- EWF Image Support ----------------

# class EWFImgInfo(pytsk3.Img_Info):
#     def __init__(self, ewf_handle):
#         self._ewf_handle = ewf_handle
#         super(EWFImgInfo, self).__init__(url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)
    
#     def close(self):
#         self._ewf_handle.close()
    
#     def read(self, offset, size):
#         self._ewf_handle.seek(offset)
#         return self._ewf_handle.read(size)
    
#     def get_size(self):
#         return self._ewf_handle.get_media_size()

# # ---------------- Recursive Directory Traversal ----------------

# def list_directory_tree(fs_info, directory, current_path, prefix="", records=None, counts=None):
#     if counts is None:
#         counts = {"directories": 0, "files": 0}
#     if records is None:
#         records = []
    
#     try:
#         logging.info(f"Scanning directory: {current_path}")
#         dir_entries = list(directory)
#         logging.info(f"Found {len(dir_entries)} entries in {current_path}")
        
#         for i, entry in enumerate(dir_entries):
#             if not hasattr(entry, 'info') or not entry.info:
#                 continue
            
#             try:
#                 name = entry.info.name.name.decode('utf-8', errors='replace').strip()
#             except AttributeError:
#                 name = f"[InvalidName_{entry.info.meta.addr}]"
            
#             if name in (".", ".."):
#                 continue
                
#             full_path = "/" + name if current_path == "/" else current_path + "/" + name
#             size = 0
#             created = modified = accessed = None
            
#             if hasattr(entry.info, 'meta') and entry.info.meta:
#                 meta = entry.info.meta
#                 size = meta.size if meta.size is not None else 0
                
#                 if hasattr(meta, 'crtime') and meta.crtime:
#                     created = datetime.fromtimestamp(meta.crtime)
#                 if hasattr(meta, 'mtime') and meta.mtime:
#                     modified = datetime.fromtimestamp(meta.mtime)
#                 if hasattr(meta, 'atime') and meta.atime:
#                     accessed = datetime.fromtimestamp(meta.atime)
            
#             entry_type = "File"
#             if hasattr(entry.info.meta, 'type') and entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
#                 entry_type = "Directory"
#                 counts["directories"] += 1
#             else:
#                 counts["files"] += 1
            
#             # Log every 1000 files to avoid excessive output
#             if len(records) % 1000 == 0 and len(records) > 0:
#                 logging.info(f"Processed {len(records)} files so far")
            
#             records.append((full_path, name, entry_type, size, created, modified, accessed, current_path))
            
#             if entry_type == "Directory":
#                 try:
#                     sub_dir = fs_info.open_dir(inode=entry.info.meta.addr)
#                     list_directory_tree(fs_info, sub_dir, full_path, prefix, records, counts)
#                 except Exception as e:
#                     logging.error(f"Error accessing subdirectory {full_path}: {str(e)}")
#     except Exception as e:
#         logging.error(f"Error listing directory {current_path}: {str(e)}")
    
#     return counts, records

# # [Include all the extraction functions from the original code]

# def preserve_metadata(file_path, created, modified, accessed):
#     if created and modified and accessed:
#         try:
#             os.utime(file_path, (accessed.timestamp(), modified.timestamp()))
#             try:
#                 import win32file, pywintypes
#                 handle = win32file.CreateFile(
#                     file_path,
#                     win32file.GENERIC_WRITE,
#                     win32file.FILE_SHARE_WRITE,
#                     None,
#                     win32file.OPEN_EXISTING,
#                     0,
#                     None
#                 )
#                 win32file.SetFileTime(
#                     handle,
#                     pywintypes.Time(created),
#                     pywintypes.Time(accessed),
#                     pywintypes.Time(modified)
#                 )
#                 handle.close()
#             except ImportError:
#                 logging.warning("To preserve created time on Windows, install pywin32.")
#         except Exception as e:
#             logging.error(f"Error preserving metadata: {str(e)}")

# def extract_file(fs_info, file_entry, dest_path):
#     try:
#         logging.info(f"Extracting file: {dest_path}")
#         os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
#         with open(dest_path, "wb") as f:
#             file_size = file_entry.info.meta.size
#             offset = 0
#             chunk_size = 1024 * 1024  # 1 MB chunks
            
#             while offset < file_size:
#                 data = file_entry.read_random(offset, min(chunk_size, file_size - offset))
#                 if not data:
#                     break
#                 f.write(data)
#                 offset += len(data)
        
#         meta = file_entry.info.meta
#         created = datetime.fromtimestamp(meta.crtime) if hasattr(meta, 'crtime') and meta.crtime else None
#         modified = datetime.fromtimestamp(meta.mtime) if hasattr(meta, 'mtime') and meta.mtime else None
#         accessed = datetime.fromtimestamp(meta.atime) if hasattr(meta, 'atime') and meta.atime else None
        
#         preserve_metadata(dest_path, created, modified, accessed)
#         return True
#     except Exception as e:
#         logging.error(f"Error extracting file {dest_path}: {str(e)}")
#         return False

# def extract_directory(fs_info, directory_entry, dest_dir):
#     try:
#         logging.info(f"Creating directory: {dest_dir}")
#         os.makedirs(dest_dir, exist_ok=True)
        
#         directory = fs_info.open_dir(inode=directory_entry.info.meta.addr)
#         for entry in directory:
#             if not hasattr(entry.info.meta, 'type'):
#                 continue
            
#             try:
#                 name = entry.info.name.name.decode('utf-8', errors='replace').strip()
#             except Exception:
#                 continue
                
#             if name in [".", ".."]:
#                 continue
                
#             dest_path = os.path.join(dest_dir, name)
            
#             if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
#                 extract_directory(fs_info, entry, dest_path)
#             elif entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_REG:
#                 extract_file(fs_info, entry, dest_path)
        
#         return True
#     except Exception as e:
#         logging.error(f"Error extracting directory {dest_dir}: {str(e)}")
#         return False

# def forensic_copy(fs_info, source_path, dest_path):
#     try:
#         entry = fs_info.open(source_path)
        
#         if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
#             return extract_directory(fs_info, entry, dest_path)
#         elif entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_REG:
#             return extract_file(fs_info, entry, dest_path)
#         else:
#             logging.warning(f"Unsupported type for path: {source_path}")
#             return False
#     except Exception as e:
#         logging.error(f"Error extracting {source_path}: {e}")
#         return False

# # [Include all other extraction functions - registry, event logs, etc.]
# # For brevity, I'm including the key ones. All the extraction functions remain the same.

# def extract_registry_hives(fs_info, db_conn, output_dir):
#     try:
#         os.makedirs(output_dir, exist_ok=True)
#         logging.info(f"Extracting registry hives to {output_dir}")
        
#         with db_conn.cursor() as cursor:
#             # Config area hives
#             hive_names = ['SAM', 'SECURITY', 'SOFTWARE', 'SYSTEM']
#             config_query = ("SELECT path, name FROM file_tree "
#                             "WHERE path LIKE %s AND name = ANY(%s) "
#                             "ORDER BY path;")
#             cursor.execute(config_query, ('%/Windows/System32/config/%', hive_names))
#             config_results = cursor.fetchall()
#             logging.info(f"Found {len(config_results)} config hives")

#             # RegBack hives
#             regback_query = ("SELECT path, name FROM file_tree "
#                              "WHERE path LIKE %s AND name = ANY(%s) "
#                              "ORDER BY path;")
#             cursor.execute(regback_query, ('%/Windows/System32/config/RegBack/%', hive_names))
#             regback_results = cursor.fetchall()
#             logging.info(f"Found {len(regback_results)} RegBack hives")

#             # User profile hives
#             user_hives = ['NTUSER.DAT', 'UsrClass.dat']
#             user_query = ("SELECT path, name FROM file_tree "
#                           "WHERE path LIKE %s AND name = ANY(%s) "
#                           "ORDER BY path;")
#             cursor.execute(user_query, ('%/Users/%', user_hives))
#             user_results = cursor.fetchall()
#             logging.info(f"Found {len(user_results)} user hives")

#             # Amcache hive
#             cursor.execute("SELECT path, name FROM file_tree WHERE name = %s;", ('Amcache.hve',))
#             amcache_results = cursor.fetchall()
#             logging.info(f"Found {len(amcache_results)} Amcache hives")

#         # Process all hives
#         for rec in config_results:
#             src, name = rec
#             dest = os.path.join(output_dir, name)
#             logging.info(f"Extracting {src} to {dest}")
#             forensic_copy(fs_info, src, dest)

#         for rec in regback_results:
#             src, name = rec
#             dest = os.path.join(output_dir, f"RegBack_{name}")
#             logging.info(f"Extracting {src} to {dest}")
#             forensic_copy(fs_info, src, dest)

#         for rec in user_results:
#             src, name = rec
#             parts = src.split('/')
#             username = "Unknown"
#             if 'Users' in parts:
#                 idx = parts.index('Users')
#                 if len(parts) > idx+1 and parts[idx+1]:
#                     username = parts[idx+1]
#             new_name = f"{username}_{name}"
#             dest = os.path.join(output_dir, new_name)
#             logging.info(f"Extracting {src} to {dest}")
#             forensic_copy(fs_info, src, dest)

#         for rec in amcache_results:
#             src, name = rec
#             dest = os.path.join(output_dir, name)
#             logging.info(f"Extracting {src} to {dest}")
#             forensic_copy(fs_info, src, dest)
            
#         return True
#     except Exception as e:
#         logging.error(f"Error extracting registry hives: {str(e)}")
#         return False

# # [Include all other extraction functions with the same pattern]

# def setup_database():
#     """Setup database with simplified GUI dialog"""
#     # Load any saved configuration
#     load_saved_config()
    
#     # Create and show database setup dialog
#     app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
    
#     dialog = DatabaseSetupDialog()
#     result = dialog.exec_()
    
#     if result == QDialog.Accepted:
#         logging.info("Database setup completed successfully")
#         return True
#     else:
#         logging.info("Database setup cancelled by user")
#         return False

# if __name__ == "__main__":
#     # This will only run if main.py is executed directly
#     if setup_database():
#         print("Database setup completed. You can now run the GUI.")
#     else:
#         print("Database setup was cancelled.")
import os
import sys
import pytsk3
import pyewf
import psycopg2
import psycopg2.extras
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("forensic_extractor.log"),
        logging.StreamHandler()
    ]
)

# ---------------- PostgreSQL Helper Functions ----------------

def open_db():
    try:
        logging.info("Connecting to database...")
        conn = psycopg2.connect(
            host="localhost",
            database="tape",
            user="postgres",
            password="Supersecured"
        )
        logging.info("Database connection successful")
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        raise

def create_table(conn):
    try:
        logging.info("Creating/verifying table structure...")
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_tree (
                    id BIGSERIAL,
                    path TEXT UNIQUE,
                    name TEXT,
                    type TEXT,
                    size BIGINT,
                    created TIMESTAMP,
                    modified TIMESTAMP,
                    accessed TIMESTAMP,
                    parent_path TEXT
                );
            """)
        conn.commit()
        logging.info("Table structure verified")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error creating table: {str(e)}")
        raise

def bulk_insert(conn, records):
    if not records:
        logging.warning("No records to insert")
        return
    
    try:
        logging.info(f"Inserting {len(records)} records into database")
        # Split records into smaller batches to avoid memory issues
        batch_size = 5000
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO file_tree
                    (path, name, type, size, created, modified, accessed, parent_path)
                    VALUES %s
                    ON CONFLICT (path) DO NOTHING
                """
                psycopg2.extras.execute_values(cursor, query, batch)
            conn.commit()
            logging.info(f"Inserted batch {i//batch_size + 1} ({len(batch)} records)")
        
        # Verify insertion
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM file_tree")
            count = cursor.fetchone()[0]
            logging.info(f"Total records in database: {count}")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error inserting records: {str(e)}")
        raise

# ---------------- EWF Image Support ----------------

class EWFImgInfo(pytsk3.Img_Info):
    def __init__(self, ewf_handle):
        self._ewf_handle = ewf_handle
        super(EWFImgInfo, self).__init__(url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)
    
    def close(self):
        self._ewf_handle.close()
    
    def read(self, offset, size):
        self._ewf_handle.seek(offset)
        return self._ewf_handle.read(size)
    
    def get_size(self):
        return self._ewf_handle.get_media_size()

# ---------------- Recursive Directory Traversal ----------------

def list_directory_tree(fs_info, directory, current_path, prefix="", records=None, counts=None):
    if counts is None:
        counts = {"directories": 0, "files": 0}
    if records is None:
        records = []
    
    try:
        logging.info(f"Scanning directory: {current_path}")
        dir_entries = list(directory)
        logging.info(f"Found {len(dir_entries)} entries in {current_path}")
        
        for i, entry in enumerate(dir_entries):
            if not hasattr(entry, 'info') or not entry.info:
                continue
            
            try:
                name = entry.info.name.name.decode('utf-8', errors='replace').strip()
            except AttributeError:
                name = f"[InvalidName_{entry.info.meta.addr}]"
            
            if name in (".", ".."):
                continue
                
            full_path = "/" + name if current_path == "/" else current_path + "/" + name
            size = 0
            created = modified = accessed = None
            
            if hasattr(entry.info, 'meta') and entry.info.meta:
                meta = entry.info.meta
                size = meta.size if meta.size is not None else 0
                
                if hasattr(meta, 'crtime') and meta.crtime:
                    created = datetime.fromtimestamp(meta.crtime)
                if hasattr(meta, 'mtime') and meta.mtime:
                    modified = datetime.fromtimestamp(meta.mtime)
                if hasattr(meta, 'atime') and meta.atime:
                    accessed = datetime.fromtimestamp(meta.atime)
            
            entry_type = "File"
            if hasattr(entry.info.meta, 'type') and entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                entry_type = "Directory"
                counts["directories"] += 1
            else:
                counts["files"] += 1
            
            # Log every 1000 files to avoid excessive output
            if len(records) % 1000 == 0 and len(records) > 0:
                logging.info(f"Processed {len(records)} files so far")
            
            records.append((full_path, name, entry_type, size, created, modified, accessed, current_path))
            
            if entry_type == "Directory":
                try:
                    sub_dir = fs_info.open_dir(inode=entry.info.meta.addr)
                    list_directory_tree(fs_info, sub_dir, full_path, prefix, records, counts)
                except Exception as e:
                    logging.error(f"Error accessing subdirectory {full_path}: {str(e)}")
    except Exception as e:
        logging.error(f"Error listing directory {current_path}: {str(e)}")
    
    return counts, records

# ---------------- File and Directory Extraction ----------------

def preserve_metadata(file_path, created, modified, accessed):
    if created and modified and accessed:
        try:
            os.utime(file_path, (accessed.timestamp(), modified.timestamp()))
            try:
                import win32file, pywintypes
                handle = win32file.CreateFile(
                    file_path,
                    win32file.GENERIC_WRITE,
                    win32file.FILE_SHARE_WRITE,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None
                )
                win32file.SetFileTime(
                    handle,
                    pywintypes.Time(created),
                    pywintypes.Time(accessed),
                    pywintypes.Time(modified)
                )
                handle.close()
            except ImportError:
                logging.warning("To preserve created time on Windows, install pywin32.")
        except Exception as e:
            logging.error(f"Error preserving metadata: {str(e)}")

def extract_file(fs_info, file_entry, dest_path):
    try:
        logging.info(f"Extracting file: {dest_path}")
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        with open(dest_path, "wb") as f:
            file_size = file_entry.info.meta.size
            offset = 0
            chunk_size = 1024 * 1024  # 1 MB chunks
            
            while offset < file_size:
                data = file_entry.read_random(offset, min(chunk_size, file_size - offset))
                if not data:
                    break
                f.write(data)
                offset += len(data)
        
        meta = file_entry.info.meta
        created = datetime.fromtimestamp(meta.crtime) if hasattr(meta, 'crtime') and meta.crtime else None
        modified = datetime.fromtimestamp(meta.mtime) if hasattr(meta, 'mtime') and meta.mtime else None
        accessed = datetime.fromtimestamp(meta.atime) if hasattr(meta, 'atime') and meta.atime else None
        
        preserve_metadata(dest_path, created, modified, accessed)
        return True
    except Exception as e:
        logging.error(f"Error extracting file {dest_path}: {str(e)}")
        return False

def extract_directory(fs_info, directory_entry, dest_dir):
    try:
        logging.info(f"Creating directory: {dest_dir}")
        os.makedirs(dest_dir, exist_ok=True)
        
        directory = fs_info.open_dir(inode=directory_entry.info.meta.addr)
        for entry in directory:
            if not hasattr(entry.info.meta, 'type'):
                continue
            
            try:
                name = entry.info.name.name.decode('utf-8', errors='replace').strip()
            except Exception:
                continue
                
            if name in [".", ".."]:
                continue
                
            dest_path = os.path.join(dest_dir, name)
            
            if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                extract_directory(fs_info, entry, dest_path)
            elif entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_REG:
                extract_file(fs_info, entry, dest_path)
        
        return True
    except Exception as e:
        logging.error(f"Error extracting directory {dest_dir}: {str(e)}")
        return False

def forensic_copy(fs_info, source_path, dest_path):
    try:
        entry = fs_info.open(source_path)
        
        if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
            return extract_directory(fs_info, entry, dest_path)
        elif entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_REG:
            return extract_file(fs_info, entry, dest_path)
        else:
            logging.warning(f"Unsupported type for path: {source_path}")
            return False
    except Exception as e:
        logging.error(f"Error extracting {source_path}: {e}")
        return False

# ---------------- Registry and Event Log Extraction Functions ----------------

def extract_registry_hives(fs_info, db_conn, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Extracting registry hives to {output_dir}")
        
        with db_conn.cursor() as cursor:
            # Config area hives
            hive_names = ['SAM', 'SECURITY', 'SOFTWARE', 'SYSTEM']
            config_query = ("SELECT path, name FROM file_tree "
                            "WHERE path LIKE %s AND name = ANY(%s) "
                            "ORDER BY path;")
            cursor.execute(config_query, ('%/Windows/System32/config/%', hive_names))
            config_results = cursor.fetchall()
            logging.info(f"Found {len(config_results)} config hives")

            # RegBack hives
            regback_query = ("SELECT path, name FROM file_tree "
                             "WHERE path LIKE %s AND name = ANY(%s) "
                             "ORDER BY path;")
            cursor.execute(regback_query, ('%/Windows/System32/config/RegBack/%', hive_names))
            regback_results = cursor.fetchall()
            logging.info(f"Found {len(regback_results)} RegBack hives")

            # User profile hives
            user_hives = ['NTUSER.DAT', 'UsrClass.dat']
            user_query = ("SELECT path, name FROM file_tree "
                          "WHERE path LIKE %s AND name = ANY(%s) "
                          "ORDER BY path;")
            cursor.execute(user_query, ('%/Users/%', user_hives))
            user_results = cursor.fetchall()
            logging.info(f"Found {len(user_results)} user hives")

            # Amcache hive
            cursor.execute("SELECT path, name FROM file_tree WHERE name = %s;", ('Amcache.hve',))
            amcache_results = cursor.fetchall()
            logging.info(f"Found {len(amcache_results)} Amcache hives")

        # Process config area hives
        for rec in config_results:
            src, name = rec
            dest = os.path.join(output_dir, name)
            logging.info(f"Extracting {src} to {dest}")
            forensic_copy(fs_info, src, dest)

        # Process RegBack hives
        for rec in regback_results:
            src, name = rec
            dest = os.path.join(output_dir, f"RegBack_{name}")
            logging.info(f"Extracting {src} to {dest}")
            forensic_copy(fs_info, src, dest)

        # Process user profile hives
        for rec in user_results:
            src, name = rec
            parts = src.split('/')
            username = "Unknown"
            if 'Users' in parts:
                idx = parts.index('Users')
                if len(parts) > idx+1 and parts[idx+1]:
                    username = parts[idx+1]
            new_name = f"{username}_{name}"
            dest = os.path.join(output_dir, new_name)
            logging.info(f"Extracting {src} to {dest}")
            forensic_copy(fs_info, src, dest)

        # Process Amcache hive
        for rec in amcache_results:
            src, name = rec
            dest = os.path.join(output_dir, name)
            logging.info(f"Extracting {src} to {dest}")
            forensic_copy(fs_info, src, dest)
            
        return True
    except Exception as e:
        logging.error(f"Error extracting registry hives: {str(e)}")
        return False

def extract_event_logs(fs_info, db_conn, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Extracting event logs to {output_dir}")
        
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT path FROM file_tree WHERE path LIKE %s AND type = 'File' LIMIT 100;", ("%/Windows/System32/winevt/Logs/%",))
            results = cursor.fetchall()
            
        if not results:
            logging.warning("No event logs found in the database.")
            return False
            
        logging.info(f"Found {len(results)} event log files")
        
        for rec in results:
            src = rec[0]
            filename = os.path.basename(src)
            dest = os.path.join(output_dir, filename)
            logging.info(f"Extracting {src} to {dest}")
            forensic_copy(fs_info, src, dest)
            
        return True
    except Exception as e:
        logging.error(f"Error extracting event logs: {str(e)}")
        return False

def extract_username(config_results, pos=0):
    usernames = []
    for item in config_results:
        try:
            path = item[pos]
            parts = path.split('/')
            if len(parts) > 2:
                username = parts[2]
                usernames.append(username)
                logging.info(f"Found username: {username}")
        except Exception as e:
            logging.error(f"Error extracting username: {str(e)}")
    return usernames

def extract_edge_directory(fs_info, db_conn, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Extracting Edge browser data to {output_dir}")
        
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT path FROM file_tree WHERE path LIKE '/Users/%/AppData/Local/Microsoft/Edge/User Data/Default';")
            config_results = cursor.fetchall()
            
        if not config_results:
            logging.warning("No Edge browser artifacts present")
            return False
            
        usernames = extract_username(config_results, pos=0)
        
        for username in usernames:
            dest = os.path.join(output_dir, username, "Default")
            src_dir = f"/Users/{username}/AppData/Local/Microsoft/Edge/User Data/Default"
            logging.info(f"Extracting Edge data for user {username}")
            forensic_copy(fs_info, src_dir, dest)
            
        return True
    except Exception as e:
        logging.error(f"Error extracting Edge directory: {str(e)}")
        return False

def extract_chrome_directory(fs_info, db_conn, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Extracting Chrome browser data to {output_dir}")
        
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT path FROM file_tree WHERE path LIKE '/Users/%/AppData/Local/Google/Chrome/User Data/Default';")
            config_results = cursor.fetchall()
            
        if not config_results:
            logging.warning("No Chrome browser artifacts present")
            return False
            
        usernames = extract_username(config_results, pos=0)
        
        for username in usernames:
            dest = os.path.join(output_dir, username, "Default")
            src_dir = f"/Users/{username}/AppData/Local/Google/Chrome/User Data/Default"
            logging.info(f"Extracting Chrome data for user {username}")
            forensic_copy(fs_info, src_dir, dest)
            
        return True
    except Exception as e:
        logging.error(f"Error extracting Chrome directory: {str(e)}")
        return False

def extract_sru_mft_pagefile(fs_info, db_conn, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Extracting SRU/MFT/pagefile to {output_dir}")
        
        sru_path = "/Windows/System32/sru/SRUDB.dat"
        mft_path = "/$MFT"
        pagefile_path = "/pagefile.sys"
        
        logging.info("Extracting SRU database...")
        forensic_copy(fs_info, sru_path, f"{output_dir}/SRUDB.dat")
        
        logging.info("Extracting MFT...")
        forensic_copy(fs_info, mft_path, f"{output_dir}/$MFT")
        
        logging.info("Extracting pagefile...")
        forensic_copy(fs_info, pagefile_path, f"{output_dir}/pagefile.sys")
        
        return True
    except Exception as e:
        logging.error(f"Error extracting SRU/MFT/pagefile: {str(e)}")
        return False

def extract_powershell_console_history(fs_info, db_conn, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Extracting PowerShell console history to {output_dir}")
        
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT path FROM file_tree WHERE path ILIKE '%ConsoleHost_history.txt%';")
            config_results = cursor.fetchall()
            
        if not config_results:
            logging.warning("No PowerShell console history present")
            return False
            
        usernames = extract_username(config_results, pos=0)
        
        for username in usernames:
            dest = os.path.join(output_dir, f"{username}_ConsoleHost_history.txt")
            src_dir = f"/Users/{username}/AppData/Roaming/Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt"
            logging.info(f"Extracting PowerShell history for user {username}")
            forensic_copy(fs_info, src_dir, dest)
            
        return True
    except Exception as e:
        logging.error(f"Error extracting PowerShell console history: {str(e)}")
        return False

def extract_prefetch_files(fs_info, db_conn, output_dir):
    try:
        prefetch_dir = os.path.join(output_dir, "Prefetch")
        os.makedirs(prefetch_dir, exist_ok=True)
        logging.info(f"Extracting prefetch files to {prefetch_dir}")
        
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT path, name FROM file_tree WHERE path ILIKE '/Windows/Prefetch/%.pf';")
            config_results = cursor.fetchall()
            
        if not config_results:
            logging.warning("No prefetch files present")
            return False
            
        for rec in config_results:
            src_path, name = rec
            dest = os.path.join(prefetch_dir, name)
            logging.info(f"Extracting prefetch file: {name}")
            forensic_copy(fs_info, src_path, dest)
            
        return True
    except Exception as e:
        logging.error(f"Error extracting prefetch files: {str(e)}")
        return False

def extract_activitiesCache_db(fs_info, db_conn, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Extracting ActivityCache.db to {output_dir}")
        
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT path FROM file_tree WHERE path ILIKE '%ActivitiesCache.db';")
            config_results = cursor.fetchall()
            
        if not config_results:
            logging.warning("No ActivityCache DB file present")
            return False
            
        for rec in config_results:
            src_dir = rec[0]
            parts = src_dir.split('/')
            user = "Unknown"
            if len(parts) > 2:
                user = parts[2]
            dest = os.path.join(output_dir, f"{user}_ActivityCache.db")
            logging.info(f"Extracting ActivityCache for user {user}")
            forensic_copy(fs_info, src_dir, dest)
            
        return True
    except Exception as e:
        logging.error(f"Error extracting ActivitiesCache DB: {str(e)}")
        return False

