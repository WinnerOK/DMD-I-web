let activeTab = 1;

const changeTab = (e) => {
  document.querySelectorAll('.tab').forEach(el => {
    if (el.classList.contains('active')) {
      el.classList.toggle('active');
    }
  });

  activeTab = e.target.getAttribute('data-tab');
  document.querySelectorAll('.body-wrapper > section').forEach(el => {
    if (el.getAttribute('data-tab') === activeTab)
      el.classList.add('active');
    else
      el.classList.remove('active');
  });

  if (parseInt(activeTab) === 6) {
    document.querySelector('.table-wrap').classList.add('hidden');
  } else {
    changeRoute(activeTab);
    document.querySelector('.table-wrap').classList.remove('hidden');
  }
  e.target.classList.toggle('active');
};

document.querySelectorAll('.tab').forEach(el => {
  el.addEventListener('click', changeTab);
});

function changeRoute(name) {
  getData('/?id=' + name, 'GET');
}

document.querySelector('#exquery').addEventListener('click', () => {
  document.querySelector('#custom-select').innerHTML = 'select * from usr.users';
});


document.querySelector('#execute').addEventListener('click', () => {
  getData('/custom', 'POST', {
    query: document.querySelector('#custom-select').textContent,
  });
});


function getData(url, method, data) {
  let xhr = new XMLHttpRequest();
  xhr.open(method, url, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onreadystatechange = function() {
    if (this.readyState === 4 && this.status === 200) {
      let el = document.createElement('html');
      el.innerHTML = this.response;
      let table = el.lastChild.querySelector('.table-wrap');

      if (table) document.querySelector('body')
        .replaceChild(table, document.querySelector('.table-wrap'));

      document.querySelector('.table-wrap').classList.remove('hidden');
    }
  };
  xhr.send(JSON.stringify(data));
}
