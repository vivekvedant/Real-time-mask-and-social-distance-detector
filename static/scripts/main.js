$(document).ready(function(){
    $("#signupBtn").click(function(){
        // $("#main").animate({left:"22.5%"},400);
        $("#main").animate({left:"23%"},400);

       

        $("#signupform").animate({left:"74%"},400);
        $("#signupform").animate({left:"76%"},400);
        $("#signupform").css("visibility","visible");
        $("#signupmsg").css("visibility","hidden");
        // $("#loginform").css("visibility","hidden");
        $("#loginmsg").css("visibility","visible");
        $("#loginform").animate({left:"25%"},400);
    });

    $("#loginBtn").click(function(){
        $("#main").animate({left:"76%"},400);
        // $("#main").animate({left:"76%"},400);

        

        $("#loginform").animate({left:"20%"},400);
        $("#loginform").animate({left:"23%"},400);
        $("#loginform").css("visibility","visible");
        $("#loginmsg").css("visibility","hidden");
        // $("#signupform").css("visibility","hidden");
        $("#signupmsg").css("visibility","visible");
        $("#signupform").animate({left:"74%"},400);
    });

    $("#create-accountbtn").click(function(){
        $(".mobile-view-signup").css("visibility","visible");
        $(".mobile-view-login").css("visibility","hidden");

        
    });

    $("#loginbtn").click(function(){
        $(".mobile-view-signup").css("visibility","hidden");
        $(".mobile-view-login").css("visibility","visible");
    });
})