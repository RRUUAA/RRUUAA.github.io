from flask import Flask, request
from flask_cors import CORS
import os
# app = Flask(__name__, static_url_path='', static_folder='static', template_folder='tmpl')
app = Flask(__name__)
CORS(app)
import requests
import json

my_apikey = 'api_key=764273b6d412996c9e6a81f06d338ed3'

def trending_parser(d):
    d = json.loads(d)
    response = {'results': []}
    for result in d['results']:
        response['results'].append({
            'title' : result['title'],
            'backdrop_path': result['backdrop_path'],
            'release_date' : result['release_date'],
        })
        if len(response['results']) == 5:
            break
    response = json.dumps(response)
    return response

def airing_today_parser(d):
    d = json.loads(d)
    response = {'results': []}
    for result in d['results']:
        response['results'].append({
            'title' : result['name'],
            'backdrop_path': result['backdrop_path'],
            'release_date' : result['first_air_date'],
        })
        if len(response['results']) == 5:
            break
    response = json.dumps(response)
    return response

def movie_tv_parser(d):
    response = {'results': []}

    for result in d['results']:
        print(result)
        id = ""
        title = ""
        overview = ""
        release_date = ""
        vote_average = ""
        vote_count = ""
        genre_ids = ""
        type = ''

        if 'id' in result:
            id = str(result['id'])
        if 'title' in result:
            title = result['title']
            type = 'movie'
        elif 'name' in result:
            title = result['name']
            type = 'tv'
        if 'runtime' in result:
            runtime = result['runtime']
        if 'spoken_languages' in result:
            spoken_languages = result['spoken_languages']
        if 'overview' in result:
            overview = result['overview']
        if 'release_date' in result:
            release_date = result['release_date']
        elif 'first_air_date' in result:
            release_date = result['first_air_date']
        if 'vote_average' in result:
            vote_average = result['vote_average']
        if 'vote_count' in result:
            vote_count = result['vote_count']
        if 'genre_ids' in result:
            genre_ids = result['genre_ids']

        url = 'https://www.themoviedb.org/' + type + '/' + str(id)

        thisdir = {
            'id': id,
            'title': title,
            'overview': overview,
            'release_date': release_date,
            'vote_average': vote_average / 2,
            'vote_count': vote_count,
            'genre_ids': genre_ids,
            'type': type,
            'url': url
        }
        if 'poster_path' in result:
            thisdir['poster_path'] = result['poster_path']
        response['results'].append(thisdir)
        if len(response['results']) == 10:
            break
    return response

def get_genredic():
    if os.path.exists('static/all_id.txt'):
        return
    else:
        mv_text = requests.get('https://api.themoviedb.org/3/genre/movie/list?api_key=764273b6d412996c9e6a81f06d338ed3&language=en-US').text
        tv_text = requests.get('https://api.themoviedb.org/3/genre/tv/list?api_key=764273b6d412996c9e6a81f06d338ed3&language=en-US').text

        mv_json = json.loads(mv_text)
        tv_json = json.loads(tv_text)

        all_json = {}
        for genre in mv_json['genres']:
            all_json[genre['id']] = genre['name']
        for genre in tv_json['genres']:
            all_json[genre['id']] = genre['name']
        with open('static/all_id.txt','w',encoding='utf-8') as f:
            json.dump(all_json,f)

@app.route('/')
def root():
    get_genredic()
    return app.send_static_file('new.html')

@app.route('/trending')
def trending():
    d = requests.get('https://api.themoviedb.org/3/trending/movie/week?api_key=764273b6d412996c9e6a81f06d338ed3').text
    response = trending_parser(d)
    return response

@app.route('/airing_today')
def airing_today():
    d = requests.get('https://api.themoviedb.org/3/tv/airing_today?api_key=764273b6d412996c9e6a81f06d338ed3').text
    response = airing_today_parser(d)
    return response

@app.route('/search', methods = ['GET'])
def upload_data():
    response = ''
    # print(str(request.args.get("Keyword")))
    # print(str(request.args.get("Category")))
    with open('static/all_id.txt','r',encoding='utf-8') as f:
        genre_dic = json.load(f)


    if request.args.get('Keyword')!=None and request.args.get('Category')!= None:
        keyword = str(request.args.get('Keyword'))
        category = str(request.args.get('Category'))
        keyword = keyword.replace(' ','%20')
        if category == 'Movies':
            category = 'movie?'
        elif category == 'TV Shows':
            category = 'tv?'
        else:
            category = 'multi?'

        api = 'https://api.themoviedb.org/3/search/' + category + my_apikey + '&language=en-US&query=' + keyword + '&page=1&include_adult=false'
        d = requests.get(api).text
        d = json.loads(d)
        d = movie_tv_parser(d)

        i = 0
        for result in d['results']:
            if i > 9:
                break
            i += 1
            for num in range(0,len(result['genre_ids'])):
                id = result['genre_ids'][num]
                result['genre_ids'][num] = genre_dic[str(id)]
            head = 'https://api.themoviedb.org/3/' + result['type'] + '/' + result['id']
            # detail_api = "https://api.themoviedb.org/3/tv/1399?api_key=764273b6d412996c9e6a81f06d338ed3&language=en-US"
            detail_api = head+ '?' + my_apikey + '&language=en-US'
            # credit_api = 'https://api.themoviedb.org/3/tv/1399/credits?api_key=97588ddc4a26e3091152aa0c9a40de22&language=en-US'
            credit_api = head + '/credits?' + my_apikey + '&language=en-US'
            # review_api = 'https://api.themoviedb.org/3/tv/1399/reviews?api_key=97588ddc4a26e3091152aa0c9a40de22&language=en-US&page=1'
            review_api = head + '/reviews?' + my_apikey + '&language=en-USpage=1'

            detail = json.loads(requests.get(detail_api).text)
            result['backdrop_path'] = detail['backdrop_path']
            if 'runtime' in detail:
                result['runtime'] = detail['runtime']
            else:
                result['runtime'] = detail['episode_run_time']
            if 'number_of_seasons' in detail:
                result['number_of_seasons'] = detail['number_of_seasons']
            if detail['spoken_languages']:
                result['spoken_languages'] = detail['spoken_languages'][0]['name']
            else:
                result['spoken_languages'] = ''

            credit = json.loads(requests.get(credit_api).text)
            if len(credit['cast']) > 7:
                result['cast'] = credit['cast'][:8]
            else:
                result['cast'] = credit['cast']

            review = json.loads(requests.get(review_api).text)
            result['review'] = []
            for j in range(0,len(review['results'])):
                if j > 4:
                    break
                thisone = review['results'][j]
                if review['results'][j]['author_details']['rating']:
                    thisone['author_details']['rating'] = review['results'][j]['author_details']['rating']/2
                timestr = review['results'][j]['created_at'][0:9]
                timedir = {
                    'year':timestr.split('-')[0],
                    'month': timestr.split('-')[1],
                    'day': timestr.split('-')[2]
                }
                thisone['created_at']  =timedir
                result['review'].append(thisone)
                print("This is review!!!!!!!!!!")

        response = json.dumps(d)
        print("This is response", response)
    return response

# @app.route('/tutor', methods = ['GET'])
# def turn_page():
#     response = ''
#     # print(str(request.args.get("Keyword")))
#     # print(str(request.args.get("Category")))
#     api = 'http://127.0.0.1:5000/'
#     if request.args.get('Id')!=None and request.args.get('Category')!= None:
#         id = str(request.args.get('Id'))
#         category = str(request.args.get('Category'))
#         api = 'https://www.themoviedb.org/' + category + '/' + id
#         print(api)
#
#     return redirect(api)

if __name__ == '__main__':
    app.run()