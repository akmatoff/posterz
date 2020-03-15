const deleteForm = document.querySelector('#delete-form');
const dropdownContent = document.querySelector('#dropdown-content');
const dropdownButton = document.querySelector('#dropdown-button');
const background = document.querySelector('#background');
const profilePicInput = document.querySelector('#profile-pic');
const profilePic = document.querySelector('#profile-img');

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

