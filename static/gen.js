const ids = [{
  id: 'users',
  field: 'users'
}, {
  id: 'hr',
  field: 'hr'
}, {
  id: 'doctors',
  field: 'doctors'
}, {
  id: 'recept',
  field: 'receptionists'
}, {
  id: 'lab_tech',
  field: 'lab_technicians',
}, {
  id: 'inventory',
  field: 'inventory_managers',
}, {
  id: 'admin',
  field: 'admin',
}, {
  id: 'nurses',
  field: 'nurses',
}, {
  id: 'paramedics',
  field: 'paramedics',
}, {
  id: 'patients',
  field: 'patients',
}, {
  id: 'pharma',
  field: 'pharmacists',
}, {
  id: 'par_groups',
  field: 'paramedics_groups',
}, {
  id: 'chats',
  field: 'chats',
}, {
  id: 'messages',
  field: 'chat_messages',
}, {
  id: 'board_messages',
  field: 'notice_board_messages',
}];

let interval = null;
let progress = 0;
const startLoad = (e) => {
  if (!e || parseInt(e.target.getAttribute('data-tab')) !== 6) {
    progress = 0;
    document.getElementById('execute').disabled = true;
    let up = true;
    interval = setInterval(() => {
      if (up) {
        if (progress >= 100) up = false;
        else progress += 10;
      } else {
        if (progress <= 0) up = true;
        else progress -= 10;
      }
      document.getElementById('progress').style.width = progress + '%';
    }, 100);
  }
};

document.getElementById('execute').addEventListener('click', startLoad);
document.getElementById('execute').addEventListener('click', function () {
  let data = {};
  for (let obj of ids) data[obj.field] = parseInt(document.getElementById(obj.id).value);
  data['execute_queries'] = document.getElementById('exe_queries').checked;
  data['truncate_tables'] = document.getElementById('trunc').checked;

  console.log('kek');
  let xhr = new XMLHttpRequest();
  xhr.open('POST', '/populate', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onreadystatechange = function() {
    if (this.readyState === 4 && this.status === 200) {
      window.location.href = this.response;
      clearInterval(interval);
      progress = 0;
      document.getElementById('progress').style.width = progress + '%';
    }
  };
  xhr.send(JSON.stringify(data));
});

