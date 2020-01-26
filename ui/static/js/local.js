var app = angular.module('myapp', []);


//------------------------------------- Set user response------------------------------------
function setUserResponse(val) {
	var UserResponse = '<img class="userAvatar" src=' + profile_pic + '><p class="userMsg">' + val + ' </p><div class="clearfix"></div>';
	$(UserResponse).appendTo('.chats').show('slow');
	console.log("val>>>",val)
	$(".usrInput").val('');
	scrollToBottomOfResults();
	$('.suggestions').remove();
	document.getElementById('keypad').focus();
}

//---------------------------------- Scroll to the bottom of the chats-------------------------------
function scrollToBottomOfResults() {
	var terminalResultsDiv = document.getElementById('chats');
	terminalResultsDiv.scrollTop = terminalResultsDiv.scrollHeight;
}

app.controller('myctrl',function($scope,$http){
	// on input/text enter--------------------------------------------------------------------------------------
$('.usrInput').on('keyup keypress', function (e) {
	var keyCode = e.keyCode || e.which;
	if (keyCode === 13) {
		  $scope.loading = true;
		  $scope.changewidth=true;
		//   $scope.isDisabled = true;
		  $scope.loadingmsg=true;
		  $('#btn-sumbit').trigger('click');
	}
});

$('#btn-sumbit').on('click', function() {
	$scope.loading = true;
	$scope.changewidth=true;
	// $scope.isDisabled = true;
	$scope.cngplace=true;
	scrollToBottomOfResults();
    var text = $(".usrInput").val();
	if (text == "" || $.trim(text) == '') {
			return false;
		} else {
			$(".usrInput").blur();
			setUserResponse(text);
			$scope.send(text);
			//e.preventDefault();
			return false;
		}
});



$scope.send=function(message) {
	console.log("User Message:", message)
	$http({
		method:"POST",
		url:"http://localhost:5005/webhooks/rest/webhook",
		data:{
			// access token for sms0286 13ede7d5d4e5750de80c9368021abe_dbcorp
			// access token for kamal 23d3c3aa2fc165698f10e62a3539f7_sequelone
			// access token for short leave 9ff0551ee04f9d151a25a6365fe457_hrconnect
			"sender": "9ff0551ee04f9d151a25a6365fe457_hrconnect",//{"access_token":"Rasa1","comp_code":"dev"},
			//"sender": "kamal",
			"message": message

		}

}).then(function(success){
	$scope.loading = false;
	$scope.changewidth=false;
	//$scope.isDisabled = false;
	$scope.loadingmsg=false;
	console.log("Rasa Response: ", success.data)
	$scope.res_text=success.data[0].text;
	setBotResponse(success.data);


})
		// success: function (data, textStatus) {
		// 	setBotResponse(data);
		// 	console.log("Rasa Response: ", data, "\n Status:", textStatus)
		// },
		// error: function (errorMessage) {
		// 	setBotResponse("");
		// 	console.log('Error' + errorMessage);

		// }
	}


			
//------------------------------------ Set bot response -------------------------------------
function setBotResponse(val) {
	setTimeout(function () {
		if (val.length < 1) {
			//if there is no response from Rasa
			msg = 'I couldn\'t get that. Let\' try something else!';

			var BotResponse = '<img class="botAvatar" src="./static/img/botAvatar.png"><p class="botMsg">' + msg + '</p><div class="clearfix"></div>';
			$(BotResponse).appendTo('.chats').hide().fadeIn(1000);

		} else {
			//if we get response from Rasa
			console.log('bighnesh', val)
			for (i = 0; i < val.length; i++) {
				//check if there is text message
					console.log('bighnesh'+i);
				if (val[i].hasOwnProperty("text")) {
					var BotResponse = '<img class="botAvatar" src="./static/img/botAvatar.png"><p class="botMsg">' + val[i].text + '</p><div class="clearfix"></div>';
					$(BotResponse).appendTo('.chats').hide().fadeIn(1000);
				}
				
				
				if (val[i].hasOwnProperty("attachment")) {
					var mydata= val[i].attachment;
					
						if(mydata.data_type== 'key_value'){
							//console.log('abcsadfdsf', mydata.data)
							var BotResponse = '<img class="botAvatar" src="./static/img/botAvatar.png"><ul class="botMsg">'
							for (j = 0; j < mydata.data.length; j++) {
								 BotResponse = BotResponse + '<li>' + mydata.data[j].key + '<span>'+ mydata.data[j].value +  '<span></li>'
							}
							BotResponse = BotResponse +  '</ul><div class="clearfix"></div>';
							$(BotResponse).appendTo('.chats').hide().fadeIn(1000);
							
						}else if(mydata.data_type== 'pending_ar_od_summary'){
							var BotResponse = '<img class="botAvatar" src="./static/img/botAvatar.png"><ul class="botMsg">'
							for (j = 0; j < mydata.data.length; j++) {
								BotResponse = BotResponse + '<li>' + mydata.data[j].type + '<span>'+ mydata.data[j].number_of_days +  '<span></li>'
							}
							BotResponse = BotResponse +  '</ul><div class="clearfix"></div>';
							$(BotResponse).appendTo('.chats').hide().fadeIn(1000);
	
						}else if(mydata.data_type== 'pending_ar_details'){
							var BotResponse = '<img class="botAvatar" src="./static/img/botAvatar.png"><ul class="botMsg">'
							for (j = 0; j < mydata.data.length; j++) {
								 BotResponse = BotResponse + '<li>' + '<p class="heading">'+ mydata.data[j].SNo + '&nbsp;&nbsp;&nbsp;'+ mydata.data[j].n +'</p>'+ mydata.data[j].applied_date + '<span>'+ mydata.data[j].Applied_Date_Time + '</span>' +'<br/>'
								 + mydata.data[j].from_date +'<span>' + mydata.data[j].From_date + '</span>' +'<br/>' + mydata.data[j].to_date + '<span>'+ mydata.data[j].To_date +'</span>' +'<br/>' +
								 mydata.data[j].in_time + '<span>' + mydata.data[j].In_time + '</span>' +'<br/>'+ mydata.data[j].out_time +'<span>' + mydata.data[j].Out_time + '</span>' +'<br/>' + mydata.data[j].reason + '<span>'+ mydata.data[j].Not_marking_reason + '</span>' +
								 '</li>'
							}
							BotResponse = BotResponse +  '</ul><div class="clearfix"></div>';
							$(BotResponse).appendTo('.chats').hide().fadeIn(1000);

						}else if(mydata.data_type== 'pending_od_details'){
							var BotResponse = '<img class="botAvatar" src="./static/img/botAvatar.png"><ul class="botMsg">'
							for (j = 0; j < mydata.data.length; j++) {
								 BotResponse = BotResponse + '<li>' + '<p class="heading">'+ mydata.data[j].SNo + '&nbsp;&nbsp;&nbsp;'+ mydata.data[j].n +'</p>'+ mydata.data[j].applied_date + '<span>'+ mydata.data[j].Applied_Date_Time + '</span>' +'<br/>'
								 + mydata.data[j].from_date +'<span>' + mydata.data[j].From_date + '</span>' +'<br/>' + mydata.data[j].to_date + '<span>'+ mydata.data[j].To_date +'</span>' + '</li>'
							}
							BotResponse = BotResponse +  '</ul><div class="clearfix"></div>';
							$(BotResponse).appendTo('.chats').hide().fadeIn(1000);

						}else if(mydata.data_type== 'leave_transaction_detail'){
							var BotResponse = '<img class="botAvatar" src="./static/img/botAvatar.png"><ul class="botMsg">'
							for (j = 0; j < mydata.data.length; j++) {
								 BotResponse = BotResponse + '<li>' + '<p class="heading">'+ mydata.data[j].SNo + '&nbsp;&nbsp;&nbsp;'+ mydata.data[j].n +'</p>'+ mydata.data[j].applied_date + '<span>'+ mydata.data[j].Applied_Date_Time + '</span>' +'<br/>'
								 + mydata.data[j].from_date +'<span>' + mydata.data[j].From_date + '</span>' +'<br/>' + mydata.data[j].to_date + '<span>'+ mydata.data[j].To_date +'</span>' +'<br/>' + mydata.data[j].reason + '<span>'+ mydata.data[j].Not_marking_reason + '</span>' +
								 '</li>'
							}
							BotResponse = BotResponse +  '</ul><div class="clearfix"></div>';
							$(BotResponse).appendTo('.chats').hide().fadeIn(1000);

						}else if(mydata.data_type== 'restarted_chatbot'){
							console.log(mydata);
						}else if(mydata.data_type== 'profile_pic'){
							window.profile_pic = mydata.data;
						}else if(mydata.data_type== 'todo_od_details'){
							var BotResponse = '<img class="botAvatar" src="./static/img/botAvatar.png"><ul class="botMsg">'
							for (j = 0; j < mydata.data.length; j++) {
								 BotResponse = BotResponse + '<li>' + '<p class="heading">'+ mydata.data[j].SNo + '&nbsp;&nbsp;&nbsp;'+ mydata.data[j].n +'</p>'+ mydata.data[j].emp_name + '<span>'+ mydata.data[j].Emp_Name + '</span>' +'<br/>'
								 + mydata.data[j].no_of_days +'<span>' + mydata.data[j].No_Of_Days + '</span>' +'<br/>' + mydata.data[j].from_date + '<span>'+ mydata.data[j].From_date +'</span>' +'<br/>' 
								 + mydata.data[j].to_date + '<span>'+ mydata.data[j].To_date +'</span>' + '</li>'
							}
							BotResponse = BotResponse +  '</ul><div class="clearfix"></div>';
							$(BotResponse).appendTo('.chats').hide().fadeIn(1000);

						}else if(mydata.data_type== 'todo_ar_details'){
							var BotResponse = '<img class="botAvatar" src="./static/img/botAvatar.png"><ul class="botMsg">'
							for (j = 0; j < mydata.data.length; j++) {
								 BotResponse = BotResponse + '<li>' + '<p class="heading">'+ mydata.data[j].SNo + '&nbsp;&nbsp;&nbsp;'+ mydata.data[j].n +'</p>'+ mydata.data[j].emp_name + '<span>'+ mydata.data[j].Emp_Name + '</span>' +'<br/>'
								 + mydata.data[j].from_date + '<span>'+ mydata.data[j].From_date +'</span>' + '<br/>' + mydata.data[j].to_date + '<span>'+ mydata.data[j].To_date + '</span>' + '<br/>'
								 + mydata.data[j].in_time + '<span>' + mydata.data[j].In_time + '</span>' + '<br/>' + mydata.data[j].out_time + '<span>' + mydata.data[j].Out_time + '</span>' + '<br/>'
								 + mydata.data[j].actual_in_time + '<span>' + mydata.data[j].Actual_in_time + '</span>' + '<br/>'
								 + mydata.data[j].actual_out_time + '<span>' + mydata.data[j].Actual_out_time + '</span>' +  '</li>'
							}
							BotResponse = BotResponse +  '</ul><div class="clearfix"></div>';
							$(BotResponse).appendTo('.chats').hide().fadeIn(1000);

						}else if(mydata.data_type== 'todo_leave_details'){
							var BotResponse = '<img class="botAvatar" src="./static/img/botAvatar.png"><ul class="botMsg">'
							for (j = 0; j < mydata.data.length; j++) {
								 BotResponse = BotResponse + '<li>' + '<p class="heading">'+ mydata.data[j].SNo + '&nbsp;&nbsp;&nbsp;'+ mydata.data[j].n +'</p>'+ mydata.data[j].emp_name + '<span>'+ mydata.data[j].Emp_Name + '</span>' +'<br/>'
								 + mydata.data[j].no_of_days +'<span>' + mydata.data[j].No_Of_Days + '</span>' +'<br/>' + mydata.data[j].from_date + '<span>'+ mydata.data[j].From_date +'</span>' +'<br/>' 
								 + mydata.data[j].to_date + '<span>'+ mydata.data[j].To_date +'</span>' +'<br/>' + mydata.data[j].leave_type + '<span>'+ mydata.data[j].Leave_Type +'</span>' + '</li>'
							}
							BotResponse = BotResponse +  '</ul><div class="clearfix"></div>';
							$(BotResponse).appendTo('.chats').hide().fadeIn(1000);

						}else if(mydata.data_type== 'faq_disable'){
							console.log('Enable Button');
							document.getElementById("faq").disabled = false;

						}
				}
				

				//check if there is image
				// if (val[i].hasOwnProperty("image")) {
					// var BotResponse = '<div class="singleCard">' +
						// '<img class="imgcard" src="' + val[i].image + '">' +
						// '</div><div class="clearfix">'
					// $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
				// }

				// //check if there is  button message
				if (val[i].hasOwnProperty("buttons")) {
					addSuggestion(val[i].buttons);
				}

			}
			scrollToBottomOfResults();
		}

	}, 500);
}


// ------------------------------------------ Toggle chatbot -----------------------------------------------
$('#profile_div').click(function () {
	$('.profile_div').toggle('scale');
	$('.widget').toggle('scale');
	document.getElementById('keypad').focus();
	scrollToBottomOfResults();

});

$('#close').click(function () {
	$('.profile_div').toggle('scale');
	$('.widget').toggle('scale');
});

document.getElementById("faq").onclick = function() {
    //disable
	this.disabled = true;

	//do some validation stuff
	var text = 'break out of current story'; 
	$scope.send(text);
	var faq_text = 'faq';
	$scope.send(faq_text);
}
// $('#faq').click(function () {
// 	var text = 'break out of current story'; 
// 	$scope.send(text);
// 	var faq_text = 'faq';
// 	$scope.send(faq_text);
// });
// ------------------------------------------ Suggestions -----------------------------------------------

function addSuggestion(textToAdd) {
	setTimeout(function () {
		var suggestions = textToAdd;
		var suggLength = textToAdd.length;
		$(' <div class="singleCard"> <div class="suggestions"><div class="menu"></div></div></diV>').appendTo('.chats').hide().fadeIn(1000);
		// Loop through suggestions
		for (i = 0; i < suggLength; i++) {
			$('<div class="menuChips">' + suggestions[i].title + '</div>').appendTo('.menu');
		}
		scrollToBottomOfResults();
	}, 1000);
}

$scope.starting_msg = [{text: "Hello, I'm Honobot." }]
console.log($scope.starting_msg);

setBotResponse($scope.starting_msg);

$scope.initialize_msg = [{text: "Initializing Your Data Please Wait..." }]
console.log($scope.initialize_msg);

setBotResponse($scope.initialize_msg);

var text = 'break out of current story';
//setUserResponse(text);
$scope.send(text);

var infotext = 'getting user info from api';
$scope.send(infotext);
// $(document).on("click", ".profile_div", function () {
	
// 	$scope.starting_msg = [{text: "Hello, I'm Honobot." }]
// 	console.log($scope.starting_msg);
	
// 	setBotResponse($scope.starting_msg);
	

// 	//$('.suggestions').remove(); //delete the suggestions 
// });

// on click of suggestions, get the value and send to rasa
$(document).on("click", ".menu .menuChips", function () {
	$scope.loading = true;
	$scope.changewidth=true;
	$scope.loadingmsg=true;
	scrollToBottomOfResults();
	var text = this.innerText;
	setUserResponse(text);
	$scope.send(text);
	$('.suggestions').remove(); //delete the suggestions 
});


$(document).on("click", ".see_more", function () {
		 
			document.getElementById("dots").innerHTML =
			'4. View Leave Balance<br> 5. View Anniversary List<br>\
			6. View Attendance Calendar<br> 7. View Holiday List<br>\
			8. News<br> 9. View Salary Details <br> 10. Weather report<br>\
			11. View Team Details (for managers only)<br>\
			12. View/Approve Pending Requests (for managers only)<br>\
			13. Raise Zendesk Tickets';
			document.getElementById("myBtn").style.display = 'none';
			scrollToBottomOfResults();
			document.getElementById('keypad').focus();

			

});


});

