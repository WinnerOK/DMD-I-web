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
  field: 'paramedics_group',
}, {
  id: 'chats',
  field: 'chats',
}, {
  id: 'messages',
  field: 'chats_messages',
}, {
  id: 'board_messages',
  field: 'notice_board_messages',
}];

document.getElementById('execute').addEventListener('click', function () {
  let data = {};
  for (let obj of ids) data[obj.field] = document.getElementById(obj.id).value;
  data['execute_queries'] = document.getElementById('exe_queries').checked;
  data['truncate_tables'] = document.getElementById('trunc').checked;

  let xhr = new XMLHttpRequest();
  xhr.open('POST', '/populate', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onreadystatechange = function() {
    if (this.readyState === 4 && this.status === 200) {
      console.log(this.response);
    }
  };
  xhr.send(JSON.stringify(data));
});
