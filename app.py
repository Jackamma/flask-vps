from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def home():
	return render_template('index.html')

@app.route("/ippodromo/")
def ippo():
	# Aggiungere verifica hash telegram
	first_name = request.args.get('first_name')
	return render_template('ippo.html', first_name=first_name)

@app.route("/donne/")
def donne():
	donna = request.args.get('donna')
	result = False
	if donna:
		result = donna + ' è troia'
	return render_template('donne.html', result=result)

# @app.route("/donne/<nome>")
# def donneResponse(nome):
# 	testo = False
# 	if nome:
# 		testo = nome + ' è troia'
# 	return render_template('donne.html', result=testo)

if __name__ == "__main__":
	app.run(debug=True)