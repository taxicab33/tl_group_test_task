import redis


class RedisContextManager:
    def __enter__(self):
        self.redis_client = redis.StrictRedis(
            host='redis',
            decode_responses=True
        )
        return self.redis_client

    def __exit__(self, exc_type, exc_value, traceback):
        # Закрытие соединения с Redis в конце блока with
        self.redis_client.close()
