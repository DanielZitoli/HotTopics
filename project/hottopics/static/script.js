$(document).ready(function(){

    $("#sidebar").click(openSidebar);
    $("#sidebar").mouseenter(openSidebar);
    $("main").click(closeSidebar);
    $("#sidebar").mouseleave(closeSidebar);



    function openSidebar(){
        sidebarExpanded = true
        $("#sidebar").addClass('toggleSidebar') 
        $(".avoidtitle").addClass('toggleTitle')
        $(".add").addClass('toggleTitle')
        $("ul").addClass('toggleNav')
        $("#navlogo").addClass("toggleLogo")
    }
    function closeSidebar(){
        sidebarExpanded = false
        $("#sidebar").removeClass('toggleSidebar') 
        $(".avoidtitle").removeClass('toggleTitle')
        $(".add").removeClass('toggleTitle')
        $("ul").removeClass('toggleNav') 
        $("#navlogo").removeClass("toggleLogo")
    }

    //Logic for Sidebar Mobile Swipe

    body = document.querySelector("body")
    body.addEventListener("touchstart", touchStart)
    body.addEventListener("touchmove", touchMove)
    body.addEventListener("touchend", touchEnd)

    sidebar = document.querySelector("#sidebar")
    logo = document.querySelector("#navlogo")
    title = document.querySelector(".avoidtitle")
    add = document.querySelector(".add")

    sidebarExpanded = false
    startPos = 0
    currentPosition = 0
    currentSlide = 0


    function touchStart(event){
        startPos = getPositionX(event)
        animationID = requestAnimationFrame(animation)
        $("#sidebar-container *").css('transition', 'all 0s') // selects descendents of the sidebar and sets transition to none
    }

    function touchMove(event){
        currentPosition = getPositionX(event)
        currentSlide = currentPosition - startPos

        if (!sidebarExpanded){ 
            if (currentSlide < 0){
                startPos = currentPosition
            } 
        } else {
            if (currentSlide > 0){
                startPos = currentPosition
            }
        }
    }

    function touchEnd(event){
        cancelAnimationFrame(animationID)

        //resets sidebars transitions
        $("#sidebar-container *").css("transition", "")

        if (!sidebarExpanded){
            if (currentSlide > 100){
                openSidebar()
            } else {
                sidebar.style.width = "60px"
                logo.style.left = "0"
                title.style.opacity = "0"
                add.style.opacity = "0"
            }
        } else {
            if (currentSlide < -120){
                closeSidebar()
            } else {
                sidebar.style.width = "300px"
                logo.style.left = "62px"
                title.style.opacity = "1"
                add.style.opacity = "1"
            }
        }

        startPos = 0, currentSlide = 0, currentPosition = 0
    }

    function getPositionX(event){
        return event.touches[0].clientX
    }

    function animation(){
        setSidebarPosition()
        requestAnimationFrame(animation)
    }

    function setSidebarPosition(){
        shift = sidebarExpanded ? 240 + currentSlide : currentSlide
        sidebar.style.width = `max(${60 + shift}px, 60px)`
        logo.style.left = `min(${shift * 62/230}px, 62px)`
        title.style.opacity = `${(shift - 100)/140}`
        add.style.opacity = `${(shift - 100)/140}`

    }

});