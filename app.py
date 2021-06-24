# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import peewee, os, hmac, time, uuid
from hashlib import sha256
from flask_socketio import SocketIO, send, emit
from random import randint, uniform
from load_config import get_config_file

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
    #I import the huge json file with all male names with the support function in load_config.py
    config = get_config_file(maleNames.json)
    maleNames = config["maleNames"].split(";")
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
