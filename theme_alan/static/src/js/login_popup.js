odoo.define("theme_alan.login_pop_js", function (require) {
"use strict";

var publicWidget = require("web.public.widget");

publicWidget.registry.loginpop = publicWidget.Widget.extend({
    "selector": "#wrapwrap",
    "events":{
        "click .loginpop":"_openPopAndRenderTemp",
        "click .loginbtn":"_checkAuthentication",
        "click .haveAccount":"_backToLogin",
        "click .signupbtn":"_userSignup",
        "click .resetbtn":"_resetFormTemp",
        "click .resetbtnconf":"_resetPassword"
    },
    _resetPassword:function(ev){
        if($("#loginr").val().trim() != ""){
            ev.preventDefault();
            return this._rpc({
                route: "/json/web/reset_password",
                params: {
                        "login":$("#loginr").val(),
                    }
            }).then(function (result) {
                if("error" in result){
                    $("#errorr").css("display","block").empty().append(result["error"]);
                }
                else if ("message" in result){
                    $("#reset_form").css("display","none");
                    $("#msgbox").css("display","block");
                    $("#messager").empty().append(result["message"]);
                }
            });
        }
    },
    _resetFormTemp:function(){
        $("#nav-reset-tab").click();
    },
    _userSignup:function(ev){
        if($("#logins").val().trim() != "" && $("#passwords").val().trim() != ""
            && $("#confirm_passwords").val().trim() != "" && $("#names").val().trim() != ""){
            ev.preventDefault();
            return this._rpc({
                route: "/json/signup/",
                params: {
                        "login":$("#logins").val(),
                        "name":$("#names").val(),
                        "password":$("#passwords").val(),
                        "confirm_password":$("#confirm_passwords").val(),
                        "token":$("#token").val()
                    }
            }).then(function (result) {
                if("error" in result){
                    $("#errors").css("display","block").empty().append(result["error"])
                }
                else if(result["signup_success"] == true){
                    window.location.reload();
                }
            });
        }
    },
    _backToLogin:function(){
        $("#nav-login-tab").click();
    },
    _openPopAndRenderTemp:function(evt){
        var theme_name = $(evt.currentTarget).attr('data-theme_name');
        return this._rpc({
            route: "/json/login/",
            params: {'theme_name':theme_name}
        }).then(function (result) {
            $("#nav-login").empty().append(result["loginTemp"]);
            $("#nav-login-tab").click();
            if("signupTemp" in result){
                $("#nav-register").empty().append(result["signupTemp"]);
            }
            if("resetTemp" in result){
                $("#nav-reset").empty().append(result["resetTemp"]);
            }

        });
    },
    _checkAuthentication:function(ev){
        if($("#login").val().trim() != "" && $("#password").val().trim() != ""){
            ev.preventDefault();
            return this._rpc({
                route: "/json/web/login",
                params: {
                        "login":$("#login").val(),
                        "password":$("#password").val()
                        }
            }).then(function (result) {
                if(result["login_success"] == true){
                    window.location.reload();
                }
                else if("error" in result){
                    $("#errormsg").css("display","block").empty().append(result["error"]);
                }
            });
        }
    }
});
});
