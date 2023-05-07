import math
import random


tiempo = 0
tiempo_final = 7 * 24 * 60  # 7 dias en minutos
hora_inicio = 6
hora_fin = 16
tiempo_limite_rechazo = 0
condicion_rechazo = 10 * 60  # 10 horas trabajadas
cantidad_bandejas_maquina_1 = 6
cantidad_bandejas_maquina_2 = 6
cota_superior_semana = 0.16
cota_superior_sabado = 0.21
kappa_semana = -0.93432
sigma_semana = 10.726
mu_semana = 4.7681
kappa_sabado = -0.18729
sigma_sabado = 2.5903
mu_sabado = 18.997
ta_galletita = 10 #min
ta_pre_pizza = 15 #min
ta_facturas = 20 #min
ta_panes = 25 #min
factor_horno_1 = 1 # si es nuevo es 0,9 si es viejo es 1
factor_horno_2 = 1 # si es nuevo es 0,9 si es viejo es 1
vector_tiempo_comprometido_maquina_1 = [0 for _ in range(cantidad_bandejas_maquina_1)]
vector_tiempo_comprometido_maquina_2 = [0 for _ in range(cantidad_bandejas_maquina_2)]
def obtener_dia_de_semana(tiempo):
    """
    Tomamos el numero entero para saber que dia de la semana es (de 0 a 6)
    :param tiempo:
    :return:
    """
    return int(tiempo/60/24)

def es_antes_del_horario_de_apertura(tiempo):
    """
    Chequeamos que el horario sea antes del definido en hora_inicio
    :param tiempo:
    :return:
    """
    return (tiempo/60)%24 < hora_inicio


def esta_cerrada_la_panaderia(dia_semana):
    """
    La panaderia cierra lunes y domingos
    :param dia_semana:
    :return:
    """
    return dia_semana % 7 == 0 or dia_semana % 7 == 6


def es_sabado(dia_semana):
    """
    Los sabados tenemos comportamientos distintos
    :param dia_semana:
    :return:
    """
    return dia_semana % 7 == 5

def fda_dia_semana(dominio):
    """
    Cuando es dia de semana se tiene una fdp diferente
    :return:
    """
    partial_fdp = (1 + kappa_semana * ((dominio - mu_semana) / sigma_semana))
    return (1/sigma_semana) * (partial_fdp ** (-1 - (1 / kappa_semana)))


def intervalo_arribo_semana():
    while(True):
        random_number = random.uniform(0, 1)
        dominio_inferior = mu_semana
        dominio_superior = mu_semana - (sigma_semana / kappa_semana)
        dominio = random.uniform(dominio_inferior, dominio_superior)
        imagen = cota_superior_semana * random_number
        if imagen < fda_dia_semana(dominio):
            return dominio

def fda_dia_sabado(dominio):
    """
    Cuando es dia de semana se tiene una fdp diferente
    :return:
    """
    z = (dominio - mu_sabado)/ sigma_sabado
    inv_sigma = 1/sigma_sabado
    termino_aux_1 = -(1+kappa_semana*z)**(-1/kappa_sabado)
    termino_exp = math.exp(termino_aux_1)
    termino_adicional = (1+kappa_sabado*z)**(-1-(1/kappa_sabado))
    return inv_sigma * termino_exp * termino_adicional


def intervalo_arribo_sabado():
    while(True):
        random_number = random.uniform(0, 1)
        dominio_inferior = 0
        dominio_superior = -(sigma_sabado/kappa_sabado+mu_sabado)
        dominio = random.uniform(dominio_inferior, dominio_superior)
        imagen = cota_superior_sabado * random_number
        if imagen < fda_dia_semana(dominio):
            return dominio


def indice_bandeja_con_menor_tc_horno_1():
    indice_min = 0
    valor_min = vector_tiempo_comprometido_maquina_1[0]
    for i in range(1, len(vector_tiempo_comprometido_maquina_1)):
        if vector_tiempo_comprometido_maquina_1[i] < valor_min:
            valor_min = vector_tiempo_comprometido_maquina_1[i]
            indice_min = i
    return indice_min


def indice_bandeja_con_menor_tc_horno_2():
    indice_min = 0
    valor_min = vector_tiempo_comprometido_maquina_2[0]
    for i in range(1, len(vector_tiempo_comprometido_maquina_2)):
        if vector_tiempo_comprometido_maquina_2[i] < valor_min:
            valor_min = vector_tiempo_comprometido_maquina_2[i]
            indice_min = i
    return indice_min


def seleccionar_tiempo_atencion_horno_1():
    numero_random = random.uniform(0, 1)
    if numero_random < 0.1:
        return ta_galletita * factor_horno_1
    if numero_random < 0.25:
        return ta_pre_pizza * factor_horno_1
    if numero_random < 0.6:
        return ta_facturas * factor_horno_1
    return ta_panes * factor_horno_1


def seleccionar_tiempo_atencion_horno_2():
    numero_random = random.uniform(0, 1)
    if numero_random < 0.1:
        return ta_galletita * factor_horno_2
    if numero_random < 0.25:
        return ta_pre_pizza * factor_horno_2
    if numero_random < 0.6:
        return ta_facturas * factor_horno_2
    return ta_panes * factor_horno_2


def el_pedido_termina_antes_del_cierre(tiempo, tiempo_atencion):
    return (((tiempo+tiempo_atencion)/60) % 24) < hora_fin


def main():
    global tiempo
    global vector_tiempo_comprometido_maquina_1
    global vector_tiempo_comprometido_maquina_2
    tiempo_proxima_llegada = (24+hora_inicio)*60
    cantidad_rechazados = 0
    bandejas_horneadas = 0
    sumatoria_tiempo_ocioso = 0
    sumatoria_tiempo_espera = 0
    tiempo_atencion = 0
    while(True):
        es_horno_uno = False
        tiempo = tiempo_proxima_llegada
        dia_semana = obtener_dia_de_semana(tiempo)
        if not es_antes_del_horario_de_apertura(tiempo):
            tiempo_proxima_llegada = dia_semana * 24 * 60 + hora_inicio
        if esta_cerrada_la_panaderia(dia_semana):
            continue
        intervalo_arribos = intervalo_arribo_sabado() if es_sabado(dia_semana) else intervalo_arribo_semana()
        tiempo_proxima_llegada = intervalo_arribos + tiempo
        indice_horno_1 = indice_bandeja_con_menor_tc_horno_1()
        indice_horno_2 = indice_bandeja_con_menor_tc_horno_2()
        if vector_tiempo_comprometido_maquina_2[indice_horno_2] < vector_tiempo_comprometido_maquina_1[indice_horno_1]:
            """
            usamos horno 2
            """
            tiempo_atencion = seleccionar_tiempo_atencion_horno_2()
            es_horno_uno = False
        else:
            """
            Usamos horno 1
            """
            tiempo_atencion = seleccionar_tiempo_atencion_horno_1()
            es_horno_uno = True

        if not el_pedido_termina_antes_del_cierre(tiempo, tiempo_atencion):
            """
            como no temrino en el dia, lo rechazo
            """
            cantidad_rechazados = cantidad_rechazados + 1
        else:
            """
            tomo el pedido del horneado por que se procesa en el dia
            """
            bandejas_horneadas = bandejas_horneadas + 1
            if (es_horno_uno):
                """
                Trabajamos con el horno 1 por tener el menor tiempo comprometido
                """
                if tiempo > vector_tiempo_comprometido_maquina_1[indice_horno_1]:
                    sumatoria_tiempo_ocioso = sumatoria_tiempo_ocioso + (tiempo - vector_tiempo_comprometido_maquina_1[indice_horno_1])
                    vector_tiempo_comprometido_maquina_1[indice_horno_1] = tiempo + tiempo_atencion
                else:
                    sumatoria_tiempo_espera = sumatoria_tiempo_espera + vector_tiempo_comprometido_maquina_1[indice_horno_1] - tiempo
                    vector_tiempo_comprometido_maquina_1[indice_horno_1] = tiempo + tiempo_atencion
            else:
                """
                Trabajamos con el horno 2 que tiene menor tiempo comprometido
                """
                if tiempo > vector_tiempo_comprometido_maquina_2[indice_horno_2]:
                    sumatoria_tiempo_ocioso = sumatoria_tiempo_ocioso + (tiempo - vector_tiempo_comprometido_maquina_2[indice_horno_2])
                    vector_tiempo_comprometido_maquina_2[indice_horno_2] = tiempo + tiempo_atencion
                else:
                    sumatoria_tiempo_espera = sumatoria_tiempo_espera + vector_tiempo_comprometido_maquina_2[indice_horno_2] - tiempo
                    vector_tiempo_comprometido_maquina_2[indice_horno_2] = tiempo + tiempo_atencion

        if not tiempo > tiempo_final:
            """
            Aun no termina la simulacion sigo con el proximo evento 
            """
            continue
        else:
            """
            Finalizo la simulacion
            """
            promedio_tiempo_ocioso = sumatoria_tiempo_ocioso / tiempo
            promedio_tiempo_espera = sumatoria_tiempo_espera / bandejas_horneadas
            promedio_arrepentidos = (cantidad_rechazados / bandejas_horneadas) * 100
            print(f'promedio_tiempo_ocioso = {promedio_tiempo_ocioso}')
            print(f'promedio_tiempo_espera = {promedio_tiempo_espera}')
            print(f'promedio_arrepentidos = {promedio_arrepentidos}')
            return

if __name__ == '__main__':
    print("iniciando_script")
    main()
