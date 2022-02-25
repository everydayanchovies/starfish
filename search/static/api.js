/**
 * Helper function to get cookie
 * Source: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * General API call function
 *  1). Forwards the asynchronous request to the API
 *  2). Checks the response:
 *    a): [Case 200] Call callback for success
 *    b): [Case 401] Issue login procedure and try again
 *    c): [Otherwise] Call callback for error
 *
 * Arguments:
 *  endpoint - The API url to connect to
 *  data - The data to be send, default: null
 *  method - "get" or "post", default: based on data
 *  cb_success - Callback in case of success, default: empty
 *  cb_error - Callback in case an unexpected error occurs, default: empty
 *  cb_cancel - Callback in case login was required but canceled, default: empty
 */
function api_call(endpoint, data, method, cb_success, cb_error, cb_cancel)
{
	// Set default callbacks
	if( typeof cb_success != "function") cb_success = function(){};
	if( typeof cb_error != "function") cb_error = std_error_handler;
	if( typeof cb_cancel != "function") cb_cancel = function(){};
	// Set default data
	if( data == undefined ) data = null
	// Set default method
	if( method == undefined && data == null)  method = "get"
	else if( method == undefined) method = "post"
	// Setup attempt to execute post call to api
	if(method == "post"){
		if(data == null) data = {}
		// Setup ajax with CSRF token
		$.ajaxSetup({ crossDomain: false, });
		data['csrfmiddlewaretoken'] = getCookie('csrftoken');
		var jqxhr = $.post(endpoint, data);
	}else if(method == "get" && data != null){
		var jqxhr = $.get(endpoint, data);
  }else{
		var jqxhr = $.get(endpoint);
	}
	// Add handler for the success case
	jqxhr.done(function(response, textStatus, jqXHR){
		cb_success(response, jqXHR)
	});
	// Add handler for the fail case
	jqxhr.fail(function(jqXHR, textStatus, errorThrown){
		// error code is 401 (Unauthorized)
		if(jqXHR.status == 401){
			// Show login dialog
			show_login(
				function(){
					// Login success: try api call again
					api_call(endpoint, data, method, cb_success, cb_error, cb_cancel);
				},
				function(){
					// Login cancel
					cb_cancel();
					// Assist garbage collect
					data = null
				}
				);
		}else{
			// Unexpected error, not related to login
			cb_error(jqXHR, textStatus, errorThrown)
			// Assist garbage collect
			data = null
		}
	});
}

/**
 * Generic API call from form. Form data is serialized with jQuery.
 */
function generic_form_api(endpoint, form, success_cb, error_cb, cancel_cb){
	$('div.django-ckeditor-widget textarea').each(function () {
		var $textarea = $(this);
		$textarea.val(CKEDITOR.instances[$textarea.attr('id')].getData());
	 });
	var formdata = $(form).serialize();
	api_call(endpoint, formdata, "post", success_cb, error_cb, cancel_cb);
}

/**
 * Login using the API.
 *  form - element or id, form contains `username', `password` and csrftoken
 *  success_cb - Callback in case of success
 *  error_cb - Callback in case of an error
 */
function login_api(form, success_cb, error_cb){
	generic_form_api("/login", form, success_cb, error_cb);
}

/**
 * Post comment using the API.
 *  form - element or id, form contains ....
 *  success_cb - Callback in case of success
 *  error_cb - Callback in case of an error
 *  cancel_cb - Callback in case of a cancelled procedure
 */
function comment_api(form, success_cb, error_cb, cancel_cb){
	generic_form_api("/comment", form, success_cb, error_cb, cancel_cb);
}

/**
 * Cast vote using the API.
 *  model_type - Type of the object that the vote is about
 *  model_id - Id of the object that the vote is about
 *  vote - Either +1 or -1
 */
function vote_api(model_type, model_id, vote)
{
	data = {'model':model_type, 'id':model_id, 'vote':vote}
	endpoint = "/vote"
	cb_success = function(){
		location.reload(true);
	};
	return api_call(endpoint, data, "post", cb_success);
}

function load_questionform_api(model_type, model_id, cb_success)
{
	data = {'model':model_type, 'id':model_id}
  endpoint = "/loadquestionform"
	return api_call(endpoint, data, "get", cb_success);
}
