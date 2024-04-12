const menus = document.querySelector("nav ul");
const menusBtn = document.querySelector(".menu-btn");
const closeBtn = document.querySelector(".close-btn");

let closed=1

menusBtn.addEventListener("click", function () {
    if (closed==1){
        menus.classList.add("display");
        closed=0
    }
    else{
        menus.classList.remove("display");
        closed=1
    }

});

closeBtn.addEventListener("click", function () {
  menus.classList.remove("display");
  closed=1
});

function closer(){
    menus.classList.remove("display");
    closed=1
}

