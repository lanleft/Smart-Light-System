from pickle import FALSE, TRUE

from numpy import append
from flask import Flask, render_template, url_for, request, jsonify
import json
import datetime
import html
import requests 
import smtplib
from email.message import EmailMessage

app = Flask(__name__, static_url_path="/static")
lampDict = dict()
homes = [[] for _ in range(10)]
TIME_MAX = 6000
url_iots = []

"""
struct lamp:
{
    status="off",
    last_activated_time=0,
    prev_used_time=0,
    created_date=int(datetime.datetime.now().timestamp()),
}
home {
    user_id,
    username,
    password
}
"""
for i in range(10):
    tmp = "test"+str(i)
    homes[i] = ["SLS"+str(i), tmp, tmp]

@app.template_filter("from_timestamp")
def from_timestamp(timestamp, timeformat):
    return datetime.datetime.fromtimestamp(timestamp).strftime(timeformat)


@app.route("/", methods=["GET"])
def login_html():
    return render_template("login.html")
'''
@app.route("/", methods=["GET"])
def home():
    return render_template("index_1.html")
'''
@app.route("/api/login/", methods = ["POST"])
def login():
    form = request.get_json()
    username = form["username"]
    password = form["password"]
    for home in homes:
        if username==home[1] and password==home[2]:
            res = {
                "success":True,
                "user_id": home[0]
            }
            return jsonify(res)
    res = {
        "success": False,
        "msg": "username not exit"
    }
    return jsonify(res)

@app.route("/home", methods=["GET"])
def home():
    return render_template("index_1.html")

@app.route("/api/init", methods = ["POST"])
def setup():
    form = request.get_json()
    # global url_iot
    url_iot = "http://"+form["IP"]
    ok = TRUE
    for current in url_iots:
        if(current == url_iot) :
            ok = FALSE
    if(ok==TRUE): url_iots.append(url_iot)
    res = {"IP":form["IP"], "success":True}
    return jsonify(res)


@app.route("/api/lamp/add", methods=["POST"])
def add():
    # print(lampDict)   
    form = request.get_json()
    id = html.escape(form['id'])
    type_value = form['type']
    address_value = form['address']
    user_id = form['user_id']
    if id not in lampDict:
        lampDict[id] = dict(
            status="off",
            last_activated_time=0,
            prev_used_time=0,
            created_date=int(datetime.datetime.now().timestamp()),
            type=type_value,
            address=address_value,
            user_id=user_id
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
        msg = f"Alert: Your house is on fire!"
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
            try:
                x = requests.post(url_iot+"/api/config/lamp", json=lampChange, timeout=2.0) # --> if have iot url
                print(x)
            except requests.Timeout:
                print("Connection to "+url_iot+" timed out!")
                pass
            except requests.ConnectionError:
                print("Connection error!")
                pass
    else:
        lampDict[id]["status"] = "off"
        lampDict[id]["prev_used_time"] += (
            int(datetime.datetime.now().timestamp())
            - lampDict[id]["last_activated_time"]
        )
        lampDict[id]["last_activated_time"] = 0
        lampChange = {"id": id, "status" : "off"}
        for url_iot in url_iots:
            try:
                x = requests.post(url_iot+"/api/config/lamp", json=lampChange, timeout=2.0) # --> if have iot url
                print(x)
            except requests.Timeout:
                print("Connection to "+url_iot+" timed out!")
                pass
            except requests.ConnectionError:
                print("Connection error!")
                pass
    
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
        "prev_used_time": lampDict[id]["prev_used_time"]
    }
    return jsonify(res)


@app.route("/api/lamp/all", methods=["POST"])
def info_all():
    form = request.get_json()
    user_id = form["user_id"]
    res = []
    for key in lampDict:
        item = lampDict[key]
        item.update({"id": key})
        if item["user_id"]==user_id:
            res.append(item)
    # print (res)
    return jsonify(res)

@app.route("/api/lamp/delete", methods=["POST"])
def delete_lamp():
    form = request.get_json()
    id = str(form["id"])
    # print (form)
    # print(lampDict)
    if id not in lampDict:
        res = {
            "success": False,
            "msg": "id not exist"
        }
        # print (res)
        return jsonify(res)
    # item = lampDict[id]
    del lampDict[id]
    res = {
        "success": True,
        "msg": f"delete {id} success"
    }
    # print (res)
    return jsonify(res)

@app.route("/api/lamp", methods=["POST"])
def iot_change():
    
    form = request.get_json()
    # print (form)

    id, new_status = form["id"], form["status"]
    print(id)
    print(new_status)
    if id not in lampDict:
        lampDict[id] = dict(
            status="off",
            last_activated_time=0,
            prev_used_time=0,
            created_date=int(datetime.datetime.now().timestamp()),
            type="",
            address=""
        )
        lampDict[id]["status"] = new_status
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

