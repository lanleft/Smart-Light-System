$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

function lampItemTmpl(cnt, data) {
    res = $(`
        <tr id="lamp-row-${cnt}">
        <td>${cnt}</td>               
        <td>${data.id}</td>
        <td>${data.type}</td>
        <td>${data.address}</td>
        <td>${moment.unix(data.created_date).format('LLLL')}</td>
        <td>0</td>
        <td>${moment.utc(data.prev_used_time * 1000).format("HH:mm:ss")}</td>
        <td>
            <div class="form-check-md form-switch form-switch-md">
                <input class="form-check-input lamp-switch" type="checkbox" id="status" 
                    ${data.status == "on" ? "checked" : ""}>
            </div>
        </td>
        <td style="display:none;">${data.last_activated_time}</td>
        <td>
            <a class="edit" title="Edit" data-toggle="tooltip" onclick=reqChangeAddress(\"${data.id}\")><i class="material-icons">&#xE254;</i></a>
            <a class="delete" title="Delete" data-toggle="tooltip" onclick=reqDelete(\"${data.id}\")><i class="material-icons">&#xE872;</i></a>
        </td>
        </tr>
    `).trigger("create");
    return res;
}

function updateUpTime() {
    $('tr[id^="lamp-row-"]').each(function () {
        var id = $(this).attr('id');
        var upTimeCol = $(this).find("td:nth-child(4)");
        var isUp = $(this).find("td:nth-child(6) .lamp-switch").is(':checked');
        var lastActivatedTime = $(this).find("td:nth-child(7)").text();
        if (isUp)
            upTimeCol.html(moment.unix(lastActivatedTime).toNow());
    })
}

function reqDelete(id) {
    $.ajax({
        type: 'POST',
        url: `/api/lamp/delete`,
        contentType: 'application/json',
        data: JSON.stringify({
            'id': id
        }),
        dataType: "json",
        success: function (data) {
            if (data != null) {
                if (data.success) {
                    reqUpdateLampTable();
                }
            } else {}
        }
    });
}

function reqUpdateLampTable() {
    var user_id = localStorage.getItem('user_id')
    $.ajax({
        type: 'POST',
        url: `/api/lamp/all`,
        contentType: 'application/json',
        data: JSON.stringify({
            'user_id': user_id
        }),
        dataType: "json",
        success: function (data) {
            if (data != null) {
                $('#lamp-table > tbody').empty();
                for (let i = 0; i < data.length; i++) {
                    lampItemTmpl(i + 1, data[i]).appendTo($('#lamp-table > tbody'));
                }
                $(".lamp-switch").on("change", function () {
                    handleLampSwitch(this);
                });
                updateUpTime();
            } else {}
        }
    });
}

function reqAddLamp() {
    ///var id = (Math.random() + 1).toString(36).substring(4);
    document.getElementById("dialog-id").setAttribute("placeholder", "1234");
    
    let dialog = document.getElementById("Dialog");

    dialog.style.display = "block";
}

function reqChangeAddress(id) {
    let dialog = document.getElementById("Dialog");
    dialog.style.display = "block";
    console.log(id);
    ///console.log("id: " + id)
    ///var id = (Math.random() + 1).toString(36).substring(4);
    console.log(document.getElementById("dialog-id"));
    document.getElementById("dialog-id").value=id
    // document.getElementById("dialog-type").setAttribute("value", type);
    // document.getElementById("dialog-address").setAttribute("value", address);
    // document.getElementById("dialog-id").innerHTML=id;

    
}

function reqChangeLamp(id, new_status) {
    var user_id = localStorage.getItem('user_id')
    $.ajax({
        type: 'PUT',
        url: `/api/lamp/change`,
        contentType: 'application/json',
        data: JSON.stringify({
            'id': id,
            'new_status': new_status,
            'user_id': user_id
        }),
        dataType: "json",
        success: function (data) {
            if (data != null) {
                if (data.success) {
                    reqUpdateLampTable();
                }
            } else {}
        }
    });
}

function handleLampSwitch(switchObj) {
    var status = $(switchObj).is(':checked');
    var id = $(switchObj).closest('tr').find("td:nth-child(2)").text();
    reqChangeLamp(id, status ? "on" : "off");
}

const dialogCancel = (event) => {
    let dialog = document.getElementById("Dialog");
    dialog.style.display = "none";
}
const dialogSubmit = (event) => {
    let dialog = document.getElementById("Dialog");
    let input = document.getElementById("dialog-id");
    let id = input.value;
    let type = document.getElementById("dialog-type").value;
    let address = document.getElementById("dialog-address").value;
    var user_id = localStorage.getItem("user_id");
    $.ajax({
        type: 'POST',
        url: `/api/lamp/add`,
        data: JSON.stringify({
            'id': id,
            'type': type,
            'address': address,
            'user_id': user_id
        }),
        contentType: 'application/json',
        dataType: "json",
        success: function (data) {
            if (data != null) {
                if (data.success) {
                    reqUpdateLampTable();
                }
            } else {}
        }
    });
    input.value = "";
    dialog.style.display = "none";
}
document.getElementById("dialog-submit").addEventListener('click', dialogSubmit);
document.getElementById("dialog-cancel").addEventListener('click', dialogCancel);
reqUpdateLampTable();


$(document).ready(function () {
    setInterval(reqUpdateLampTable, 1000);
    setInterval(updateUpTime, 1000);

    // get modal dialog
    var modal = document.getElementById('Dialog');

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function (event) 
    {
        if (event.target == modal) {

            modal.style.display = "none";
        }
    }

});