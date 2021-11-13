import requests
import json
import pprint
import urllib.parse
from datetime import date

# Chave para acessar a API no AccuWeather
accuweatherAPIKey = "403GcBO1m2nhXAvRBTslhhYHh7WJKzk4"
# Token para acessar a API no Mapbox
mapboxToken = "pk.eyJ1IjoibWFsZWdvcGMiLCJhIjoiY2s5b2RqdDBwMGJsbzNvbWVsN3diZDVteSJ9.CNGokNZxDeUM8Xmg4CGQtw"

dias_semana = ['Domingo', 'Segunda-feira','Terça-feira','Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado']

def pegarCoordenadas(): 
    # chama/requisita a api de geolocalização  - latitude/longitude pelo número do ip
    r = requests.get('http://www.geoplugin.net/json.gp')

    if (r.status_code != 200):
        print('Não foi possível obter a localização.') # verificação se a requisição deu certo
        return(None)
    else:
        try:
            #print(type(json.loads(r.text))) # usa json para mostrar o que é tipo "dicionário" ou "lista"
            localizacao = json.loads(r.text)
            #print(pprint.pprint(localizacao))
            coordenadas = {} #dicionário vazio (objeto no JavaScript)
            coordenadas['lat'] = localizacao['geoplugin_latitude']
            coordenadas['long'] = localizacao['geoplugin_longitude']
            #print('lat: ',coordenadas['lat'])
            #print('long: ',coordenadas['long'])
            return(coordenadas)
        except:
            return(None)

def pegarCoordenadas2(nomeLocal): 
    nomeLocal = urllib.parse.quote(nomeLocal) #converte caracteres especiais
    # chama/requisita a api de geolocalização do Mapbox - latitude/longitude pelo nome do local
    r = requests.get('https://api.mapbox.com/geocoding/v5/mapbox.places/' + nomeLocal + '.json?access_token=' + mapboxToken)

    if (r.status_code != 200):
        print('Não foi possível obter a geolocalização.') # verificação se a requisição deu certo
        return(None)
    else:
        try:
            #print(type(json.loads(r.text))) # usa json para mostrar o que é tipo "dicionário" ou "lista"
            localizacao = json.loads(r.text)
            #print(pprint.pprint(localizacao))
            coordenadas = {} #dicionário vazio (objeto no JavaScript)
            coordenadas['lat'] = str(localizacao['features'][0]['geometry']['coordinates'][1])
            coordenadas['long'] = str(localizacao['features'][0]['geometry']['coordinates'][0]) #invertido lat e long no Mapbox
            #print('lat: ',coordenadas['lat'])
            #print('long: ',coordenadas['long'])
            return(coordenadas)
        except:
            return(None)

def pegarCodigoLocal(lat,long):
    # AccuWeather trabalha com número de localização da região que é obtido com a API abaixo, dadas latitute e longitude
    LocationAPIUrl = "http://dataservice.accuweather.com/locations/v1/" \
    + "cities/geoposition/search?apikey=" + accuweatherAPIKey \
    + "&q=" + lat + "%2C" + long + "&language=pt-br"

    r = requests.get(LocationAPIUrl)       
    if (r.status_code != 200):
        print('Não foi possível obter o código do local.')
        return(None)
    else:
        try:
            locationResponse = json.loads(r.text)
            infoLocal = {} #dicionário (objeto em JavaScript)
            infoLocal['nomeLocal'] = locationResponse['LocalizedName'] + ", " \
                        + locationResponse['AdministrativeArea']['LocalizedName'] + ". " \
                        + locationResponse['Country']['LocalizedName']
            infoLocal['codigoLocal'] = locationResponse['Key']
            #print("Obtendo clima do local: ", infoLocal['nomeLocal'])
            #print("Código do Local: ", infoLocal['codigoLocal'])
            return(infoLocal)
        except:
            return(None)

def pegarTempoAgora(codigoLocal, nomeLocal):
    # fornece as condições correntes do clima pelo codigo do local
    CurrentConditionsAPIUrl = "http://dataservice.accuweather.com/currentconditions/v1/" \
                              + codigoLocal + "?apikey=" + accuweatherAPIKey \
                              + "&language=pt-br"
    r = requests.get(CurrentConditionsAPIUrl)
    if (r.status_code != 200):
        print('Não foi possível obter o clima atual.')
        return(None)
    else:
        try:
            CurrentConditionsResponse = json.loads(r.text)
            #print(pprint.pprint(CurrentConditionsResponse))
            #trata-se nesse caso de uma lista (e não dicionário como os anteriores)
            infoClima = {} #dicionário (objeto em JavaScript)
            infoClima['textoClima'] = CurrentConditionsResponse[0]['WeatherText']
            infoClima['temperatura'] = CurrentConditionsResponse[0]['Temperature']['Metric']['Value']
            infoClima['nomeLocal'] = nomeLocal
            #print('Clima no momento: ', infoClima['textoClima'])
            #print('Temperatura: ' + str(infoClima['temperatura']) + " graus Celsius")
            return(infoClima)
        except:
            return(None)
        
def pegarPrevisao5dias(codigoLocal):
    # fornece a previsão para 5 dias
    DailyAPIUrl = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/" \
                              + codigoLocal + "?apikey=" + accuweatherAPIKey \
                              + "&language=pt-br&metric=true"
    r = requests.get(DailyAPIUrl)
    if (r.status_code != 200):
        print('Não foi possível obter a previsão para 5 dias.')
        return(None)
    else:
        try:
            DailyResponse = json.loads(r.text)                  
            info5days = [] #lista
            for dia in DailyResponse['DailyForecasts']:
                climaDia = {}
                climaDia['max'] = dia['Temperature']['Maximum']['Value']
                climaDia['min'] = dia['Temperature']['Minimum']['Value']
                climaDia['clima'] = dia['Day']['IconPhrase']
                diaSemana = int(date.fromtimestamp(dia['EpochDate']).strftime("%w"))
                climaDia['dia'] = dias_semana[diaSemana]
                #climaDia['dia'] = dia['EpochDate']
                info5days.append(climaDia)                                    
            return(info5days)
        except:
            return(None)

def mostrarPrevisao(lat,long):
    flag = 1
    try:
        local = pegarCodigoLocal(lat,long)
        climaAtual = pegarTempoAgora(local['codigoLocal'], local['nomeLocal'])
        print('\nClima atual em: ' + climaAtual['nomeLocal'])
        print(climaAtual['textoClima'])
        print('Temperatura: ' + str(climaAtual['temperatura']) + "\xb0" + "C")
    except:
        print('Erro ao obter o clima atual.')
        flag = 0
    if flag != 0:
        Opcao = input("\nDeseja ver a previsão para os próximos dias? (S|N)")
        if Opcao.upper() != 'N': 
            print('\nClima para hoje e para os próximos dias:\n')
            try:
                previsao5dias = pegarPrevisao5dias(local['codigoLocal'])
                #print(pprint.pprint(previsao5dias))
                for dia in previsao5dias:
                    print(dia['dia'])
                    print('Mínima: ' + str(dia['min']) + "\xb0" + "C")
                    print('Máxima: ' + str(dia['max']) + "\xb0" + "C")
                    print('Clima: ' + dia['clima'])
                    print('------------------')
            except:
                print('Erro ao obter a previsão para os próximos dias.') 

# Início do Programa

try:
    coordenadas = pegarCoordenadas()
           
    Opcao = 's' 
    while Opcao.upper() != 'N':
        mostrarPrevisao(coordenadas['lat'],coordenadas['long'])
        Opcao = input("\nDeseja consultar a previsão para outro local? (S|N)")
        if Opcao.upper() != 'N':
            nomeLocal = input("\nDigite o nome do local: ")
            coordenadas = pegarCoordenadas2(nomeLocal)               
        else:
            print("Fim do programa.")    
except:
    print('Erro ao processar a solicitação. Entre em contato com o suporte.')
    



