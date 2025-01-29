import time
from typing import Dict
import random
from collections import deque


class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        self.last_message_time_by_user: Dict[str, object] = {}

    def can_send_message(self, user_id: str) -> bool:
        last_message_time = self.last_message_time_by_user.get(user_id)

        if (
            last_message_time is None
            or time.time() - last_message_time >= self.min_interval
        ):
            return True
        return False

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            self.last_message_time_by_user[user_id] = time.time()
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        last_message_time = self.last_message_time_by_user.get(user_id)

        if (
            last_message_time is not None
            and current_time - last_message_time <= self.min_interval
        ):
            return self.min_interval - (current_time - last_message_time)
        return 0


def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\n=== Message flow simulation  (Throttling) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Message {message_id:2d} | User {user_id} | "
            f"{'✓' if result else f'× (waiting time {wait_time:.1f}с)'}"
        )

        # random delay from 0.1 to 1 sec between messages
        time.sleep(random.uniform(0.1, 1.0))

    print("\n waiting 4 seconds ..")
    time.sleep(4)

    print("\n=== New set of messages after waiting  ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(
            f"Message {message_id:2d} | User {user_id} | "
            f"{'✓' if result else f'× (waiting time {wait_time:.1f}с)'}"
        )
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_throttling_limiter()
