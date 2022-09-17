from core.classes.exceptions import InvalidContentError
from requests import get


class Content:
    def __init__(self, id: str) -> None:
        self.id = id

        self._query_content()
        self._query_content_data()

    def _query_content(self) -> None:
        response = get(
            f'https://scapi.rockstargames.com/ugc/mission/details?title=gtav&contentId={self.id}',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'x-lang': 'en-US',
                'x-cache-ver': '0',
                'x-amc': 'true',
            },
            verify=False,
        )

        if response.status_code != 200:
            raise InvalidContentError

        content = response.json()['content']

        self.name = content['name'] if 'name' in content else ''
        self.desc = content['desc'] if 'desc' in content else ''
        self.type = content['type'] if 'type' in content else ''
        self.tags = content['userTags'] if 'userTags' in content else []
        self.image = content['imgSrc'] if 'imgSrc' in content else ''

    def _query_content_data(self) -> None:
        if not len(self.image):
            raise InvalidContentError

        langs = ['en', 'fr', 'de', 'it', 'es', 'pt', 'pl', 'ru', 'es-mx']
        prefixes = []

        for i in range(3):
            for j in range(3):
                prefixes.append(f'{i}_{j}')

        for prefix in prefixes:
            for lang in langs:
                response = get(f'''http://prod.cloud.rockstargames.com/ugc/gta5mission/{self.image.split('/')[5]}/{self.id}/{prefix}_{lang}.json''', verify=False)

                if response.status_code == 200:
                    self.data = response.json()
                    self.lang = lang
                    return
        raise InvalidContentError
