var animation = document.getElementsByClassName("animation");
window.onscroll = function() {
  for(let i=0; i<animation.length; i++){
    var topElm = animation[i].offsetTop;
    var btmElm = animation[i].offsetTop + animation[i].clientHeight;
    var top_screen = window.pageYOffset;
    var bottom_screen = window.pageYOffset + window.innerHeight;
    if ((bottom_screen > topElm) && (top_screen < btmElm)) {
        animation[i].classList.add("animation-opacity")
    } else {
        animation[i].classList.remove("animation-opacity")
    }
  }
};