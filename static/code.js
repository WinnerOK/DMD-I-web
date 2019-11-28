let activeTab = 1;

let isLoading = false;
let isLoadingData = false;
let progress = 0;
let interval = null;
const startLoad = (e) => {
  if (!isLoading) {
    if (!e || parseInt(e.target.getAttribute('data-tab')) !== 6) {
      isLoading = true;
      progress = 0;
      interval = setInterval(() => {
        if (progress >= 100) progress = 0;
        else progress += 10;
        document.getElementById('progress').style.width = progress + '%';
      }, 100);
    }
  }
};

const changeTab = (e) => {
  if (!isLoadingData) {
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
      clearInterval(interval);
      progress = 0;
      document.getElementById('progress').style.width = progress + '%';
    } else {
      changeRoute(activeTab);
      document.querySelector('.table-wrap').classList.remove('hidden');
    }
    e.target.classList.toggle('active');
  }

};

document.querySelectorAll('.tab').forEach(el => {
  el.addEventListener('mousedown', startLoad);
  el.addEventListener('click', changeTab);
});

document.querySelector('#exquery').addEventListener('click', () => {
  document.querySelector('#custom-select').innerHTML = 'select * from usr.users';
});

function changeRoute(name) {
  getData('/?id=' + name, 'GET');
}

document.querySelector('#execute').addEventListener('click', () => {
  startLoad();
  getData('/custom', 'POST', {
    query: document.querySelector('#custom-select').textContent,
  });
});

function getData(url, method, data, isWhole) {
  if (!isLoadingData) {
    isLoadingData = true;
    let xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
      if (this.readyState === 4 && this.status === 200) {
        let el = document.createElement('html');
        el.innerHTML = this.response;
        let table = isWhole ? el.lastChild : el.lastChild.querySelector('.table-wrap');

        if (table) {
          if (isWhole) document.querySelector('html')
            .replaceChild(table, document.querySelector('body'));
          else document.querySelector('body')
            .replaceChild(table, document.querySelector('.table-wrap'));
        }

        document.querySelector('.table-wrap').classList.remove('hidden');

        clearInterval(interval);
        progress = 0;
        isLoadingData = false;
        isLoading = false;
        document.getElementById('progress').style.width = progress + '%';
      }
    };
    xhr.send(JSON.stringify(data));
  }
}
