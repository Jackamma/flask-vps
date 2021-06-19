var isGameActive = false;

$(document).ready(function() {

    if (isDataValid == 'True'){

		$('#sendButton').on('click', function(){
			// console.log($('#inputText').val());
			if ($('#inputText').val().trim()){
				socket.emit('sendMessage', {'text':first_name+': '+$('#inputText').val().trim(), 'propic':propic});
			}
			$('#inputText').val('');
		});

		const queryString = window.location.search;

		const urlParams = new URLSearchParams(queryString);

		const user = urlParams.get('id')
		const first_name = urlParams.get('first_name')
		const propic = urlParams.get('photo_url');

		var socket = io.connect(window.location.origin+'', {query: 'id='+user+'&first_name='+first_name});

		var input = document.getElementById("inputText");

		// Execute a function when the user releases a key on the keyboard
		if (input){
			input.addEventListener("keydown", function(event) {
				// Number 13 is the "Enter" key on the keyboard
				if (event.key === 'Enter') {
					// Cancel the default action, if needed
					event.preventDefault();
					// Trigger the button element with a click
					document.getElementById("sendButton").click();
				}
			});
		}

		function updateMessage(msg, isService){
			var div = document.createElement('div');
			div.style = 'position: relative; float: left; margin-left: 10px; text-align: left;';
			var img = document.createElement("img");
			img.src = msg['propic'];
			img.className += "profile_img";
			var tag = document.createElement("span");
			var text = document.createTextNode(msg['text']);
			if (isService){
				tag.style.fontStyle = 'italic';
				tag.style.fontWeight = 'bold';
				tag.style.color = 'green';
			}
			tag.appendChild(text);
			tag.className += "message";
			var messagesBox = document.getElementById("messagesBox");
			div.appendChild(img);
			div.appendChild(tag);
			messagesBox.appendChild(div);
			messagesBox.appendChild(document.createElement("br"));
			// $("#messagesBox").animate({ scrollTop: 9999999 }, 400);
			// console.log(document.getElementById('messagesBox').scrollHeight);
			$("#messagesBox").animate({ scrollTop: document.getElementById('messagesBox').scrollHeight }, 400);
		}

		socket.on('updateMessage', function(msg){
			updateMessage(msg);
		});

		socket.on('updateServiceMessage', function(msg){
			updateMessage(msg, true);
		});
		  
		document.addEventListener("visibilitychange", function(){
			if (document.hidden){
				socket.emit('real_disconnect');
			} else {
				socket.emit('real_connect');
			}
		}, false);

		socket.on('updatePlayers', function(players){
			// console.log(players);
			$("#players").empty();
			var i = 0;
			for (var p in players){
				$("#players").append('<li>'+players[p]+'</li>');
				i++;
			}
			$("#nPlayers").text(i+'');

			var minPlayer = window.location.hostname == '127.0.0.1' ? 1 : 2;

			if ((i >= minPlayer || user == '25571068' || user == '175104816') && !isGameActive){
				$("#startIppo").attr('disabled', false);
				$("#startIppo").attr('hidden', false);
			} else {
				$("#startIppo").attr('disabled', true);
				$("#startIppo").attr('hidden', true);
			}
		});

		$("#startIppo").click(function(){
			socket.emit('startGame');
		});

		// socket.on('gameAlreadyStarted', function(){
		// 	alert('')
		// });

		var betResult;

		$(".betButt").click(function(){
			// var abc = $(this).closest(".head-div").attr("id");
			var horseNames = {'betHorse0':'CAVALLO', 'betHorse1':'REINBO', 'betHorse2':'UNICORNO', 'betHorse3':'FANTINO'};
			var currId = this.id+'';
			var posting = $.post("/sendBet", '{ "user":"'+user+'", "bet":"'+currId+'", "code":"'+gameCode+'" }');
			posting.done(function(res){
				// console.log('Risultato: '+res);
				betResult = res;
			});
			$(".betButt").attr('hidden', true);
			$('#'+currId.replace('betHorse', 'name')).css('color', 'green');
			socket.emit('sendServiceMessage', {'text':first_name+' ha scommesso su '+horseNames[this.id], 'propic':propic});
		});

		var gameCode;
		socket.on('startGame', function(code){
			if (code)
				gameCode = code;
			// isGameActive = true;
			$("#startIppo").attr('disabled', true);
			$("#startIppo").attr('hidden', true);
			// $("#countdown").attr('hidden', false);
			$("#beforeStart").attr('hidden', false);
			$(".betButt").attr('hidden', false);
			$(".horseName").css('color', 'white');
		});

		socket.on('startCountdown', function(num){
			$("#countdown").text(num+'');
		});

		// funzione deprecata
		socket.on('runRace', function(horseList){
			// console.log('start!');
			// console.log(horseList);

			$("#horse0").css('left', horseList[0]+'%');
			$("#horse1").css('left', horseList[1]+'%');
			$("#horse2").css('left', horseList[2]+'%');
			$("#horse3").css('left', horseList[3]+'%');
			
		});


		socket.on('sendRace', function(winnerList){
			// console.log(winnerList);
			if (!isGameActive){
				
				isGameActive = true;

				var isCountdownActive = true;
				var i_countdown = 10;
				var countdown = setInterval(() => {
					i_countdown--;
					if (i_countdown){
						$("#countdown").text(i_countdown+'');
					} else {
						clearInterval(countdown);
						isCountdownActive = false;
						$("#beforeStart").attr('hidden', true);
						$("#raceBg").attr('hidden', false);
						$(".results").attr('hidden', true);
						$("#countdown").text('10');
					}
				}, 1000);

				var race = setInterval(function(){
					// console.log(winnerList[0]['race']);
					if (!isCountdownActive){
						if (winnerList[0]['race'].length > 0 || winnerList[1]['race'].length > 0 || winnerList[2]['race'].length > 0 || winnerList[3]['race'].length > 0){
							for (var i = 0; i < 4; i++){
								if (winnerList[i]['race'].length > 0){
									$("#horse"+winnerList[i]['number']).css('left', winnerList[i]['race'][0]+'%');
									winnerList[i]['race'].shift();

									// Non funziona, lascia spazio e rompe tutto, trovare altra soluzione
									if (winnerList[i]['race'].length == 0){
										// $("#horse"+winnerList[i]['number']).attr('hidden', true);
										$("#horse"+winnerList[i]['number']).css('visibility', 'hidden');
									}
								}
							}
						} else {
							clearInterval(race);
							isGameActive = false;
							$("#startIppo").attr('disabled', false);
							$("#startIppo").attr('hidden', false);
							$("#raceBg").attr('hidden', true);
							$(".results").attr('hidden', false);
							if (betResult == '0')
								$("#betResult").text('HAI VINTO!');
							else
								$("#betResult").text('Hai scommesso sul cavallo sbagliato :(');
							$(".horse").css('visibility', 'visible');
							$(".horse").css('left', '-40%');
							$("#first").text(winnerList[0]['name']+' ('+winnerList[0]['time']+' s) [multiplier '+winnerList[0]['multiplier']+'x]');
							$("#second").text(winnerList[1]['name']+' ('+winnerList[1]['time']+' s) [multiplier '+winnerList[1]['multiplier']+'x]');
							$("#third").text(winnerList[2]['name']+' ('+winnerList[2]['time']+' s) [multiplier '+winnerList[2]['multiplier']+'x]');
							$("#fourth").text(winnerList[3]['name']+' ('+winnerList[3]['time']+' s) [multiplier '+winnerList[3]['multiplier']+'x]');
						}
					}
				}, 100);
			}
				
		});

		// $('#startIppo').on('click', function() {
		// 	socket.send($('#myMessage').val());
		// 	$('#myMessage').val('');
		// });

    }
	
	

	// socket.on('message', function(msg) {
	// 	$("#players").append('<li>'+msg+'</li>');
	// 	console.log('Received message');
	// });

	

});