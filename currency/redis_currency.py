from django.core.cache.backends import redis

import redis

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Пример команды
r.set('foo', 'bar')
print(r.get('foo'))
