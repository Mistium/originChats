import json, os

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

channels_db_dir = os.path.join(_MODULE_DIR, "channels")
channels_index = os.path.join(_MODULE_DIR, "channels.json")

def get_channel_messages(channel_name, limit=100):
    """
    Retrieve messages from a specific channel.

    Args:
        channel_name (str): The name of the channel to retrieve messages from.
        limit (int): The maximum number of messages to retrieve.

    Returns:
        list: A list of messages from the specified channel.
    """
    # Load the channel data
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)
    except FileNotFoundError:
        return []

    # Return the last 'limit' messages
    return channel_data[-limit:]

def save_channel_message(channel_name, message):
    """
    Save a message to a specific channel.

    Args:
        channel_name (str): The name of the channel to save the message to.
        message (dict): The message to save, should contain 'user', 'content', and 'timestamp'.

    Returns:
        bool: True if the message was saved successfully, False otherwise.
    """
    # Ensure the channels directory exists
    os.makedirs(channels_db_dir, exist_ok=True)
    
    # Load existing channel data or create a new one
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)
    except FileNotFoundError:
        channel_data = []

    # Append the new message
    channel_data.append(message)

    # Save the updated channel data with compact formatting
    with open(f"{channels_db_dir}/{channel_name}.json", 'w') as f:
        json.dump(channel_data, f, separators=(',', ':'), ensure_ascii=False)

    return True

def get_all_channels_for_roles(roles):
    """
    Get all channels available for the specified roles.

    Args:
        roles (list): A list of roles to filter channels by.

    Returns:
        list: A list of channel info dicts available for the specified roles.
    """
    channels = []
    try:
        with open(channels_index, 'r') as f:
            all_channels = json.load(f)
        for channel in all_channels:
            permissions = channel.get("permissions", {})
            view_roles = permissions.get("view", [])
            if any(role in view_roles for role in roles):
                channels.append(channel)
    except FileNotFoundError:
        return []
    return channels

def edit_channel_message(channel_name, message_id, new_content):
    """
    Edit a message in a specific channel.

    Args:
        channel_name (str): The name of the channel.
        message_id (str): The ID of the message to edit.
        new_content (str): The new content for the message.

    Returns:
        bool: True if the message was edited successfully, False otherwise.
    """
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)

        for msg in channel_data:
            if msg.get("id") == message_id:
                msg["content"] = new_content
                break
        else:
            return False  # Message not found

        # Ensure the channels directory exists
        os.makedirs(channels_db_dir, exist_ok=True)
        
        with open(f"{channels_db_dir}/{channel_name}.json", 'w') as f:
            json.dump(channel_data, f, separators=(',', ':'), ensure_ascii=False)

        return True
    except FileNotFoundError:
        return False

def get_channel_message(channel_name, message_id):
    """
    Retrieve a specific message from a channel by its ID.

    Args:
        channel_name (str): The name of the channel.
        message_id (str): The ID of the message to retrieve.

    Returns:
        dict: The message if found, None otherwise.
    """
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)

        for msg in channel_data:
            if msg.get("id") == message_id:
                return msg
        return None  # Message not found
    except FileNotFoundError:
        return None  # Channel not found
    
def does_user_have_permission(channel_name, user_roles, permission_type):
    """
    Check if a user with specific roles has permission to perform an action on a channel.

    Args:
        channel_name (str): The name of the channel.
        user_roles (list): A list of roles assigned to the user.
        permission_type (str): The type of permission to check (e.g., "view", "edit").

    Returns:
        bool: True if the user has the required permission, False otherwise.
    """
    try:
        with open(channels_index, 'r') as f:
            channels_data = json.load(f)

        for channel in channels_data:
            if channel.get("name") == channel_name:
                permissions = channel.get("permissions", {})
                allowed_roles = permissions.get(permission_type, [])
                return any(role in allowed_roles for role in user_roles)
    except FileNotFoundError:
        return False  # Channel index not found

    return False  # Channel not found
    
def delete_channel_message(channel_name, message_id):
    """
    Delete a message from a specific channel.

    Args:
        channel_name (str): The name of the channel.
        message_id (str): The ID of the message to delete.

    Returns:
        bool: True if the message was deleted successfully, False otherwise.
    """
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)

        new_data = [msg for msg in channel_data if msg.get("id") != message_id]

        # Ensure the channels directory exists
        os.makedirs(channels_db_dir, exist_ok=True)
        
        with open(f"{channels_db_dir}/{channel_name}.json", 'w') as f:
            json.dump(new_data, f, separators=(',', ':'), ensure_ascii=False)

        return True
    except FileNotFoundError:
        return False
    
def get_channels():
    """
    Get all channels from the channels index.

    Returns:
        list: A list of channel info dicts.
    """
    try:
        with open(channels_index, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # No channels found
    
def create_channel(channel_name, channel_type):
    """
    Create a new channel.

    Args:
        channel_name (str): The name of the channel to create.
        channel_type (str): The type of the channel (e.g., "text", "voice").

    Returns:
        bool: True if the channel was created successfully, False if it already exists.
    """
    try:
        with open(channels_index, 'r') as f:
            channels = json.load(f)
    except FileNotFoundError:
        channels = []

    # Check if the channel already exists
    if any(channel.get('name') == channel_name for channel in channels):
        return False  # Channel already exists

    new_channel = {
        "name": channel_name,
        "type": channel_type,
        "permissions": {
            "view": ["owner"],
            "edit": ["owner"],
            "send": ["owner"]
        }
    }

    channels.append(new_channel)

    # Save the updated channels index
    with open(channels_index, 'w') as f:
        json.dump(channels, f, indent=4)

    return True

def delete_channel(channel_name):
    """
    Delete a channel.

    Args:
        channel_name (str): The name of the channel to delete.

    Returns:
        bool: True if the channel was deleted successfully, False if it does not exist.
    """
    try:
        with open(channels_index, 'r') as f:
            channels = json.load(f)
        
        new_channels = [channel for channel in channels if channel['name'] != channel_name]

        if len(new_channels) == len(channels):
            return False  # Channel not found

        # Save the updated channels index
        with open(channels_index, 'w') as f:
            json.dump(new_channels, f, indent=4)

        # Remove the channel's message file
        os.remove(f"{channels_db_dir}/{channel_name}.json")

        return True
    except FileNotFoundError:
        return False  # Channels index not found
    
def set_channel_permissions(channel_name, role, permission, allow=True):
    """
    Set permissions for a specific role on a channel.

    Args:
        channel_name (str): The name of the channel.
        role (str): The role to set permissions for.
        permission (str): The permission to set (e.g., "view", "edit", "send").

    Returns:
        bool: True if permissions were set successfully, False if the channel does not exist.
    """
    try:
        with open(channels_index, 'r') as f:
            channels = json.load(f)

        for channel in channels:
            if channel['name'] == channel_name:
                if permission not in channel['permissions']:
                    channel['permissions'][permission] = []
                if role not in channel['permissions'][permission]:
                    if allow:
                        channel['permissions'][permission].append(role)
                    else:                        # If removing permission, ensure the role exists before removing
                        if role in channel['permissions'][permission]:
                            channel['permissions'][permission].remove(role)
                
                # Save the updated channels index
                with open(channels_index, 'w') as f:
                    json.dump(channels, f, indent=4)
                
                return True
        
        return False  # Channel not found
    except FileNotFoundError:
        return False  # Channels index not found
    
def reorder_channel(channel_name, new_position):
    """
    Reorder a channel in the channels index.

    Args:
        channel_name (str): The name of the channel to reorder.
        new_position (int): The new position for the channel (0-based index).

    Returns:
        bool: True if the channel was reordered successfully, False if it does not exist.
    """
    try:
        with open(channels_index, 'r') as f:
            channels = json.load(f)

        for i, channel in enumerate(channels):
            if channel['name'] == channel_name:
                # Remove the channel from its current position
                channels.pop(i)
                # Insert it at the new position
                channels.insert(int(new_position), channel)

                # Save the updated channels index
                with open(channels_index, 'w') as f:
                    json.dump(channels, f, indent=4)
                
                return True
        
        return False  # Channel not found
    except FileNotFoundError:
        return False  # Channels index not found

def get_message_replies(channel_name, message_id, limit=50):
    """
    Get all replies to a specific message.

    Args:
        channel_name (str): The name of the channel.
        message_id (str): The ID of the message to get replies for.
        limit (int): Maximum number of replies to return.

    Returns:
        list: A list of messages that are replies to the specified message.
    """
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)

        replies = []
        for msg in channel_data:
            if msg.get("reply_to", {}).get("id") == message_id:
                replies.append(msg)
                if len(replies) >= limit:
                    break
        
        return replies
    except FileNotFoundError:
        return []  # Channel not found
    
def purge_messages(channel_name, count):
    """
    Purge the last 'count' messages from a channel.

    Args:
        channel_name (str): The name of the channel.
        count (int): The number of messages to purge.

    Returns:
        bool: True if messages were purged successfully, False if the channel does not exist or has fewer messages.
    """
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)

        if len(channel_data) < count:
            return False  # Not enough messages to purge

        # Remove the last 'count' messages
        new_data = channel_data[:-count]

        # Save the updated channel data
        with open(f"{channels_db_dir}/{channel_name}.json", 'w') as f:
            json.dump(new_data, f, separators=(',', ':'), ensure_ascii=False)

        return True
    except FileNotFoundError:
        return False  # Channel not found

def can_user_delete_own(channel_name, user_roles):
    """
    Check if a user with specific roles can delete their own message in a channel.
    If the channel does not specify delete_own, all roles are allowed by default.
    """
    try:
        with open(channels_index, 'r') as f:
            channels_data = json.load(f)
        for channel in channels_data:
            if channel.get("name") == channel_name:
                permissions = channel.get("permissions", {})
                if "delete_own" not in permissions:
                    return True  # Default: all roles can delete their own messages
                allowed_roles = permissions.get("delete_own", [])
                return any(role in allowed_roles for role in user_roles)
    except FileNotFoundError:
        return True  # Default to True if channel index not found
    return True  # Default to True if channel not found

def can_user_edit_own(channel_name, user_roles):
    """
    Check if a user with specific roles can edit their own message in a channel.
    If the channel does not specify edit_own, all roles are allowed by default.
    """
    try:
        with open(channels_index, 'r') as f:
            channels_data = json.load(f)
        for channel in channels_data:
            if channel.get("name") == channel_name:
                permissions = channel.get("permissions", {})
                if "edit_own" not in permissions:
                    return True  # Default: all roles can edit their own messages
                allowed_roles = permissions.get("edit_own", [])
                return any(role in allowed_roles for role in user_roles)
    except FileNotFoundError:
        return True  # Default to True if channel index not found
    return True  # Default to True if channel not found