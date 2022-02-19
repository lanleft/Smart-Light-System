// //////////////////////////////////////////////
async function fetchLogin(username, password) {
    const response = await fetch(`/api/login/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({'username': username, 'password': password}),
      }).then(r =>  r.json().then(data => ({status: r.status, body: data})));
    return response;
    }
  
  async function getLogin(username, password){
    const res = await this.fetchLogin(username, password);
    return res;
  }
  //load user
  window.onload = function(e) {
    document.getElementById('login').onclick = function(e){
      var username = document.getElementById('username').value;
      var password = document.getElementById('password').value;
      getLogin(username, password).then(data => {
        var success = data.body.success;
        if (success != true){
          alert('user not exist');
        } else {
          var user_id = data.body.user_id;
          localStorage.setItem('user_id', user_id);
          window.location.href = '/home';
        }
      });
    }
  }
  
  //load query user 
  