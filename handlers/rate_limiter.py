import time
from collections import defaultdict, deque
import threading

class RateLimiter:
    """Thread-safe rate limiter for user messages"""
    
    def __init__(self, messages_per_minute=30, burst_limit=5, cooldown_seconds=60):
        self.messages_per_minute = messages_per_minute
        self.burst_limit = burst_limit
        self.cooldown_seconds = cooldown_seconds
        
        # Track message timestamps for each user
        self.user_messages = defaultdict(deque)
        # Track burst messages for each user
        self.user_burst_count = defaultdict(int)
        # Track last burst time for each user
        self.user_last_burst = defaultdict(float)
        
        self.lock = threading.Lock()

        self.user_cooldown_until = defaultdict(lambda: 0.0)
    
    def is_allowed(self, user_id):
        """
        Check if a user is allowed to send a message.
        Returns (allowed: bool, reason: str, wait_time: float)
        """
        with self.lock:
            current_time = time.time()

            if self.user_cooldown_until[user_id] > current_time:
                remaining = self.user_cooldown_until[user_id] - current_time
                return False, f"You are in timeout for {remaining:.1f} more seconds", remaining
            
            # Clean old messages (older than 1 minute)
            user_msgs = self.user_messages[user_id]
            while user_msgs and current_time - user_msgs[0] > 60:
                user_msgs.popleft()
            
            # Check if user is in cooldown from burst limit
            last_burst = self.user_last_burst[user_id]
            if last_burst and current_time - last_burst < self.cooldown_seconds:
                remaining_cooldown = self.cooldown_seconds - (current_time - last_burst)
                return False, f"You are in cooldown for {remaining_cooldown:.1f} more seconds", remaining_cooldown
            
            # Check messages per minute limit
            if len(user_msgs) >= self.messages_per_minute:
                oldest_message_time = user_msgs[0]
                wait_time = 60 - (current_time - oldest_message_time)
                return False, f"Rate limit exceeded. Wait {wait_time:.1f} seconds", wait_time
            
            # Check burst limit (messages within last 10 seconds)
            recent_messages = sum(1 for msg_time in user_msgs if current_time - msg_time <= 10)
            if recent_messages >= self.burst_limit:
                self.user_last_burst[user_id] = current_time
                return False, f"Burst limit exceeded. You're in cooldown for {self.cooldown_seconds} seconds", self.cooldown_seconds
            
            # User is allowed to send message
            user_msgs.append(current_time)
            return True, "", 0
    
    def reset_user(self, user_id):
        """Reset rate limiting for a specific user (admin function)"""
        with self.lock:
            self.user_messages[user_id].clear()
            self.user_burst_count[user_id] = 0
            self.user_last_burst[user_id] = 0
    
    def get_user_status(self, user_id):
        """Get current rate limiting status for a user"""
        with self.lock:
            current_time = time.time()
            user_msgs = self.user_messages[user_id]
            
            # Clean old messages
            while user_msgs and current_time - user_msgs[0] > 60:
                user_msgs.popleft()
            
            recent_messages = sum(1 for msg_time in user_msgs if current_time - msg_time <= 10)
            last_burst = self.user_last_burst[user_id]
            cooldown_remaining = 0
            
            if last_burst and current_time - last_burst < self.cooldown_seconds:
                cooldown_remaining = self.cooldown_seconds - (current_time - last_burst)
            
            return {
                "messages_this_minute": len(user_msgs),
                "messages_per_minute_limit": self.messages_per_minute,
                "recent_messages": recent_messages,
                "burst_limit": self.burst_limit,
                "cooldown_remaining": cooldown_remaining
            }

    def set_user_timeout(self, user_id, timeout_seconds):
        """Ban user from sending messages for `timeout_seconds` starting now"""
        with self.lock:
            self.user_cooldown_until[user_id] = time.time() + timeout_seconds
            self.user_messages[user_id].clear()
        return True