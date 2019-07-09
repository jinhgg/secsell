
 $(document).ready(function() {

	var $form_modal = $('.cd-user-modal'),
		$form_login = $form_modal.find('#cd-login'),
		$form_signup = $form_modal.find('#cd-signup'),
		$form_forgot_password = $form_modal.find('#cd-reset-password'),
		$form_modal_tab = $('.cd-switcher'),
		$tab_login = $form_modal_tab.children('li').eq(0).children('a'),
		$tab_signup = $form_modal_tab.children('li').eq(1).children('a'),
		$forgot_password_link = $form_login.find('.cd-form-bottom-message a'),
		$back_to_login_link = $form_forgot_password.find('.cd-form-bottom-message a'),
        $main_nav = $('.R_login'),
        $login_nav = $('.ulogin'),
        $register_nav = $('.curegister');
	//open modal

    $register_nav.on('click', function(event){
            $form_modal.addClass('is-visible');
            signup_selected();
	});
    $('.ulogin').on('click', function(event){
		    $form_modal.addClass('is-visible');
            login_selected();
	});
    $('.tb-ms-login').on('click', function(event){
		    $form_modal.addClass('is-visible');
            login_selected();
	});

    $('.cd-switcher #login').on('click', function(event){
		    $form_modal.addClass('is-visible');
            login_selected();
	});
     $('.cd-switcher #signup').on('click', function(event){
		    $form_modal.addClass('is-visible');
            signup_selected();
	});
	//close modal
	$('.cd-user-modal').on('click', function(event){
		if( $(event.target).is($form_modal) || $(event.target).is('.cd-close-form') ) {
			$form_modal.removeClass('is-visible');
		}
	});
	//close modal when clicking the esc keyboard button
	$(document).keyup(function(event){
    	if(event.which=='27'){
    		$form_modal.removeClass('is-visible');
	    }
    });

     $('.close').on('click', function(event){
		   $form_modal.removeClass('is-visible');
	});

	//back to login from the forgot-password form
	$back_to_login_link.on('click', function(event){
		event.preventDefault();
		login_selected();
	});

	function login_selected(){
		$form_login.addClass('is-selected');
		$form_signup.removeClass('is-selected');
		$form_forgot_password.removeClass('is-selected');
		$tab_login.addClass('selected');
		$tab_signup.removeClass('selected');
	}

	function signup_selected(){
		$form_login.removeClass('is-selected');
		$form_signup.addClass('is-selected');
		$form_forgot_password.removeClass('is-selected');
		$tab_login.removeClass('selected');
		$tab_signup.addClass('selected');
	}

	function forgot_password_selected(){
		$form_login.removeClass('is-selected');
		$form_signup.removeClass('is-selected');
		$form_forgot_password.addClass('is-selected');
	}
     //验证手机 return /^1\d{10}$/.test(_keyword);
    function isPhoneNumber(_keyword) {
             return  /^1[3|4|5|7|8]\d{9}$/.test(_keyword);
    };
       //验证邮箱
    function isEmail(word) {
            return /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(word);
    };

     function signincheckinput() {
         var loginform = $('#login-form')
         var name=$('#login-form input[id="email"]').val();
         var pass=$('#login-form input[id="password"]').val()
         var phone=$('#login-form input[id="email"]').val();
         var checkcode=$('#login-form input[id="checkcode"]').val();
         var State = $("#signinState");
         var telPassword_error = $("#signin_telPassword_error");
         var signin_checkcode_error= $("#signin_checkcode_error");
          if(name==''|| !(isPhoneNumber(name) || isEmail(name))){
                  State.removeClass().addClass("inputerror").html("请输入正确的邮箱或手机号");
                 $('#email').focus();
                  return false;
           }else if(pass==''){
                  telPassword_error.removeClass().addClass("inputerror").html("请输入密码");
                 $('#password').focus();
                  return false;
           }else if(checkcode==''){
                  signin_checkcode_error.removeClass().addClass("inputerror").html("请输入验证码");
                 $('#checkcode').focus();
                  return false;
           }else{
                   return true;
           }
     }


   var post_flag = false;
     //登录  ajax提交
   $('#loginsubmit').click(function(){
         var email=$('#login-form input[id="email"]').val();
         var password=$('#login-form input[id="password"]').val();
         var remember =$('#login-form input[id="remember"]:checked').val();
         var checkcode=$('#login-form input[id="checkcode"]').val();
         var ErrorInfo = $("#ErrorInfo");
         // var csrftoken = $('#csrf_token').val();
         var csrftoken = $('meta[name=csrf-token]').attr('content')

         if(post_flag) return;
            //标记当前状态为正在提交状态
         post_flag = true;
         function csrfSafeMethod(method) {
                // these HTTP methods do not require CSRF protection
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
         }
// &&且 ||或
         $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
         });
         var var_data = {
                    "email": email,
                    "password": password,
                    "name": email,
                    "username": email,
                    "remember": remember,
                    "checkcode":checkcode,
         }
         var json_str = JSON.stringify(var_data);
         if (signincheckinput()) {
              $.ajax({
                        url: "/login",
                        type: "POST",
                        data: json_str,
                        cache: false,
                        async:false,
                        contentType: "application/json",
                        dataType: "json",
                        success: function (data) {
                            setTimeout(function(){
                                       }, 1000);
                           //   alert(data);
                            if (data.status == 200) {
                              //alert(data.redirect_url);
                               window.location.href = data.redirect_url+Math.random() ;
                               location.reload(true);
                               post_flag =false; //在提交成功之后将标志标记为可提交状态
                            }
                            else  {
                              // alert(data.msg);
                               login_selected();
                               ErrorInfo.removeClass().addClass("inputerror").html(data.msg);
                               $('#login-form input[id="email"]').focus();
                               post_flag =false; //在提交成功之后将标志标记为可提交状态
                               return false;
                            }
                        },
                        error:function(XMLHttpRequest, textStatus, errorThrown){
                          //  alert(data);
                         // alert(JSON.stringify(XMLHttpRequest) + "\n" + textStatus + "\n" + errorThrown);
                            alert(errorThrown);
                            post_flag =false; //在提交成功之后将标志标记为可提交状态
                         }
                })
               return false;
         }
   })
     //注册
   $('#regsubmit').click(function(){
         var regform = $('#register-form')
         var name=$('#register-form input[id="email"]').val();
         var passwd=$('#register-form input[id="password"]').val();
         var phone=$('#register-form input[id="email"]').val();
         var signupcheckcode=$('#register-form input[id="signupcheckcode"]').val();
         var regIdState = $("#regIdState");
         var reg_telPassword_error = $("#register_telPassword_error");
         var signup_checkcode_error = $("#signup_checkcode_error");
         var canRegister = false;
        // var csrftoken =$('#register-form input[name="csrfmiddlewaretoken"]').val();
         canRegister =$('#register-form input[id="accept-terms"]:checked').val();
         var csrftoken = $.cookie('csrftoken');
         $('#username').val(name);
         if (!(canRegister)){
             alert("请先同意XX协议");
             return false;
         }

         if(name==''|| !(isPhoneNumber(name) || isEmail(name))){
              regIdState.removeClass().addClass("inputerror").html("请输入正确的邮箱或手机号");
             $('#email').focus()
              return false;
         }else if(passwd==''){
                  reg_telPassword_error.removeClass().addClass("inputerror").html("请输入密码");
                 $('#password').focus()
                  return false;
         }else if ( passwd.length < 6 ) {
                  reg_telPassword_error.removeClass().addClass("inputerror").html("密码长度不能小于6位");
                   $('#password').focus()
                  return false;
          }else if(signupcheckcode==''){
                  signup_checkcode_error.removeClass().addClass("inputerror").html("请输入验证码");
                 $('#signupcheckcode').focus()
                  return false;
         }else{

             var var_data = {
                        "email": name,
                        "password": passwd,
                        "name": name,
                        "username": name,
                        "checkcode":signupcheckcode,
             }
            var json_str = JSON.stringify(var_data);
             $.ajax({
                        url: "/register",
                        type: "POST",
                        data: json_str,
                        cache: false,
                        async:false,
                        headers:{ "X-CSRFtoken":$.cookie("csrftoken")},
                        contentType: "application/json",
                        dataType: "json",
                        success: function (data) {
                           //   alert(data);
                            if (data.status == 200) {
                              //alert(data.redirect_url);
                              // window.location.href = data.redirect_url+Math.random() ;
                               window.location.href = data.redirect_url
                               location.reload(true);
                              //   $('.cd-user-modal').removeClass('is-visible');
                            }
                            else if (data.status == 401) {
                              // alert(data.msg);
                               signup_selected();
                               ErrorInfo.removeClass().addClass("inputerror").html(data.msg);
                               $('#register-form input[id="email"]').focus();
                               return false;
                            }
                        },
                        error:function(XMLHttpRequest, textStatus, errorThrown){
                            alert(errorThrown);
                         }
                })
               //$('register-form').submit();
         }

   })
    //重新取验证码图片

   $('#newPic').on('click', function(event){
		 $("#codePic").attr("src","/valicode?flag="+Math.random());
	});
   $('#signupnewPic').on('click', function(event){
		 $("#signupcodePic").attr("src","/valicode?flag="+Math.random());
	});


});

