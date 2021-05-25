
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
			console.log(players);
			$("#players").empty();
			var i = 0;
			for (var p in players){
				$("#players").append('<li>'+players[p]+'</li>');
				i++;
			}
			$("#nPlayers").text(i+'');

			if (i > 1){
				$("#startIppo").attr('disabled', false);
				$("#startIppo").attr('hidden', false);
			} else {
				$("#startIppo").attr('disabled', true);
				$("#startIppo").attr('hidden', true);
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