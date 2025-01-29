import random
from typing import Dict
import time
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.messages_by_user: Dict[str, object] = {}

    def _cleanup_window(self, user_id: str, current_time: float):
        self.messages_by_user[user_id] = deque(maxlen=self.max_requests)
        self.messages_by_user[user_id].append(current_time)

    def can_send_message(self, user_id: str) -> bool:
        if self.messages_by_user.get(user_id) is None:
            return True

        first_message_time = self.messages_by_user.get(user_id).popleft()
        current_time_send = time.time()
        if current_time_send - first_message_time >= self.window_size:
            self._cleanup_window(user_id, current_time_send)
            return True
        else:
            self.messages_by_user.get(user_id).appendleft(first_message_time)
            if len(self.messages_by_user.get(user_id)) < self.max_requests:
                return True

        return False

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            if self.messages_by_user.get(user_id) is None:
                self.messages_by_user[user_id] = deque(maxlen=self.max_requests)
            self.messages_by_user[user_id].append(time.time())
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        if self.messages_by_user.get(user_id) is not None:
            first_message_time = self.messages_by_user.get(user_id).popleft()
            if current_time - first_message_time <= self.window_size:
                self.messages_by_user.get(user_id).appendleft(first_message_time)
                return self.window_size - (current_time - first_message_time)

        return 0


# function for rate limiter testing
def test_rate_limiter():
    # create rate limiter: 10sec sliding window, 1 message per user
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # simulate message flow (concurrent ID from 1 to 20 )
    print("\n=== Message flow simulation (Sliding Window) ===")
    for message_id in range(1, 11):
        # simulate different users (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Message {message_id:2d} | User {user_id} | "
            f"{'✓' if result else f'× (waiting time {wait_time:.1f}с)'}"
        )

        # random delay from 0.1 to 1 sec between messages
        time.sleep(random.uniform(0.1, 1.0))

    # waiting for window to clear
    print("\n waiting 4 seconds...")
    time.sleep(4)

    print("\n=== New set of messages after waiting ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(
            f"Message {message_id:2d} | User {user_id} | "
            f"{'✓' if result else f'× (waiting time {wait_time:.1f}с)'}"
        )
        # random delay from 0.1 to 1 sec between messages
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
