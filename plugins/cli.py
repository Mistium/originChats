import os
import sys
import asyncio
import time
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import channels, users, roles
from logger import Logger

REQUIRED_PERMISSIONS = ["owner", "admin"]
COMMAND_PREFIX = "!"


def getInfo():
    return {
        "name": "CLI Plugin",
        "description": "Manage your server, channels, and users through chat commands.",
        "handles": ["new_message"]
    }


class CommandHandler:
    
    def __init__(self, ws, channel, server_data):
        self.ws = ws
        self.channel = channel
        self.server_data = server_data
        self.username = getattr(ws, 'username', None)
        
    def reply(self, message):
        send_message_to_channel(self.channel, message, self.server_data)
    
    def error(self, message):
        self.reply(f"❌ Error: {message}")
    
    def success(self, message):
        self.reply(f"✅ {message}")


class UserCommands:
    
    @staticmethod
    def ban(handler, args):
        if len(args) < 1:
            return handler.error("Usage: ban <username>")
        
        username = args[0]
        if users.ban_user(username):
            if handler.server_data and "connected_clients" in handler.server_data:
                from handlers.websocket_utils import disconnect_user
                loop = asyncio.get_event_loop()
                loop.create_task(disconnect_user(
                    handler.server_data["connected_clients"],
                    username,
                    "You have been banned from this server"
                ))
            handler.success(f"Banned user '{username}'")
        else:
            handler.error(f"Failed to ban user '{username}'")
    
    @staticmethod
    def unban(handler, args):
        if len(args) < 1:
            return handler.error("Usage: unban <username>")
        
        username = args[0]
        if users.unban_user(username):
            handler.success(f"Unbanned user '{username}'")
        else:
            handler.error(f"Failed to unban '{username}'")
    
    @staticmethod
    def banned(handler, args):
        banned_users = users.get_banned_users()
        if banned_users:
            handler.reply("🚫 Banned users:\n" + "\n".join(f"  • {user}" for user in banned_users))
        else:
            handler.reply("No users are currently banned")
    
    @staticmethod
    def users_list(handler, args):
        user_list = users.get_users()
        if user_list:
            lines = ["👥 Users:"]
            for user in user_list:
                roles_str = ", ".join(user.get('roles', []))
                lines.append(f"  • {user['username']} ({roles_str})")
            handler.reply("\n".join(lines))
        else:
            handler.reply("No users found")


class ChannelCommands:
    
    @staticmethod
    def channels_list(handler, args):
        channel_list = channels.get_channels()
        if channel_list:
            lines = ["📋 Channels:"]
            for ch in channel_list:
                ch_type = ch.get('type', 'unknown')
                lines.append(f"  • {ch.get('name', 'unnamed')} ({ch_type})")
            handler.reply("\n".join(lines))
        else:
            handler.reply("No channels found")
    
    @staticmethod
    def create_channel(handler, args):
        if len(args) < 2:
            return handler.error("Usage: create <name> <type>\nTypes: text, separator")
        
        name, ch_type = args[0], args[1].lower()
        if ch_type not in ["text", "separator"]:
            return handler.error("Invalid type. Use 'text' or 'separator'")
        
        if channels.create_channel(name, ch_type):
            handler.success(f"Created channel '{name}' ({ch_type})")
        else:
            handler.error(f"Failed to create channel (may already exist)")
    
    @staticmethod
    def delete_channel(handler, args):
        if len(args) < 1:
            return handler.error("Usage: delete <name>")
        
        name = args[0]
        if channels.delete_channel(name):
            handler.success(f"Deleted channel '{name}'")
        else:
            handler.error(f"Failed to delete channel '{name}'")
    
    @staticmethod
    def channel_info(handler, args):
        if len(args) < 1:
            return handler.error("Usage: info <name>")
        
        name = args[0]
        info = channels.get_channel(name)
        if info:
            lines = [
                f"📌 Channel: {info.get('name', 'unnamed')}",
                f"   Type: {info.get('type', 'unknown')}"
            ]
            if "permissions" in info:
                lines.append("   Permissions:")
                for role, perms in info["permissions"].items():
                    lines.append(f"     • {role}: {', '.join(perms)}")
            handler.reply("\n".join(lines))
        else:
            handler.error(f"Channel '{name}' not found")


class RoleCommands:
    
    @staticmethod
    def roles_list(handler, args):
        all_roles = roles.get_all_roles()
        if all_roles:
            lines = ["🎭 Roles:"]
            for role_name, role_data in all_roles.items():
                color = role_data.get('color', 'default')
                lines.append(f"  • {role_name} (color: {color})")
            handler.reply("\n".join(lines))
        else:
            handler.reply("No roles found")
    
    @staticmethod
    def create_role(handler, args):
        if len(args) < 1:
            return handler.error("Usage: createrole <name>")
        
        role_name = args[0]
        if roles.add_role(role_name, {}):
            handler.success(f"Created role '{role_name}'")
        else:
            handler.error(f"Failed to create role (may already exist)")
    
    @staticmethod
    def delete_role(handler, args):
        if len(args) < 1:
            return handler.error("Usage: deleterole <name>")
        
        role_name = args[0]
        if roles.delete_role(role_name):
            handler.success(f"Deleted role '{role_name}'")
        else:
            handler.error(f"Failed to delete role '{role_name}'")
    
    @staticmethod
    def give_role(handler, args):
        if len(args) < 2:
            return handler.error("Usage: give <username> <role>")
        
        username, role_name = args[0], args[1]
        if users.give_role(username, role_name):
            handler.success(f"Gave role '{role_name}' to '{username}'")
        else:
            handler.error(f"Failed to give role")
    
    @staticmethod
    def remove_role(handler, args):
        if len(args) < 2:
            return handler.error("Usage: remove <username> <role>")
        
        username, role_name = args[0], args[1]
        if users.remove_role(username, role_name):
            handler.success(f"Removed role '{role_name}' from '{username}'")
        else:
            handler.error(f"Failed to remove role")
    
    @staticmethod
    def rolecolor(handler, args):
        if len(args) < 2:
            return handler.error("Usage: rolecolor <role> <color>")
        
        role_name, color = args[0], args[1]
        if roles.update_role_key(role_name, "color", color):
            handler.success(f"Updated color for role '{role_name}'")
        else:
            handler.error(f"Failed to update role color")


class ModerationCommands:
    
    @staticmethod
    def purge(handler, args):
        if len(args) < 1 or not args[0].isdigit():
            return handler.error("Usage: purge <count>")
        
        count = int(args[0])
        if count <= 0:
            return handler.error("Count must be greater than 0")
        
        if channels.purge_messages(handler.channel, count):
            handler.success(f"Purged {count} messages")
        else:
            handler.error("Failed to purge messages")


COMMANDS = {
    "ban": UserCommands.ban,
    "unban": UserCommands.unban,
    "banned": UserCommands.banned,
    "users": UserCommands.users_list,
    "channels": ChannelCommands.channels_list,
    "create": ChannelCommands.create_channel,
    "delete": ChannelCommands.delete_channel,
    "info": ChannelCommands.channel_info,
    "roles": RoleCommands.roles_list,
    "createrole": RoleCommands.create_role,
    "deleterole": RoleCommands.delete_role,
    "give": RoleCommands.give_role,
    "remove": RoleCommands.remove_role,
    "rolecolor": RoleCommands.rolecolor,
    "purge": ModerationCommands.purge,
}


def show_help(handler, args):
    if args and args[0] in COMMANDS:
        cmd = args[0]
        func = COMMANDS[cmd]
        doc = func.__doc__ or "No help available"
        handler.reply(f"📖 {doc}")
    else:
        lines = ["📖 Available Commands:", ""]
        
        categories = {
            "User Management": ["ban", "unban", "banned", "users"],
            "Channel Management": ["channels", "create", "delete", "info"],
            "Role Management": ["roles", "createrole", "deleterole", "give", "remove", "rolecolor"],
            "Moderation": ["purge"]
        }
        
        for category, cmds in categories.items():
            lines.append(f"**{category}**")
            for cmd in cmds:
                if cmd in COMMANDS:
                    lines.append(f"  !{cmd}")
            lines.append("")
        
        lines.append("💡 Use !help <command> for detailed help")
        handler.reply("\n".join(lines))


COMMANDS["help"] = show_help


def send_message_to_channel(channel, content, server_data):
    from handlers.websocket_utils import broadcast_to_all
    
    message = {
        "user": "OriginChats",
        "content": content.strip(),
        "timestamp": time.time(),
        "type": "message",
        "pinned": False,
        "id": str(uuid.uuid4())
    }
    
    channels.save_channel_message(channel, message)
    
    if server_data and "connected_clients" in server_data:
        broadcast_msg = {
            "cmd": "message_new",
            "message": message,
            "channel": channel,
            "global": True
        }
        loop = asyncio.get_event_loop()
        loop.create_task(broadcast_to_all(server_data["connected_clients"], broadcast_msg))


def on_new_message(ws, message_data, server_data=None):
    if not ws or not getattr(ws, 'authenticated', False):
        Logger.warning("Authentication check failed")
        return
    
    username = getattr(ws, 'username', None)
    user_roles = users.get_user_roles(username)
    
    if not user_roles or not any(role in user_roles for role in REQUIRED_PERMISSIONS):
        return
    
    content = message_data.get("content", "").strip()
    if not content.startswith(COMMAND_PREFIX):
        return
    
    parts = content[len(COMMAND_PREFIX):].split()
    if not parts:
        return
    
    command = parts[0].lower()
    args = parts[1:]
    
    channel = message_data.get("channel", "general")
    handler = CommandHandler(ws, channel, server_data)
    
    if command in COMMANDS:
        try:
            COMMANDS[command](handler, args)
        except Exception as e:
            Logger.error(f"Error executing command '{command}': {e}")
            handler.error(f"Command failed: {str(e)}")
    else:
        handler.reply(f"Unknown command: {command}\nUse !help for a list of commands")