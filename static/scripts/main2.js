
function errors(errors_field_id){
    if(errors_field_id.find('.errors').length > 0){
       
        $(errors_field_id).find('input').addClass('errors');

    }
}

$(document).ready(function(){
    //Desktop login form
    var username_errors = $('#username_field');
    var password_error   = $("#password_field");

    errors(username_errors);
    errors(password_error);

    //Mobile login form
    var mobile_user_errors = $("#mobile_username_field");
    var mobile_password_errors = $("#mobile_password_field");
    
    errors(mobile_user_errors);
    errors(mobile_password_errors);

    //Desktop signup form
    var signup_username_error = $("#signup_username_field");
    var signup_password_error = $("#signup_password_field");
    var signup_phone_error = $("#signup_phone_field");
    var code_error = $("#signup_code_field");
    errors(signup_username_error);
    errors(signup_password_error);
    errors(signup_phone_error);
    errors(code_error);
    

    //Mobile signup form
    var mobile_signup_user_errors = $("#mobile_signup_username_field");
    var mobile_signup_password_errors = $("#mobile_singup_password_field");

    errors(mobile_signup_user_errors);
    errors(mobile_signup_password_errors);

   
});