import asyncio
import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from db import users, channels, roles
from logger import Logger

class FileWatcher(FileSystemEventHandler):
    """File system event handler for watching JSON files"""
    
    def __init__(self, broadcast_func, main_loop):
        self.broadcast_func = broadcast_func
        self.main_loop = main_loop
        
        # Cache for tracking changes
        self._users_cache = {}
        self._channels_cache = []
        
        # Initialize caches
        self._load_initial_state()
        super().__init__()
    
    def _load_initial_state(self):
        """Load initial state of files to track changes"""
        try:
            with open(users.users_index, 'r') as f:
                self._users_cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._users_cache = {}
        
        try:
            with open(channels.channels_index, 'r') as f:
                self._channels_cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._channels_cache = []
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        filename = os.path.basename(event.src_path)
             # Handle users.json changes
        if filename == 'users.json' or filename == 'roles.json':
            Logger.edit(f"Users file changed: {event.src_path}")
            asyncio.run_coroutine_threadsafe(
                self._handle_users_change(), 
                self.main_loop
            )
        
        # Handle channels.json changes
        elif filename == 'channels.json':
            Logger.edit(f"Channels file changed: {event.src_path}")
            asyncio.run_coroutine_threadsafe(
                self._handle_channels_change(),
                self.main_loop
            )
    
    async def _handle_users_change(self):
        try:
            await self.broadcast_func({
                "cmd": "users_list",
                "users": users.get_users()
            })
            
        except Exception as e:
            Logger.error(f"Error handling users.json change: {e}")
    
    async def _handle_channels_change(self):
        """Handle channels.json file changes"""
        try:
            # Load new channels data
            with open(channels.channels_index, 'r') as f:
                new_channels = json.load(f)
            
            await self.broadcast_func({
                "cmd": "channels_get",
                "val": new_channels
            })
            
        except Exception as e:
            Logger.error(f"Error handling channels.json change: {e}")

def setup_file_watchers(broadcast_func, main_loop):
    """Setup file watchers for users.json and channels.json"""
    
    # Get the database directory
    db_dir = os.path.dirname(users.users_index)
    
    # Create event handler
    event_handler = FileWatcher(broadcast_func, main_loop)
    
    # Create observer
    observer = Observer()
    observer.schedule(event_handler, db_dir, recursive=False)
    
    # Start watching
    observer.start()
    Logger.success(f"File watcher started for directory: {db_dir}")
    
    return observer
