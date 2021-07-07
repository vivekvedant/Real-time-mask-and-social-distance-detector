/*===== SHOW NAVBAR  =====*/ 
const showNavbar = (toggleId, navId, bodyId, headerId,videoId) =>{
    const toggle = document.getElementById(toggleId),
    nav = document.getElementById(navId),
    bodypd = document.getElementById(bodyId),
    headerpd = document.getElementById(headerId),
    videopd = document.getElementsByClassName(videoId)
    
    // Validate that all variables exist
    if(toggle && nav && bodypd && headerpd && videopd){
        toggle.addEventListener('click', ()=>{
            // show navbar
            nav.classList.toggle('show')
            // change icon
            toggle.classList.toggle('bx-x')
            // add padding to body
            bodypd.classList.toggle('body-pd')
            // add padding to header
            headerpd.classList.toggle('body-pd')


        })
    }
}

showNavbar('header-toggle','nav-bar','body-pd','header')


$(document).ready(function() {
    $('table').DataTable( {
      responsive: true
  } );
    
});

