#!/usr/bin/env python
# coding: utf-8

menu_glowne = ('''Menu główne programu.
    Co chcesz zrobić?
    1. Wyświetlić profil użytkownika.
    2. Wyświetlić listę użytkownika.
    0. Zakończ działanie programu.''')
menu_lista = '''Co chcesz wyświetlić: 
    1. Aktualnie oglądane. 
    2. Obejrzane serie. 
    3. Wstrzymane.
    4. Planowane.  
    5. Porzucone.
    6. Wszystkie.
    7. Wróć do menu głównego.
    0. Zakończ działanie programu.'''
import requests
import matplotlib.pyplot as plt

def czas(czas):
    return round(czas/24/60, 1)

def plotHistogram(x_axis, y_axis, title=""):
    plt.bar(x_axis, y_axis)
    plt.xlim([min(x_axis), max(x_axis)])
    plt.title(title)
    plt.grid()       
    plt.xlabel("Oceny")
    plt.ylabel("Ilość ocenionych")
    plt.show() 

def menu(menu_string = ''): 
    stop = 1
    while stop != 0:
        print(menu_string)
        try:
            wybor = int(input())
            break
        except ValueError:
            print('Nie podałes liczby! Spróbuj jeszcze raz')
            print(menu_string)
            wybor = input()
        stop = 0
    return wybor

def user(user_name = '', menu_glowne_wybor = 0):
    query = '''
query($search: String){
    User(name: $search){
        id
        name
        avatar{
            large
            medium
        }
        siteUrl
        stats{
            watchedTime
            animeListScores{
                meanScore
            }
            animeScoreDistribution{
                score
                amount
            } 
            favouredGenres{
                genre
                amount
                meanScore
                timeWatched
            }
   }
    }
    }

'''
    variables = {
    'search': user_name
}
    
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    try: 
        response.json()['data']['User']['id']
    except TypeError:
        print('Brak użytkownika w bazie!')
        return None
    tab = []
    tab2 = []
    ilosc_anime = 0
    if menu_glowne_wybor == 1:
        print("\nNazwa użytownika: " + user_name + " id użytkownika " + str(response.json()['data']['User']['id']))
        print("Link do avatara: " + response.json()['data']['User']['avatar']['large'])
        print("Link do profilu: " + response.json()['data']['User']['siteUrl'])
        if response.json()['data']['User']['stats']['animeScoreDistribution'] == []:
            print("Użytkownik nie ocenił swoich tytułów")
        else:
            for i in range(0, len(response.json()['data']['User']['stats']['animeScoreDistribution'])):
                tab.append(response.json()['data']['User']['stats']['animeScoreDistribution'][i]['amount'])
                tab2.append((response.json()['data']['User']['stats']['animeScoreDistribution'][i]['score']))
                ilosc_anime += response.json()['data']['User']['stats']['animeScoreDistribution'][i]['amount']
            plotHistogram(tab2, tab, "Ilość anime według oceny")
            print("Ilość ocenionych anime: " + str(ilosc_anime))
            print("Łączny czas oglądania: " + str(czas(response.json()['data']['User']['stats']['watchedTime'])) + " dni")
            print("Średnia ocena: " + str(response.json()['data']['User']['stats']['animeListScores']['meanScore']/10))
            print("\nTop 5 ulubionych gatunków: ")
            print("|     Gatunek       |  Liczba  |  Średnia ocena  | Czas oglądania w dniach | ")
            for i in range(0,5):
                print(response.json()['data']['User']['stats']['favouredGenres'][i]['genre'].center(18)  +
                      (str(response.json()['data']['User']['stats']['favouredGenres'][i]['amount'])).center(15) +
                      (str(response.json()['data']['User']['stats']['favouredGenres'][i]['meanScore']/10)).center(20) +
                      (str(czas(response.json()['data']['User']['stats']['favouredGenres'][i]['timeWatched'])).center(15))                 
                         )
    if menu_glowne_wybor == 2:
        try: 
            return response.json()['data']['User']['id']
        except TypeError:
            return None

def wyswietl_liste(status, id_user = int):
    if id_user == None:
        print('Brak tytułów na liście!')
        zakoncz = 0
        return zakoncz
    else:
        status_dic = {1 : 'CURRENT', 
                      2 : 'COMPLETED', 
                      3: 'PLANNING', 
                      4 : 'PAUSED', 
                      5: 'DROPPED' }
        query = '''
query ($id_user: Int) {
  MediaListCollection(userId: $id_user, type: ANIME) {
    lists {
      entries {
        id
        status
        score
        progress
        customLists
        media {
          id
          title {
            romaji
          }
          format
          status
          episodes
          duration
          coverImage {
            large
          }          
          nextAiringEpisode {
            airingAt
            episode
          }
         
        }
      }
    }
  }
}
'''
    variables = {
        'id_user': id_user
    }
    i=0
    url = 'https://graphql.anilist.co'
    
    response = requests.post(url, json={'query': query, 'variables': variables})
    sentence = str(response.json())
    import re
    ile = len(re.findall('(?=entries)', sentence))
    f22 = open("aaaa.txt","w", encoding="utf8")
    f22.write(str(response.json()['data']['MediaListCollection']))
    f22.close()
    if(status < 6):
        x = 0
        for i in range(0, ile):
            slownik = response.json()['data']['MediaListCollection']['lists'][i]['entries']
            for j in range(0, len(slownik)):
                if slownik[j]['status'] == status_dic[status]:
                    x += 1
                    print(str(x) + " Tytuł: " + slownik[j]['media']['title']['romaji'] + "\tOcena: " + str(slownik[j]['score']) + 
                    "\t Postęp: " + str(slownik[j]['progress']) + "/" + str(slownik[j]['media']['episodes']) +
                    "\tFormat: "  + slownik[j]['media']['format']
                    + "\n" )
    if(status == 6):
        x = 0
        for k in range(1,6):
            print((status_dic[k]))
            for i in range(0, ile):
                slownik = response.json()['data']['MediaListCollection']['lists'][i]['entries']
                for j in range(0, len(slownik)):
                    if slownik[j]['status'] == status_dic[k]:
                        x += 1
                        print(str(x) + " Tytuł: " + slownik[j]['media']['title']['romaji'] + "\tOcena: " + str(slownik[j]['score']) + 
                        "\t Postęp: " + str(slownik[j]['progress']) + "/" + str(slownik[j]['media']['episodes']) +
                        "\tFormat: "  + slownik[j]['media']['format']
                        + "\n" )
    if status == 7:
        return 

def program():
    zakoncz = True
    while zakoncz != 0:
        zakoncz = menu(menu_glowne)
        if zakoncz == 1:
            print('Podaj nazwe użytkownika: ')
            user_name = input()
            user(user_name, zakoncz)
        if zakoncz == 2:
            print('Podaj nazwe użytkownika: ')
            user_name = input()
            x = user(user_name, zakoncz)
            if x != None:
                lista = menu(menu_lista)
                if lista == 0:
                    return 
                if lista > 7:
                    print("Podales bledna wartosc. Powrot do menu glownego!")
                else:
                    wyswietl_liste(lista, x)
        if int(zakoncz) > 2 or int(zakoncz) < 0:
            print("Podaj własciwą wartosc!")
    return 

if __name__ == "__main__":
    # Uruchom program
    program()



