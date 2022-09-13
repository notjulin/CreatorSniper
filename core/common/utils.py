import base64
import binascii
import json
import os
import os.path
import re
import urllib.parse

from core.classes.content import Content
from core.classes.exceptions import InvalidContent, InvalidData, InvalidImage, NotImplemented
from core.classes.http import RosHTTP
from core.classes.memory import Memory
from core.common.config import *
from flask import Flask, Response, cli, jsonify, request
from requests import get

app = Flask(__name__, static_folder=os.path.abspath(FLASK_FOLDER))

ros = RosHTTP()


def _eval_expr(expressions: str, *args) -> None:
    for expr in expressions.split():
        eval(expr, *args)


def _show_server_banner(*_) -> None:
    os.system("cls")
    print(BANNER)
    print(f" * Running on http://{FLASK_HOST}:{FLASK_PORT} (Press CTRL+C to quit)", end="\n\n")


def _scan_module() -> tuple[str]:
    memory = Memory("GTA5.exe")
    memory.pattern_scan(PATTERN)

    _eval_expr(EXPR_ACCT_TICKET, locals())

    acct_ticket = memory.read("string", 208)

    _eval_expr(EXPR_SESS_TICKET, locals())

    sess_ticket = memory.read("string", 88)

    _eval_expr(EXPR_SESS_KEY, locals())

    sess_key = base64.b64encode(memory.read("bytes", 16)).decode()

    return (acct_ticket, sess_ticket, sess_key)


def _get_data_len(data: dict[str] | bytes) -> bytes:
    image = isinstance(data, bytes)

    if not image:
        data = json.dumps(data)

    data_len = len(data)
    data_len = binascii.unhexlify(f"{data_len:x}" if len(f"{data_len:x}") % 2 == 0 else f"0{data_len:x}")

    match len(data_len):
        case 1:
            data_len = b"\x00\x00\x00" + data_len

        case 2:
            data_len = b"\x00\x00" + data_len

        case 3:
            data_len = b"\x00" + data_len

        case _:
            raise InvalidImage if image else InvalidData

    data_len += b"\x00\x00\x00"
    data_len += b"\x02" if image else b"\x00"

    return data_len


def run_server() -> None:
    cli.show_server_banner = _show_server_banner

    (ros.acct_ticket, ros.sess_ticket, ros.sess_key) = _scan_module()

    app.run(FLASK_HOST, FLASK_PORT, FLASK_DEBUG)


@app.errorhandler(Exception)
def app_handler(error: Exception) -> Response:
    return jsonify({"error": error.__class__.__name__})


@app.route("/", methods=["GET"])
def app_index() -> Response:
    return app.send_static_file("index.html")


@app.route("/data", methods=["POST"])
def app_data() -> Response:
    if "id" not in request.json:
        return Response(status=404)

    content = Content(request.json["id"])

    print(f" * [DATA] {content.id}")

    return jsonify(
        {
            "id": content.id,
            "name": content.name,
            "desc": content.desc,
            "tags": content.tags,
            "data": content.data,
            "lang": content.lang,
            "image": content.image,
        }
    )


@app.route("/delete", methods=["POST"])
def app_delete() -> Response:
    if "id" not in request.json:
        return Response(status=404)

    data = f"""contentType=gta5mission&contentId={request.json["id"]}&deleted=true""".encode()
    response = ros.post("http://ugc-gta5-prod.ros.rockstargames.com/gta5/11/gameservices/ugc.asmx/SetDeleted", data)

    if "<Status>1</Status>" in response:
        print(f""" * [DELETE] {request.json["id"]}""")

        return Response(status=200)
    return Response(status=404)


@app.route("/list", methods=["GET"])
def app_list() -> Response:
    contents = []
    offset = 0

    while True:
        data = f"contentType=gta5mission&queryName=GetMyContent&queryParams={{published:true}}&offset={offset}&count=31".encode()
        response = ros.post("http://ugc-gta5-prod.ros.rockstargames.com/gta5/11/gameservices/ugc.asmx/QueryContent", data)

        if "<Status>1</Status>" in response:
            for (content, name) in re.findall(r"r c=\"([\w-]{22})\">\r\n.+?<m a=\".+?\" cd=\".+?\" f1=\".+?\"(?:| n=\"(.+?)\") (?:l|pd)=\"", response):
                if not len(name):
                    name = "(empty)"

                image = ros.get(f"http://prod.ros.rockstargames.com/cloud/11/cloudservices/ugc/gta5mission/{content}/2_0.jpg")
                contents.append({"id": content, "image": base64.b64encode(image).decode(), "name": name})

            (count, total) = re.findall(r"<Result Count=\"(\d+)\" Total=\"(\d+)\"", response)[0]

            offset += int(count)

            if offset >= int(total) - 1:
                break
        else:
            break

    if len(contents):
        print(" * [LIST] %d contents" % len(contents))

        return jsonify({"contents": contents})
    return Response(status=404)


@app.route("/clone", methods=["POST"])
def app_clone() -> Response:
    match request.json:
        case {"id": id, "name": name, "desc": desc, "tags": tags, "data": data, "lang": lang, "image": image}:
            tags = tags.split(",") if "," in tags else [tags]
            tags = ",".join(list(set([tag for tag in tags if len(tag.strip())])))

            image = get(image, verify=False).content if image.startswith("https://") else base64.b64decode(image.split("base64,")[1])

            data_len = _get_data_len(data)
            image_len = _get_data_len(image)

            datajson = json.dumps(
                {
                    "meta": data["meta"],
                    "mission": data["mission"],
                    "version": 2,
                }
            ).replace("\"", "\\\"")

            template = b"contentType=gta5mission&paramsJson="

            template += urllib.parse.quote_plus(
                """{"ContentName":"%s","DataJson":"%s","Description":"%s","Publish":true,"Language":"%s","TagCsv":"%s"}"""
                % (
                    name,
                    datajson,
                    desc,
                    lang,
                    tags,
                )
            ).encode()

            template += b"&data=%b%b%b%b" % (
                data_len,
                json.dumps(data).encode(),
                image_len,
                image,
            )

            response = ros.post("http://ugc-gta5-prod.ros.rockstargames.com/gta5/11/gameservices/ugc.asmx/CreateContent", template)

            if "NotImplemented" in response:
                raise NotImplemented

            if "<Status>1</Status>" in response:
                new_id = response.split("<Result ci=\"")[1].split("\"")[0]

                print(f" * [CLONE] {id} -> {new_id}")

                return jsonify({"id": id, "new_id": new_id})
            raise InvalidContent
        case _:
            return Response(status=404)
