
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

			if (i >= 1){
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

		socket.on('startGame', function(){
			$("#startIppo").attr('disabled', true);
			$("#startIppo").attr('hidden', true);
			$("#raceBg").attr('hidden', false);
		});

		socket.on('runRace', function(horseList){
			// console.log('start!');
			// console.log(horseList);

			$("#horse1").css('left', horseList[0]+'%');
			$("#horse2").css('left', horseList[1]+'%');
			$("#horse3").css('left', horseList[2]+'%');
			$("#horse4").css('left', horseList[3]+'%');
			
			// for (var z=0; z < 95; z+=0.1){
			// 	setTimeout(function(z){ 
			// 		$("#horse1").css('padding-left', z+'%');
			// 		$("#horse2").css('padding-left', z+'%');
			// 		$("#horse3").css('padding-left', z+'%');
			// 		$("#horse4").css('padding-left', z+'%');
			// }, z*100, z);
				// console.log(i);
			// }
		});

		socket.on('finishRace', function(winnerList){
			$(".results").attr('hidden', false);
			$("#first").text(winnerList[0]);
			$("#second").text(winnerList[1]);
			$("#third").text(winnerList[2]);
			$("#fourth").text(winnerList[3]);
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