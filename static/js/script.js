// console.log('Loaded!');

var input = document.getElementById("nomeDonna");

// Execute a function when the user releases a key on the keyboard
input.addEventListener("keydown", function(event) {
  // Number 13 is the "Enter" key on the keyboard
  if (event.key === 'Enter') {
    // Cancel the default action, if needed
    event.preventDefault();
    // Trigger the button element with a click
    document.getElementById("donneBut").click();
  }
});

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

function sortObject(obj) {
    return Object.keys(obj).sort().reduce(function (result, key) {
        result[key] = obj[key];
        return result;
    }, {});
}

function onTelegramAuth(data){
    var arrayData = sortObject(data);
    var text = '';
    for (var k in arrayData){
        console.log(k);
        text += k + '=' + arrayData[k]+'\n';
    }
    text = text.replace(/\\n$/, '');
    console.log(text);

    $secret_key = hash('sha256', BOT_TOKEN, true);
    
}


function checkTelegramData(data, token){
  const secret = crypto.createHash('sha256').update(token).digest();
  let array = [];

  for (let key in data){
    if (key != 'hash') {
      array.push(key + '=' + data[key]);
    }
  }
  const check_hash = crypto
    .createHmac('sha256', secret)
    .update(array.sort().join('\n'))
    .digest('hex');

  return check_hash == data.hash;
}