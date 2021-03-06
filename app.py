# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import peewee, os, hmac, time, uuid
from hashlib import sha256
from flask_socketio import SocketIO, send, emit
from random import randint, uniform

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins='*')

db = peewee.SqliteDatabase(
	os.path.join(
		os.path.dirname(os.path.realpath(__file__)),
		'stats.db'
	)
)

maxPadding = 40
minPadding = -40
horses = [{'name':'Cavallo', 'position':0, 'number':0},
			{'name':'Reinbo', 'position':0, 'number':1},
			{'name':'Unicorno', 'position':0, 'number':2},
			{'name':'Fantino', 'position':0, 'number':3}]

minPos = 0.001
maxPos = 0.5
timeDelay = 0.1

class Horse:
	def __init__(self, args):
		self.position = minPadding
		self.name = args['name']
		self.number = args['number']
		self.multiplier = round(uniform(1,2), 2)
		
	def addPosition(self):

		toAdd = uniform(minPos,maxPos)
		self.position += toAdd * self.multiplier
		#print('Nuova posizione:',self.position)
		return self.position

class visits(peewee.Model):
	number = peewee.IntegerField()
	page = peewee.TextField()

	class Meta:

		database = db
		db_table = 'visits'

visits.create_table()

bot_token = open(os.path.join(
		os.path.dirname(os.path.realpath(__file__)),
		'token.txt'
	)).read()

bot_token = bot_token.strip()

@app.route("/")
def home():
	try:
		v = visits.get(visits.page=='home')
		n = v.number + 1
		visits.update(number=n).where(visits.page=='home').execute()
	except:
		n = 1
		new = visits.create(number=1, page='home')
		new.save()
	return render_template('index.html')

onlineUsers = {}
isGameActive = False

@socketio.on('connect')
def sockConnect():
	# print('\n+++++++++++', 'connesso', '+++++++++++\n')
	if request.args.get('id'):
		onlineUsers[request.args.get('id')] = request.args.get('first_name')
		emit('updatePlayers', onlineUsers, broadcast=True)
		# print('\n+++++++++++', onlineUsers, '+++++++++++\n')

@socketio.on('real_disconnect')
def realSockDisconnect():
	curr_id = request.args.get('id')
	if curr_id and curr_id in onlineUsers:
		onlineUsers.pop(curr_id)
		emit('updatePlayers', onlineUsers, broadcast=True)

@socketio.on('real_connect')
def sockConnect():
	if request.args.get('id'):
		onlineUsers[request.args.get('id')] = request.args.get('first_name')
		emit('updatePlayers', onlineUsers, broadcast=True)

@socketio.on('disconnect')
def sockDisconnect():
	# print('\n+++++++++++', 'disconnesso', '+++++++++++\n')
	curr_id = request.args.get('id')
	if curr_id and curr_id in onlineUsers:
		onlineUsers.pop(curr_id)
		emit('updatePlayers', onlineUsers, broadcast=True)
		# print('+++++++++++', onlineUsers, '+++++++++++')

allGames = {}

@socketio.on('startGame')
def startGame():
	global isGameActive, allGames
	if isGameActive:
		emit('startGame')
		return
	gameCode = uuid.uuid4().hex
	emit('startGame', gameCode, broadcast=True)

	
	# print('-------------- START GAME --------------')
	isGameActive = True

	horseList = []
	for h in horses:
		horseList.append(Horse(h))
	horsesRace = {}
	winnerHorses = []
	winnerHorsesList = []
	raceResults = {}

	for h in horseList:
		if h.name not in horsesRace:
			horsesRace[h.name] = []

	start = time.time()
	order = 0
	i = 0
	while len(winnerHorsesList) < 4:
		i+=1
		# JShorseList = []
		for h in horseList:
			if h.name not in winnerHorsesList:
				newPos = h.addPosition()
				if newPos > maxPadding:
					newPos = maxPadding
				horsesRace[h.name].append(newPos)
				if newPos == maxPadding:
					# horsesRace[h.name].append(newPos)
					# h.position = maxPadding
					winnerHorsesList.append(h.name)
					# winnerHorses.append([h.name, round(time.time()-start, 2)])
					winnerHorses.append({'name':h.name, 'time':round(i*timeDelay, 2), 'multiplier':h.multiplier, 'race':horsesRace[h.name], 'number':h.number})
					raceResults[str(h.number)] = order
					order+=1
			# JShorseList.append(h.position)

		# time.sleep(timeDelay)
			
		# emit('runRace', JShorseList, broadcast=True)

	allGames[gameCode] = raceResults

	emit('sendRace', winnerHorses, broadcast=True)
	isGameActive = False

# @socketio.on('updatePlayers')
# def handleMessage(players):
# 	print('players: ' + str(players))
# 	print('\n+++++++++++', 'update', '+++++++++++\n')
# 	send(players, broadcast=True)

@app.route("/ippodromo/")
def ippo():
	isDataValid = False
	isDataExpired = False
	if request.args.get('hash'):
		dataArray = []
		for i in request.args:
			strToAdd = i+'='+request.args[i]
			if strToAdd not in dataArray and i != 'hash':
				dataArray.append(i+'='+request.args[i])
		dataArray.sort()
		hashString = '\n'.join(dataArray)
		secret = bot_token.encode()
		API_SECRET = sha256(secret).digest()
		message = hashString.encode()
		signature = hmac.new(
			API_SECRET,
			msg=message,
			digestmod=sha256
		).hexdigest()

		isDataValid = hmac.compare_digest(signature.encode(), request.args.get('hash').encode())
		tHash = request.args.get('hash')

		unix_time_now = int(time.time())
		unix_time_auth_date = int(request.args.get('auth_date'))

		if unix_time_now - unix_time_auth_date > 86400:
			isDataValid = False
			isDataExpired = True
		# print(signature, '=', tHash)

	if request.host == '127.0.0.1:5000':
		isDataValid = True
		isDataExpired = False

	first_name = request.args.get('first_name')
	# if isDataValid and not isDataExpired:
	# 	onlineUsers[request.args.get('id')] = first_name
	# nOnlineUsers = len(onlineUsers)
	return render_template('ippo.html', isDataValid=isDataValid, first_name=first_name, isDataExpired=isDataExpired)

@socketio.on('sendMessage')
def sendMessage(msg):
	emit('updateMessage', msg, broadcast=True)

@socketio.on('sendServiceMessage')
def sendMessage(msg):
	emit('updateServiceMessage', msg, broadcast=True)

bets = {}

@app.route('/sendBet',methods=['POST'])
def sendBet():
	global allGames
	if request.method=='POST':
		res = request.get_json(force=True)
		print('----------------------')
		horseN = res['bet'].replace('betHorse', '')
		bets[res['user']] = horseN
		print(allGames)
		return str(allGames[res['code']][horseN])
		# return '{"Content-Type": "application/json","test":"test!!"}'
	# else:    
	# 	return render_template('index.html')

@app.route("/donne/")
def donne():
	maleNames = [ 'christian', 'jacopo', 'erik', 'eric', 'gabbro', 'daniel', 'pilota', 'pino', 'nando', 'nevio', 'teo', 'daniil', 'abaco', 'abbondanzio', 'abbondio', 'abdone', 'abelardo', 'abele', 'abenzio', 'abibo', 'abramio', 'abramo', 'acacio', 'acario', 'accursio', 'achille', 'acilio', 'aciscolo', 'acrisio', 'adalardo', 'adalberto', 'adalfredo', 'adalgiso', 'adalrico', 'adamo', 'addo', 'adelardo', 'adelberto', 'adelchi', 'adelfo', 'adelgardo', 'adelmo', 'adeodato', 'adolfo', 'adone', 'adriano', 'adrione', 'afro', 'agabio', 'agamennone', 'agape', 'agapito', 'agazio', 'agenore', 'agesilao', 'agostino', 'agrippa', 'aiace', 'aidano', 'aimone', 'aladino', 'alamanno', 'alano', 'alarico', 'albano', 'alberico', 'alberto', 'albino', 'alboino', 'albrico', 'alceo', 'alceste', 'alcibiade', 'alcide', 'alcino', 'aldo', 'aldobrando', 'aleandro', 'aleardo', 'aleramo', 'alessandro', 'alessio', 'alfio', 'alfonso', 'alfredo', 'algiso', 'alighiero', 'almerigo', 'almiro', 'aloisio', 'alvaro', 'alviero', 'alvise', 'amabile', 'amadeo', 'amando', 'amanzio', 'amaranto', 'amato', 'amatore', 'amauri', 'ambrogio', 'ambrosiano', 'amedeo', 'amelio', 'amerigo', 'amico', 'amilcare', 'amintore', 'amleto', 'amone', 'amore', 'amos', 'ampelio', 'anacleto', 'andrea', 'angelo', 'aniceto', 'aniello', 'annibale', 'ansaldo', 'anselmo', 'ansovino', 'antelmo', 'antero', 'antimo', 'antino', 'antioco', 'antonello', 'antonio', 'apollinare', 'apollo', 'apuleio', 'aquilino', 'araldo', 'aratone', 'arcadio', 'archimede', 'archippo', 'arcibaldo', 'ardito', 'arduino', 'aresio', 'argimiro', 'argo', 'arialdo', 'ariberto', 'ariele', 'ariosto', 'aris', 'aristarco', 'aristeo', 'aristide', 'aristione', 'aristo', 'aristofane', 'aristotele', 'armando', 'arminio', 'arnaldo', 'aronne', 'arrigo', 'arturo', 'ascanio', 'asdrubale', 'asimodeo', 'assunto', 'asterio', 'astianatte', 'ataleo', 'atanasio', 'athos', 'attila', 'attilano', 'attilio', 'auberto', 'audace', 'augusto', 'aureliano', 'aurelio', 'auro', 'ausilio', 'averardo', 'azeglio', 'azelio', 'bacco', 'baldassarre', 'balderico', 'baldo', 'baldomero', 'baldovino', 'barbarigo', 'bardo', 'bardomiano', 'barnaba', 'barsaba', 'barsimeo', 'bartolo', 'bartolomeo', 'basileo', 'basilio', 'bassiano', 'bastiano', 'battista', 'beato', 'bellino', 'beltramo', 'benedetto', 'beniamino', 'benigno', 'benito', 'benvenuto', 'berardo', 'berengario', 'bernardo', 'beronico', 'bertoldo', 'bertolfo', 'biagio', 'bibiano', 'bindo', 'bino', 'birino', 'bonagiunta', 'bonaldo', 'bonaventura', 'bonavita', 'bonifacio', 'bonito', 'boris', 'bortolo', 'brancaleone', 'brando', 'bruno', 'bruto', 'caino', 'caio', 'calanico', 'callisto', 'calogero', 'camillo', 'candido', 'cantidio', 'canziano', 'carlo', 'carmelo', 'carmine', 'caronte', 'carponio', 'casimiro', 'cassiano', 'cassio', 'casto', 'cataldo', 'catullo', 'cecco', 'cecilio', 'celso', 'cesare', 'cesario', 'cherubino', 'chiaffredo', 'cino', 'cipriano', 'cirano', 'ciriaco', 'cirillo', 'cirino', 'ciro', 'clarenzio', 'claudio', 'cleandro', 'clemente', 'cleonico', 'climaco', 'clinio', 'clodomiro', 'clodoveo', 'colmanno', 'colmazio', 'colombano', 'colombo', 'concetto', 'concordio', 'corbiniano', 'coreno', 'coriolano', 'cornelio', 'coronato', 'corrado', 'cosimo', 'cosma', 'costante', 'costantino', 'costanzo', 'cremenzio', 'crescente', 'crescenzio', 'crespignano', 'crispino', 'cristaldo', 'cristiano', 'cristoforo', 'crocefisso', 'cuniberto', 'cupido', 'daciano', 'dacio', 'dagoberto', 'dalmazio', 'damaso', 'damiano', 'damocle', 'daniele', 'danilo', 'danio', 'dante', 'dario', 'davide', 'davino', 'decimo', 'delfino', 'demetrio', 'democrito', 'demostene', 'deodato', 'desiderato', 'desiderio', 'didimo', 'diego', 'dino', 'diocleziano', 'diodoro', 'diogene', 'diomede', 'dione', 'dionigi', 'dionisio', 'divo', 'dodato', 'domenico', 'domezio', 'domiziano', 'donatello', 'donato', 'doriano', 'doroteo', 'duccio', 'duilio', 'durante', 'eberardo', 'ecclesio', 'edgardo', 'edilberto', 'edmondo', 'edoardo', 'efisio', 'efrem', 'egeo', 'egidio', 'eginardo', 'egisto', 'eleuterio', 'elia', 'eliano', 'elifio', 'eligio', 'elio', 'eliodoro', 'eliseo', 'elita', 'elmo', 'elogio', 'elpidio', 'elvezio', 'elvino', 'emanuele', 'emidio', 'emiliano', 'emilio', 'emmerico', 'empirio', 'endrigo', 'enea', 'enecone', 'ennio', 'enrico', 'enzo', 'eraclide', 'eraldo', 'erardo', 'erasmo', 'erberto', 'ercolano', 'ercole', 'erenia', 'eriberto', 'erico', 'ermanno', 'ermenegildo', 'ermes', 'ermete', 'ermilo', 'erminio', 'ernesto', 'eros', 'esa??', 'esuperio', 'eterie', 'ettore', 'euclide', 'eufebio', 'eufemio', 'eufronio', 'eugenio', 'eusebio', 'euseo', 'eustorgio', 'eustosio', 'eutalio', 'evaldo', 'evandro', 'evaristo', 'evasio', 'everardo', 'evidio', 'evodio', 'evremondo', 'ezechiele', 'ezio', 'fabiano', 'fabio', 'fabrizio', 'famiano', 'fausto', 'fazio', 'fedele', 'federico', 'fedro', 'felice', 'feliciano', 'ferdinando', 'fermiano', 'fermo', 'fernando', 'ferruccio', 'festo', 'fidenziano', 'fidenzio', 'filiberto', 'filippo', 'filomeno', 'fiorenziano', 'fiorenzo', 'flaviano', 'flavio', 'fleano', 'floriano', 'folco', 'fortunato', 'fosco', 'franco', 'francesco', 'frido', 'frontiniano', 'fulberto', 'fulgenzio', 'fulvio', 'furio', 'furseo', 'fuscolo', 'gabino', 'gabriele', 'gaetano', 'gaglioffo', 'gaio', 'galdino', 'galeazzo', 'galileo', 'gallicano', 'gandolfo', 'garimberto', 'gaspare', 'gastone', 'gaudenzio', 'gaudino', 'gautiero', 'gavino', 'gedeone', 'geminiano', 'generoso', 'genesio', 'gennaro', 'gentile', 'genziano', 'gerardo', 'gerasimo', 'geremia', 'gerino', 'germano', 'gerolamo', 'geronimo', 'geronzio', 'gervasio', 'gesualdo', 'gherardo', 'giacinto', 'giacobbe', 'giacomo', 'giadero', 'giambattista', 'gianbattista', 'giancarlo', 'giandomenico', 'gianfranco', 'gianluca', 'gianluigi', 'gianmarco', 'gianmaria', 'gianmario', 'gianni', 'gianpaolo', 'gianpiero', 'gianpietro', 'gianuario', 'giasone', 'gilberto', 'gildo', 'gillo', 'gineto', 'gino', 'gioacchino', 'giobbe', 'gioberto', 'giocondo', 'gioele', 'giona', 'gionata', 'giordano', 'giorgio', 'giosuele', 'giosu??', 'giotto', 'giovanni', 'giove', 'gioventino', 'giovenzio', 'girardo', 'girolamo', 'giuda', 'giuliano', 'giulio', 'giuseppe', 'giustiniano', 'giusto', 'glauco', 'goffredo', 'golia', 'gomberto', 'gondulfo', 'gonerio', 'gonzaga', 'gordiano', 'gosto', 'gottardo', 'graciliano', 'grato', 'graziano', 'gregorio', 'grimaldo', 'gualberto', 'gualtiero', 'guelfo', 'guerrino', 'guglielmo', 'guiberto', 'guido', 'guiscardo', 'gumesindo', 'gustavo', 'iacopo', 'iacopone', 'icaro', 'icilio', 'ido', 'iginio', 'igino', 'ignazio', 'igor', 'ilario', 'ildebrando', 'ildefonso', 'illidio', 'illuminato', 'immacolato', 'indro', 'innocente', 'innocenzo', 'ippocrate', 'ippolito', 'ireneo', 'isacco', 'isaia', 'ischirione', 'iside', 'isidoro', 'italo', 'ivan', 'ivano', 'ivanoe', 'ivo', 'ivone', 'ladislao', 'lamberto', 'lancilotto', 'landolfo', 'lanfranco', 'lapo', 'laurentino', 'lauriano', 'lautone', 'lavinio', 'lazzaro', 'leandro', 'leo', 'leonardo', 'leone', 'leonida', 'leonio', 'leonzio', 'leopardo', 'leopoldo', 'letterio', 'liberato', 'liberatore', 'liberio', 'libero', 'liberto', 'liborio', 'lidio', 'lieto', 'lino', 'lisandro', 'livino', 'livio', 'lodovico', 'loreno', 'lorenzo', 'loris', 'luca', 'luciano', 'lucio', 'ludano', 'ludovico', 'luigi', 'macario', 'maccabeo', 'maffeo', 'maggiorino', 'magno', 'maiorico', 'malco', 'mamante', 'mancio', 'manetto', 'manfredo', 'manilio', 'manlio', 'mansueto', 'manuele', 'marcello', 'marciano', 'marco', 'mariano', 'marino', 'mario', 'marolo', 'martino', 'marzio', 'massimiliano', 'massimo', 'matroniano', 'matteo', 'mattia', 'maurilio', 'maurizio', 'mauro', 'medardo', 'medoro', 'melanio', 'melchiade', 'melchiorre', 'melezio', 'menardo', 'menelao', 'meneo', 'mennone', 'mercurio', 'metello', 'metrofane', 'michelangelo', 'michele', 'milo', 'minervino', 'mirco', 'mirko', 'mirocleto', 'misaele', 'modesto', 'monaldo', 'monitore', 'moreno', 'mos??', 'muziano', 'namazio', 'napoleone', 'narciso', 'narseo', 'narsete', 'natale', 'nazario', 'nazzareno', 'nazzaro', 'neopolo', 'neoterio', 'nereo', 'neri', 'nestore', 'nicarete', 'nicea', 'niceforo', 'niceto', 'nicezio', 'nico', 'nicodemo', 'nicola', 'nicol??', 'niniano', 'nino', 'norberto', 'nostriano', 'no??', 'nunzio', 'oddone', 'oderico', 'odidone', 'odorico', 'olimpio', 'olindo', 'oliviero', 'omar', 'omero', 'onesto', 'onofrio', 'onorino', 'onorio', 'orazio', 'orenzio', 'oreste', 'orfeo', 'orio', 'orlando', 'oronzo', 'orsino', 'orso', 'ortensio', 'oscar', 'osmondo', 'osvaldo', 'otello', 'ottaviano', 'ottavio', 'ottone', 'ovidio', 'paciano', 'pacifico', 'pacomio', 'palatino', 'palladio', 'pammachio', 'pancario', 'pancrazio', 'panfilo', 'pantaleo', 'pantaleone', 'paolo', 'pardo', 'paride', 'parmenio', 'pasquale', 'paterniano', 'patrizio', 'patroclo', 'pauside', 'peleo', 'pellegrino', 'pericle', 'perseo', 'petronio', 'pierangelo', 'piergiorgio', 'pierluigi', 'piermarco', 'piero', 'piersilvio', 'pietro', 'pio', 'pippo', 'placido', 'platone', 'plinio', 'plutarco', 'polidoro', 'polifemo', 'pollione', 'pompeo', 'pomponio', 'ponziano', 'ponzio', 'porfirio', 'porziano', 'postumio', 'prassede', 'priamo', 'primo', 'prisco', 'privato', 'procopio', 'prospero', 'protasio', 'proteo', 'prudenzio', 'publio', 'pupolo', 'pusicio', 'quarto', 'quasimodo', 'querano', 'quintiliano', 'quintilio', 'quintino', 'quinziano', 'quinzio', 'quirino', 'radolfo', 'raffaele', 'raide', 'raimondo', 'rainaldo', 'ramiro', 'raniero', 'ranolfo', 'reginaldo', 'regolo', 'remigio', 'remo', 'remondo', 'renato', 'renzo', 'respicio', 'ricario', 'riccardo', 'richelmo', 'rinaldo', 'rino', 'robaldo', 'roberto', 'rocco', 'rodiano', 'rodolfo', 'rodrigo', 'rolando', 'rolfo', 'romano', 'romeo', 'romero', 'romoaldo', 'romolo', 'romualdo', 'rosario', 'rubiano', 'rufino', 'rufo', 'ruggero', 'ruperto', 'rutilo', 'sabato', 'sabazio', 'sabele', 'sabino', 'saffiro', 'saffo', 'saladino', 'salomone', 'salom??', 'salustio', 'salvatore', 'salvo', 'samuele', 'sandro', 'sansone', 'sante', 'santo', 'sapiente', 'sarbello', 'saturniano', 'saturnino', 'saul', 'saverio', 
	'savino', 'sebastiano', 'secondiano', 'secondo', 'semiramide', 'semplicio', 'sempronio', 'senesio', 'senofonte', 'serafino', 'serapione', 'sergio', 'servidio', 'serviliano', 'sesto', 'settimio', 'settimo', 'severiano', 'severino', 'severo', 'sico', 'sicuro', 'sidonio', 'sigfrido', 'sigismondo', 'silvano', 'silverio', 'silvestro', 'silvio', 'simeone', 'simone', 'sinesio', 'sinfronio', 'sireno', 'siriano', 'siricio', 'siro', 'sisto', 'soccorso', 'socrate', 'solocone', 'sostene', 'sosteneo', 'sostrato', 'spano', 'spartaco', 'speranzio', 'stanislao', 'stefano', 'stiliano', 'stiriaco', 'surano', 'sviturno', 'taddeo', 'taide', 'tammaro', 'tancredi', 'tarcisio', 'tarso', 'taziano', 'tazio', 'telchide', 'telemaco', 'temistocle', 'teobaldo', 'teodoro', 'teodosio', 'teodoto', 'teogene', 'terenzio', 'terzo', 'tesauro', 'tesifonte', 'tibaldo', 'tiberio', 'tiburzio', 'ticone', 'timoteo', 'tirone', 'tito', 'tiziano', 'tizio', 'tobia', 'tolomeo', 'tommaso', 'torquato', 'tosco', 'tranquillo', 'tristano', 'tulliano', 'tullio', 'turi', 'turibio', 'tussio', 'ubaldo', 'ubertino', 'uberto', 'ugo', 'ugolino', 'uguccione', 'ulberto', 'ulderico', 'ulfo', 'ulisse', 'ulpiano', 'ulrico', 'ulstano', 'ultimo', 'umberto', 'umile', 'uranio', 'urbano', 'urdino', 'uriele', 'ursicio', 'ursino', 'ursmaro', 'valente', 'valentino', 'valeriano', 'valerico', 'valerio', 'valfredo', 'valfrido', 'valtena', 'valter', 'varo', 'vasco', 'vedasto', 'velio', 'venanzio', 'venceslao', 'venerando', 'venerio', 'ventura', 'venustiano', 'venusto', 'verano', 'verecondo', 'verenzio', 'verulo', 'vespasiano', 'vezio', 'vidiano', 'vidone', 'vilfredo', 'viliberto', 'vincenzo', 'vindonio', 'vinebaldo', 'vinfrido', 'vinicio', 'virgilio', 'virginio', 'virone', 'viscardo', 'vitale', 'vitalico', 'vito', 'vittore', 'vittoriano', 'vittorio', 'vivaldo', 'viviano', 'vladimiro', 'vodingo', 'volfango', 'vulmaro', 'vulpiano', 'walter', 'zabedeo', 'zaccaria', 'zaccheo', 'zanobi', 'zefiro', 'zena', 'zenaide', 'zenebio', 'zeno', 'zenobio', 'zenone', 'zetico', 'zoilo', 'zosimo']

	try:
		v = visits.get(visits.page=='donne')
		n = v.number + 1
		visits.update(number=n).where(visits.page=='donne').execute()
	except:
		n = 1
		new = visits.create(number=1, page='donne')
		new.save()

	return render_template('donne.html', maleNames=maleNames, n=n)

if __name__ == "__main__":
	app.run(debug=True)
