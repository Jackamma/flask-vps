function updatePlayers(players){
	console.log(players);
	$("#players").empty();
	var i = 0;
	for (var p in players){
		$("#players").append('<li>'+players[p]+'</li>');
		i++;
	}
	$("#nPlayers").text(i+'');
}

$(document).ready(function() {

    if (isDataValid == 'True'){
        // socket.on('connect', function() {
        //     socket.emit('joined', 'User has connected!');
        // });

		const queryString = window.location.search;

		const urlParams = new URLSearchParams(queryString);

		const user = urlParams.get('id')
		const first_name = urlParams.get('first_name')

		var socket = io.connect(window.location.origin+'', {query: 'id='+user+'&first_name='+first_name});

		// socket.on('connect', updatePlayers);
		// socket.on('disconnect', updatePlayers);

		window.addEventListener('beforeunload', function (e) {
			socket.emit('disconnect');
		});

		socket.on('updatePlayers', function(players){
			console.log(players);
			$("#players").empty();
			var i = 0;
			for (var p in players){
				$("#players").append('<li>'+players[p]+'</li>');
				i++;
			}
			$("#nPlayers").text(i+'');
		});

    }
	
	

	// socket.on('message', function(msg) {
	// 	$("#players").append('<li>'+msg+'</li>');
	// 	console.log('Received message');
	// });

	// $('#sendbutton').on('click', function() {
	// 	socket.send($('#myMessage').val());
	// 	$('#myMessage').val('');
	// });

});