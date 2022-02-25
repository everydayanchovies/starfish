/**
 * Standard error handler for this interface
 */
function std_error_handler(jqXHR, textStatus, errorThrown){
	if(jqXHR.responseText != ""){
		$("#msg_error").html("<b>Oh oh:</b> "+jqXHR.responseText);
	}else{
		$("#msg_error").html("<b>Oh oh:</b> Something went wrong, but I don't know what");
	}
	$("#msg_error").show();
	$(window).scrollTop(0);
}

/**
 * Show login dialog
 **/
function show_login(cb_success, cb_cancel){
	// Set default callbacks
	if( typeof cb_success != "function" )
		cb_success = function(){
        location.reload(true);
    };
	if( typeof cb_cancel != "function")
		cb_cancel = function(){};

	// Set onclick event on Login button
	$('#btn_login_ok').click(function(){
		//do login
		login_api("#loginform",
			// On success
			function(data){
				// Hide lightbox
				$('#lightbox').hide()
				$('#no-account-div').hide();
				$('#account-div').show();
				// Dispatch to success callback
				cb_success(data)
			},
			// On error
			function(jqXHR, textStatus, errorThrown){
				$('#login_msg').html(
					"Combination of username and password incorrect."
				)
				$('#login_msg').show();
				document.getElementById("password").value='';
			}
		);
	});

	// Set onclick event on Cancel button
	$('#btn_login_cancel').click(function(){
		$('#lightbox').hide();
		// Dispatch to cancel callback
		cb_cancel();
	})
	// Show lightbox
	$('#lightbox').show()
}

/**
 * Submit a comment form
 *  form - id or element of the comment form
 */
function submit_comment_form(form){
    comment_api(form, function(){ location.reload(true); });
}

function load_questionform(model_type, model_id, questionbox_id) {
  cb_success = function(data){
    $(questionbox_id).html(data);
    $(questionbox_id).show();
    var n = $(document).height();
    $('html, body').animate({ scrollTop: n },'50');
  };
  load_questionform_api(model_type, model_id, cb_success);
}
