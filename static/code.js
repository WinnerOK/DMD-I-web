let activeTab = 1;

const changeTab = (e) => {
  document.querySelectorAll('.tab').forEach(el => {
    if (el.classList.contains('active')) {
      el.classList.toggle('active');
    }
  });

  activeTab = e.target.getAttribute('data-tab');
  document.querySelectorAll('.body-wrapper > section').forEach(el => {
    if (el.getAttribute('data-tab') === activeTab) {
      el.classList.add('active');
    } else {
      el.classList.remove('active');
    }
  });

  changeRoute(activeTab);
  e.target.classList.toggle('active');
};

document.querySelectorAll('.tab').forEach(el => {
  el.addEventListener('click', changeTab);
});

function changeRoute(name) {
  let url = '/?id=' + name,
      xhttp = new XMLHttpRequest();

  xhttp.onreadystatechange = function () {
    if (this.readyState === 4 && this.status === 200) {
      let el = document.createElement('html');
      el.innerHTML = this.response;
      let table = el.lastChild.querySelector('.table-wrap');

      if (table) document.querySelector('body')
        .replaceChild(table, document.querySelector('.table-wrap'));
    }
  };

  xhttp.open('GET', url, true);
  xhttp.send();
}
