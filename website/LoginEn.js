LOCALE_LANG="zh";
$(function(){
	$.ajax(	'/iaaa/getPreferLanguage.do',
		{
		type:"GET",
		dataType:"json",
		data:{_rand:Math.random()},
		success : function(data,status,xhr) {
			var json = data;
        	if(true == json.success)
            	LOCALE_LANG = json.language;
            switch2English();
		},
		error : function(xhr,status,error) {
			//$("#msg").text("查询时出现异常");
			$("#msg").html("<i class=\"fa fa-minus-circle\"></i> 查询时出现异常");
			$("#code_img").attr("src","/iaaa/servlet/DrawServlet?Rand="+Math.random());
		}
	});
});
function switch2English(){
//	LOCALE_LANG =  (navigator.language  ||  navigator.userLanguage).toString().toLowerCase();
	if(LOCALE_LANG.indexOf("zh")<0){
		//NOT CHINESE
		$("title").text("Unified Authentication System of Peking University");
		$("#login_panel_top_bar").text("User ID");
		$("#qrcode_panel_top_bar").text("QR Code");
		$("#qrcode_tip").text("Use PKU App to scan the QR code");
		$("#user_name").attr("placeholder","User ID / PKU Email / Cell Phone");
		$("#password").attr("placeholder","Password");
		$("#password").siblings(".pad-tip").text("Forgot");
		$("#sms_code").attr("placeholder","SMS Code");
		$("#sms_button").val("Send");
		$("#otp_code").attr("placeholder","OTP Code");
		$("#otp_code").siblings(".pad-tip").text("Help");
		$("#valid_code").attr("placeholder","CAPTCHA");
		$("#valid_code").siblings(".pad-tip").text("Change");
		$("#remember_text").html("<i class=\"fa fa-square-o i-check\"></i> Remember ID");
		$("#otp_button").val("Bind App");
		$("#logon_button").val("Login");
		$(".bottom span:first-child").text("Hotline: 010-62751023");
		if($(".bottom span:last-child a").length>0)
			$(".bottom span:last-child a").text("Computer Center, PKU");
		else
			$(".bottom span:last-child").text("© Computer Center, PKU");
	}
}
