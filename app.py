from flask import Flask, request, jsonify
import random
import matplotlib.pyplot as plt
import io
import base64
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

def poblacion_inicial(max_poblacion, num_vars):
    poblacion = []
    for i in range(max_poblacion):
        gen = [] 
        for j in range(num_vars):
            if random.random() > 0.5:
                gen.append(1)
            else:
                gen.append(0)
        poblacion.append(gen[:])
    return poblacion

def adaptacion_3sat(gen, solucion):
    n = 3
    cont = 0
    clausula_ok = True
    for i in range(len(gen)):
        n = n - 1
        if gen[i] != solucion[i]:
            clausula_ok = False
        if n == 0:
            if clausula_ok:
                cont = cont + 1
            n = 3
            clausula_ok = True
        if n > 0:
            if clausula_ok:
                cont = cont + 1
    return cont

def evalua_poblacion(poblacion, solucion):
    adaptacion = []
    for i in range(len(poblacion)):
        adaptacion.append(adaptacion_3sat(poblacion[i], solucion))
    return adaptacion

def seleccion(poblacion, solucion):
    adaptacion = evalua_poblacion(poblacion, solucion)
    total = 0
    for i in range(len(adaptacion)):
        total = total + adaptacion[i]
    val1 = random.randint(0, total)
    val2 = random.randint(0, total)
    sum_sel = 0
    for i in range(len(adaptacion)):
        sum_sel = sum_sel + adaptacion[i]
        if sum_sel >= val1:
            gen1 = poblacion[i]
            break
    sum_sel = 0
    for i in range(len(adaptacion)):
        sum_sel = sum_sel + adaptacion[i]
        if sum_sel >= val2:
            gen2 = poblacion[i]
            break
    return gen1, gen2

def cruce(gen1, gen2):
    nuevo_gen1 = []
    nuevo_gen2 = []
    corte = random.randint(0, len(gen1))
    nuevo_gen1[0:corte] = gen1[0:corte]
    nuevo_gen1[corte:] = gen2[corte:]
    nuevo_gen2[0:corte] = gen2[0:corte]
    nuevo_gen2[corte:] = gen1[corte:]
    return nuevo_gen1, nuevo_gen2

def mutacion(prob, gen):
    if random.random() < prob:
        cromosoma = random.randint(0, len(gen) - 1)
        if gen[cromosoma] == 0:
            gen[cromosoma] = 1
        else:
            gen[cromosoma] = 0
    return gen

def elimina_peores_genes(poblacion, solucion):
    adaptacion = evalua_poblacion(poblacion, solucion)
    i = adaptacion.index(min(adaptacion))
    del poblacion[i]
    del adaptacion[i]
    i = adaptacion.index(min(adaptacion))
    del poblacion[i]
    del adaptacion[i]

def mejor_gen(poblacion, solucion):
    adaptacion = evalua_poblacion(poblacion, solucion)
    return poblacion[adaptacion.index(max(adaptacion))]

@app.route('/solve', methods=['POST'])
def solve():
    datos = request.json
    num_vars = int(datos["num_vars"])
    max_poblacion = int(datos["max_poblacion"])
    max_iter = int(datos["max_iter"])
    solucion = poblacion_inicial(1, num_vars)[0]
    poblacion = poblacion_inicial(max_poblacion, num_vars)
    adaptacion_historia = []
    iteraciones = 0
    while iteraciones < max_iter:
        iteraciones = iteraciones + 1
        adaptacion = evalua_poblacion(poblacion, solucion)
        adaptacion_historia.append(max(adaptacion))
        for i in range(len(poblacion) // 2):
            gen1, gen2 = seleccion(poblacion, solucion)
            nuevo_gen1, nuevo_gen2 = cruce(gen1, gen2)
            nuevo_gen1 = mutacion(0.1, nuevo_gen1)
            nuevo_gen2 = mutacion(0.1, nuevo_gen2)
            poblacion.append(nuevo_gen1)
            poblacion.append(nuevo_gen2)
            elimina_peores_genes(poblacion, solucion)
        if max_iter < iteraciones:
            fin = True
    plt.plot(range(1, iteraciones + 1), adaptacion_historia, marker='o')
    plt.title('Evolución de la Adaptación')
    plt.xlabel('Iteración')
    plt.ylabel('Adaptación')
    plt.grid(False)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.read()).decode()
    mejor_gen_resultado = mejor_gen(poblacion, solucion)
    return jsonify({
        "Mejor gen encontrado": mejor_gen_resultado,
        "Funcion de adaptacion": adaptacion_historia[-1],
        "grafica_url": f"data:image/png;base64,{imagen_base64}"
    })

if __name__ == '__main__':
    app.run()
