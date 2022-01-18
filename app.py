from flask import Flask, render_template, url_for, request, jsonify
import json
import datetime
import html
import requests 
import smtplib
from email.message import EmailMessage

app = Flask(__name__, static_url_path="/static")
lampDict = dict()
TIME_MAX = 6000
url_iots = ["http://192.168.1.48"]

"""
struct lamp:
{
    status="off",
    last_activated_time=0,
    prev_used_time=0,
    created_date=int(datetime.datetime.now().timestamp()),
}
"""


@app.template_filter("from_timestamp")
def from_timestamp(timestamp, timeformat):
    return datetime.datetime.fromtimestamp(timestamp).strftime(timeformat)


@app.route("/", methods=["GET"])
def home():
    return render_template("index_1.html")

@app.route("/api/init", methods = ["POST"])
def setup():
    form = request.get_json()
    # global url_iot
    url_iot = "http://"+form["IP"]
    url_iots.append(url_iot)
    res = {"IP":form["IP"], "success":True}
    return jsonify(res)


@app.route("/api/lamp/add", methods=["POST"])
def add():
    # print(lampDict)   
    form = request.get_json()
    id = html.escape(form['id'])
    type_value = form['type']
    address_value = form['address']
    if id not in lampDict:
        lampDict[id] = dict(
            status="off",
            last_activated_time=0,
            prev_used_time=0,
            created_date=int(datetime.datetime.now().timestamp()),
            type=type_value,
            address=address_value
        )
        res = {"success": True}
        res.update(lampDict[id])
    else:
        lampDict[id]['type'] = type_value
        lampDict[id]['address'] = address_value
        res = {"success": True, "msg": "id existed, update type and address"}
        res.update(lampDict[id])
    return jsonify(res)

@app.route("/api/alert", methods=["POST"])
def FireAlert():
    form = request.get_json()
    typeSensor = form["type"]
    id = form['id']
    alertMsg = form['alert']

    if alertMsg=="True":
        msg = f"Dear lil chủ nhà,\nALO CHÁY NHÀ MÀY ƠI, CHÁY NHÀ KÌA!!!  \n\nP/S:Thêm nữa đừng reply email này, vì không ai giúp mày đâu...\n\nPeace!!!\nFrom: Hệ thống đèn yêu quý của mày."
        res_mail = SendMail("kubin2712@gmail.com", "Fire Alert", msg)
        res = {"success": res_mail}
    else:
        res = {"success": False}
    return jsonify(res)

def SendMail(to_email, subject, message):

    # import smtplib
    from_email="anna6553765537@gmail.com"

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content(message)
    server='smtp.gmail.com'
    print(msg)
    server = smtplib.SMTP(server, 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(from_email, "12345678@Abc")  # user & password
    try:
        server.send_message(msg)
        server.quit()
        # print('successfully sent the mail.')
        return True
    except:
        return False


@app.route("/api/lamp/change", methods=["PUT"])  # iot --> change led
def change():
    form = request.get_json()
    # global url_iot

    # if(url_iot == "test"):
    #     res = {"success": False, "msg": "URL does not exist"}
    #     return jsonify(res)

    id, new_status = form["id"], form["new_status"]
    if id not in lampDict:
        res = {"success": False, "msg": "id not exist"}
        return jsonify(res)

    if not new_status or new_status not in ["on", "off"]:
        res = {"success": False, "msg": "unknown status"}
        return jsonify(res)
    if new_status == lampDict[id]["status"]:
        res = {"success": False, "msg": f"already {new_status}"}
        return jsonify(res)

    if new_status == "on":
        lampDict[id]["status"] = "on"
        lampDict[id]["last_activated_time"] = int(datetime.datetime.now().timestamp())
        lampChange = {"id": id, "status" : "on"}
        for url_iot in url_iots:
            x = requests.post(url_iot+"/api/config/lamp", json=lampChange) # --> if have iot url
            print(x)
    else:
        lampDict[id]["status"] = "off"
        lampDict[id]["prev_used_time"] += (
            int(datetime.datetime.now().timestamp())
            - lampDict[id]["last_activated_time"]
        )
        lampDict[id]["last_activated_time"] = 0
        lampChange = {"id": id, "status" : "off"}
        for url_iot in url_iots:
            x = requests.post(url_iot+"/api/config/lamp", json=lampChange)   # --> if have iot url 
            print(x)
    res = {
        "URL" : url_iots,
        "success": True,
        "status": lampDict[id]["status"],
        "last_activated_time": lampDict[id]["last_activated_time"],
        "prev_used_time": lampDict[id]["prev_used_time"],
    }
    return jsonify(res)


@app.route(
    "/api/lamp/info/<string:id>", methods=["GET"]
)  # iot -> get info led  -> http://abc/lamp/info/
def info(id):
    # print (id)
    if id not in lampDict:
        res = {"success": False, "msg": "id not exist"}
        return jsonify(res)
    res = {
        "success": True,
        "status": lampDict[id]["status"],
        "last_activated_time": lampDict[id]["last_activated_time"],
        "prev_used_time": lampDict[id]["prev_used_time"],
    }
    return jsonify(res)


@app.route("/api/lamp/all", methods=["GET"])
def info_all():
    res = []
    for key in lampDict:
        item = lampDict[key]
        item.update({"id": key})
        res.append(item)
    return jsonify(res)

@app.route("/api/lamp", methods=["POST"])
def iot_change():
    # print ("testt")
    form = request.get_json()
    # print (form)

    id, new_status = form["id"], form["status"]
    if id not in lampDict:
        lampDict[id] = dict(
            status="off",
            last_activated_time=0,
            prev_used_time=0,
            created_date=int(datetime.datetime.now().timestamp()),
            type="",
            address=""
        )
        lampDict[id]["status"] = "on"
        lampDict[id]["last_activated_time"] = int(datetime.datetime.now().timestamp())
        lampChange = {"id": id, "status" : "on"}
        res = {
            "success": True,
            "status": lampDict[id]["status"],
            "last_activated_time": lampDict[id]["last_activated_time"],
            "prev_used_time": lampDict[id]["prev_used_time"],
        }
        res.update(lampDict[id])
        return jsonify(res)

    if not new_status or new_status not in ["on", "off"]:
        res = {"success": False, "msg": "unknown status"}
        return jsonify(res)
    if new_status == lampDict[id]["status"]:
        res = {"success": False, "msg": f"already {new_status}"}
        return jsonify(res)

    if new_status == "on":
        lampDict[id]["status"] = "on"
        lampDict[id]["last_activated_time"] = int(datetime.datetime.now().timestamp())
        lampChange = {"id": id, "status" : "on"}
    
    else:
        lampDict[id]["status"] = "off"
        lampDict[id]["prev_used_time"] += (
            int(datetime.datetime.now().timestamp())
            - lampDict[id]["last_activated_time"]
        )
        lampDict[id]["last_activated_time"] = 0
        lampChange = {"id": id, "status" : "off"}

    res = {
        "success": True,
        "status": lampDict[id]["status"],
        "last_activated_time": lampDict[id]["last_activated_time"],
        "prev_used_time": lampDict[id]["prev_used_time"],
    }
    return jsonify(res)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

