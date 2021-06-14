var isGameActive = false;

$(document).ready(function() {

    if (isDataValid == 'True'){

		const queryString = window.location.search;

		const urlParams = new URLSearchParams(queryString);

		const user = urlParams.get('id')
		const first_name = urlParams.get('first_name')

		var socket = io.connect(window.location.origin+'', {query: 'id='+user+'&first_name='+first_name});
		  
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

		$(".betButt").click(function(){
			// var abc = $(this).closest(".head-div").attr("id");
			var currId = this.id+'';
			$.post( "/sendBet", '{ "user":"'+user+'", "bet":"'+currId+'" }');
			$(".betButt").attr('hidden', true);
			$('#'+currId.replace('betHorse', 'name')).css('color', 'green');
		});

		socket.on('startGame', function(){
			// isGameActive = true;
			$("#startIppo").attr('disabled', true);
			$("#startIppo").attr('hidden', true);
			// $("#countdown").attr('hidden', false);
			$("#beforeStart").attr('hidden', false);
			$(".betButt").attr('hidden', false);
			$(".horseName").css('color', 'white');
		});

		socket.on('startCountdown', function(num){
			if (num == 0)
				num = 'VIA!';
			// console.log(num);
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
				$("#raceBg").attr('hidden', false);
				$(".results").attr('hidden', true);
				$("#beforeStart").attr('hidden', true);
				isGameActive = true;
				var race = setInterval(function(){
					// console.log(winnerList[0]['race']);
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
						$(".horse").css('visibility', 'visible');
						$(".horse").css('left', '-40%');
						$("#first").text(winnerList[0]['name']+' ('+winnerList[0]['time']+' s) [multiplier '+winnerList[0]['multiplier']+'x]');
						$("#second").text(winnerList[1]['name']+' ('+winnerList[1]['time']+' s) [multiplier '+winnerList[1]['multiplier']+'x]');
						$("#third").text(winnerList[2]['name']+' ('+winnerList[2]['time']+' s) [multiplier '+winnerList[2]['multiplier']+'x]');
						$("#fourth").text(winnerList[3]['name']+' ('+winnerList[3]['time']+' s) [multiplier '+winnerList[3]['multiplier']+'x]');
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