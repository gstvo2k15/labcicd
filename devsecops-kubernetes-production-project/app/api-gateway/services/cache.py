import redis
from ..config import setttestinglab.coms
r = redis.from_url(setttestinglab.coms.redis_url, decode_responses=True)
