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

  e.target.classList.toggle('active');
};

document.querySelectorAll('.tab').forEach(el => {
  el.addEventListener('click', changeTab);
});
