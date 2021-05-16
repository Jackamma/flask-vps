// console.log('Loaded!');

var input = document.getElementById("nomeDonna");

// Execute a function when the user releases a key on the keyboard
if (input){
	input.addEventListener("keydown", function(event) {
		// Number 13 is the "Enter" key on the keyboard
		if (event.key === 'Enter') {
			// Cancel the default action, if needed
			event.preventDefault();
			// Trigger the button element with a click
			document.getElementById("donneBut").click();
		}
	});
}

function showDonnaResult(maleNames){
		// console.log('clicked!');
		var nome = document.getElementById('nomeDonna').value;
		var res = document.getElementById('resultDonna');

		// console.log('Nome = '+nome);

		if (nome){
		// console.log(maleNames);
		nome = nome.trim();

		if (!maleNames.includes(nome.toLowerCase())){
					res.firstChild.textContent = nome + ' è troia';
		} else {
			res.firstChild.textContent = nome + ' NON è troia';
		}
				res.removeAttribute('hidden');
		} else {
				res.setAttribute('hidden', 'true');
		}
}

// var opts = {
// 	method: 'GET',      
// 	headers: {}
// };
// fetch('/get-data', opts).then(function (response) {
// 	return response.json();
// })
// .then(function (body) {
// 	console.log(body);
// });

// const urlParams = new URLSearchParams(window.location.search);

// if (urlParams.get('id')){
// 	fetch('/onlinedata', {
// 		method: 'POST', // or 'PUT'
// 		headers: { 'Content-Type': 'application/json' },
// 		body: JSON.stringify({'id':urlParams.get('id')}),
// 	})
// 	.then(response => response.json())
// 	.then(data => {
// 		console.log('Success:', data);
// 	})
// 	.catch((error) => {
// 		console.error('Error:', error);
// 	});
// }

// window.addEventListener("beforeunload", function(event) {
// 	if (urlParams.get('id')){
// 		fetch('/onlinedata', {
// 			method: 'POST', // or 'PUT'
// 			headers: { 'Content-Type': 'application/json' },
// 			body: JSON.stringify({'id':urlParams.get('id')}),
// 		})
// 		.then(response => response.json())
// 		.then(data => {
// 			console.log('Success:', data);
// 		})
// 		.catch((error) => {
// 			console.error('Error:', error);
// 		});
// 	}
// });
