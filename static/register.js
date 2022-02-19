async function fetchRegister(username, password) {
  const response = await fetch(`/api/register/`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      'username': username,
      'password': password,
    }),
  }).then(r => r.json().then(data => ({
    status: r.status,
    body: data
  })));
  return response;
}

async function getRegister(username, password) {
  const res = await this.fetchRegister(username, password);
  return res;
}

window.onload = function (e) {
  document.getElementById('register').onclick = function (e) {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    var confirm_password = document.getElementById('confirm_password').value;
    // validate de sau
    if (password != "" && password == confirm_password) {
      getRegister(username, password).then(data => {
        var success = data.body.success;
        if (success != true){
          alert('user existed');
        } else {
          var user_id = data.body.user_id;
          localStorage.setItem('user_id', user_id);
          window.location.href = '/home';
          // alert(data.body.token);
        }
      });
    } else {
      alert("fail!");
    }
  }
}