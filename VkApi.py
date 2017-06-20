import requests


class VkApi:

    APIKEY = '535750d5535750d5535750d568530b820c55357535750d50a1ed9fe025b6e1c8eacbbd2'
    APIVER = '5.63'
    APIURI = 'https://api.vk.com/method'
    POSTS_MAXPART = 100

    def _build_query(self, method, **kwargs):
        query = "%s/%s?v=%s&access_token=%s" % (self.APIURI, method, self.APIVER, self.APIKEY)
        for key in kwargs:
            query += "&%s=%s" % (key, str(kwargs[key]))
        return query

    def _get_json(self, method, **kwargs):
        return requests.get(self._build_query(method, **kwargs)).json()

    def get_posts(self, domain, count=-1):
        r = self._get_json('wall.get', domain=domain, offset=0, count=1)
        if count == -1 or count > r['response']['count']:
            count = r['response']['count']
        offset = 0
        posts = list()

        while offset < count:
            need2read = count - offset
            if need2read > self.POSTS_MAXPART:
                need2read = self.POSTS_MAXPART
            posts.append(
                self._get_json('wall.get', domain=domain, offset=offset, count=need2read)
            )
            offset += need2read
        return posts
