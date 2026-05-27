from django.conf import settings
import hashlib
import os


def get_redis_cache_connection_string():
    redis_host = os.environ.get('REDIS_HOST', 'redis')
    redis_port = os.environ.get('REDIS_PORT', 6379)
    redis_password = os.environ.get('REDIS_PASSWORD', '')
    redis_cache_db = os.environ.get('CACHE_REDIS_DB', 0)
    if redis_password:
        return f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_cache_db}"
    return f"redis://{redis_host}:{redis_port}/{redis_cache_db}"


def get_hashed_url(url):
    hash_data = "\0".join((url, settings.SECRET_KEY)).encode('utf-8')
    hash_url = hashlib.sha1(hash_data).hexdigest()
    return '{}_{}/'.format(url, hash_url)
