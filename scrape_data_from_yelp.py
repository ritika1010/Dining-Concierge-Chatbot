import requests
import json



locations = ['Manhattan']
cuisines = ['Chinese', 'Italian', 'French', 'Mexican', 'Thai', 'Indian', 'Indonesian', 'Irish', 'Halal', 'Himalayan', 'Greek', 'Hungarian', 'International', 'Malaysian', 'Mediterranean', 'Georgian',
'German', 'French Southwest',
'Galician', 'Cuban'
'Curry Sausage',
'Cypriot',
'Czech',
'Czech/Slovakian',
'Danish',
'Delis',
'Cafeteria',
'Cajun/Creole',
'Cambodian',
'Canadian (New)',
'Canteen',
'Caribbean',
'British',
'Buffets',
'Bulgarian',
'Burgers',
'Burmese',
'Cafes']
file_path = "final.json"

def search_yelp(api_key, location, cuisine, offset, id_counter, keyList):
    url = "https://api.yelp.com/v3/businesses/search"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    params = {
        "location": location,
        "categories": cuisine,
        "limit": 20,
        "offset": offset
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        res = response.json()
        datas = res['businesses']
        # print(datas)

        for data in datas:
            #only adds uniques in dynamodb
            if data['id'] not in keyList:
                new_data = {}
                new_data['business_id'] = data['id']
                new_data['name'] = data['name']
                new_data['phone'] = data['phone']
                new_data['business_id'] = data['id']
                new_data['address'] = str(data['location']['address1']) + " " + str(data['location']['address2']) + " " + str(data['location']['address3'])
                new_data['city'] = data['location']['city']
                new_data['zip_code'] = data['location']['zip_code']
                new_data['longitude'] =str(data['coordinates']['longitude'])
                new_data['latitude'] = str(data['coordinates']['latitude'])
                new_data['review_count'] = data['review_count']
                data_string = json.dumps(new_data, ensure_ascii=False)
                #writes for dynamodb
                with open('dynamodb_6.json', "a") as file:
                    file.write(data_string + "\n")
                keyList.append(data['id'])

            #adds all in open search
            #writes for opensearch
            header_line = {'index' : 'null'}
            data_header = {'_index' : 'restaurants', '_id' : id_counter}
            header_line['index']  = data_header
            data_line = {'business_id' : data['id'], 'cuisine' : cuisine}
            # {"index": {"_index": "restaurants", "_id": 1}}
            # {"uni": "TQzGf4k3HXyMbnNkYKKQSw", "location": "Brooklyn", "cuisine": "Chinese"}
            header_str = json.dumps(header_line, ensure_ascii=False)
            data_str = json.dumps(data_line, ensure_ascii=False)
            with open('open_search_6.json', "a") as file:
                file.write(header_str + "\n")
                file.write(data_str + "\n")
            id_counter = id_counter + 1
            print(id_counter)
    else:
        print("Error:", response.status_code)
        print(response.text)
    return id_counter

api_key = "0iybhhjidn6Mj94AHsqzgmGWwX0viWAb_lkwxFlgaTv9unxeJ4yE6uSQ4_E-KJ3LTAgctE9RtRu5hmRKJmYnkg6DiCQsPTq4fkgzOuU2xLTkBi-QP-EE1BWWwx0sZXYx"
keyList = []
id_counter = 1
for location in locations:
    for cuisine in cuisines:
        _offset = 0
        for i in range(20):
            id_counter = search_yelp(api_key, location, cuisine, _offset,id_counter,keyList)
            _offset = _offset + 50



# search_yelp(api_key, "Manhattan", "Italian", 0, i,keyList)
# search_yelp(api_key, "Manhattan", "Mexican", 0, i, keyList)