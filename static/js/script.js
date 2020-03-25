const header = document.querySelector('header');
const deleteForm = document.querySelector('#delete-form');
const sidebar = document.querySelector('#sidebar');
const sidebarButton = document.querySelector('#sidebar-button');
const sidebarCloser = document.querySelector('#sidebar-closer');
const background = document.querySelector('#background');
const profilePicInput = document.querySelector('#profile-pic');
const profilePic = document.querySelector('#profile-img');
const subscribeButton = document.querySelector('#subscribe-button');
const subscribeForm = document.querySelector('#subscribe-form');
const checkSub = document.querySelector('#subscribed');
const searchBar = document.querySelector('#search-bar');

// Confirm article deletion
function deleteArticleWarning() {
    var deleteWarning = confirm("Вы действительно хотите удалить статью?");

    if (deleteWarning) {
      deleteForm.submit();
    }
}

// Open sidebar
function showSidebar() {
  sidebar.style.width = '60%';
  sidebarCloser.style.display = 'block';
  searchBar.style.display = 'none';
}

function closeSidebar() {
  sidebar.style.width = '0';
  sidebarCloser.style.display = 'none';
  searchBar.style.display = 'block';
}

sidebarCloser.addEventListener('click', closeSidebar);

// Hide header on scroll
var scrollPos = window.pageYOffset;
window.onscroll = () => {
  var currentScrollPos = window.pageYOffset;
  if (scrollPos > currentScrollPos) {
    header.style.top = "0";
  } else {
    header.style.top = "-150px";
  }
  scrollPos = currentScrollPos;
}

var subscribed;

if (checkSub.innerHTML === '1') {
  subscribed = true;
} else {
  subscribed = false;
}

function followOrUnfollow() {
  if (subscribed) {
    subscribed = false;
  } else {
    subscribed = true;
  }
  subscribeForm.submit();
}

// Change button text, submit form, reload page on click
subscribeButton.addEventListener('click', function(){
  followOrUnfollow();
  setTimeout(function(){window.location.reload(true);},30)
});

window.onload = () => {
  if (subscribed) {
    subscribeButton.innerHTML = 'Отписаться';
  } else {
    subscribeButton.innerHTML = 'Подписаться';
  }
}
