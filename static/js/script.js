const header = document.querySelector('header');
const deleteForm = document.querySelector('#delete-form');
const dropdownContent = document.querySelector('#dropdown-content');
const dropdownButton = document.querySelector('#dropdown-button');
const background = document.querySelector('#background');
const profilePicInput = document.querySelector('#profile-pic');
const profilePic = document.querySelector('#profile-img');
const subscribeButton = document.querySelector('#subscribe-button');
const subscribeForm = document.querySelector('#subscribe-form');
const checkSub = document.querySelector('#subscribed');

// Confirm article deletion
function deleteArticleWarning() {
    var deleteWarning = confirm("Вы действительно хотите удалить статью?");

    if (deleteWarning === false) {
        deleteForm.removeAttribute('action');
    }
}

// Show dropdown
function showDropdownContent() {
  if (dropdownContent.style.display === 'flex') {
    dropdownContent.style.display = 'none';
  } else {
    dropdownContent.style.display = 'flex';
  }
}

function setPic() {
  profilePic.src = profilePicInput.value;
  console.log("Pic changed!");
  console.log(profilePicInput.value);
}

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
  dropdownContent.style.display = 'none';
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

function reloadPage() {
  setTimeout(() => {
    window.location.reload(true);
    console.log('reload');
  }, 1000); 
}

window.onload = () => {
  if (subscribed) {
    subscribeButton.value = 'Отписаться';
  } else {
    subscribeButton.value = 'Подписаться';
  }
}