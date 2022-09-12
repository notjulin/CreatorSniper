from core.classes.exceptions import InvalidContent
from requests import get


class Content:
    id: str
    image: str
    name: str
    desc: str
    tags: list[str]
    data: dict[str]
    lang: str

    def __init__(self, id: str) -> None:
        self.id = id

        self._query_content()
        self._query_content_data()

    def _query_content(self) -> None:
        response = get(
            f"https://scapi.rockstargames.com/ugc/mission/details?title=gtav&contentId={self.id}",
            headers={
                "x-requested-with": "XMLHttpRequest",
                "x-lang": "en-US",
                "x-cache-ver": "0",
                "x-amc": "true",
            },
            verify=False,
        )

        if response.status_code != 200:
            raise InvalidContent

        match response.json():
            case {"content": {"imgSrc": image, "name": name, "desc": desc, "userTags": tags}}:
                self.image = image
                self.name = name
                self.desc = desc
                self.tags = tags

    def _query_content_data(self) -> None:
        langs = ["en", "fr", "de", "it", "es", "pt", "pl", "ru", "es-mx"]

        for lang in langs:
            response = get(f"""http://prod.cloud.rockstargames.com/ugc/gta5mission/{self.image.split("/")[5]}/{self.id}/0_0_{lang}.json""", verify=False)

            if response.status_code == 200:
                self.data = response.json()
                self.lang = lang
                return
        raise InvalidContent
