import xmltodict
import re
import sys
import json
import redis
from redis.commands.json.path import Path
from dotenv import load_dotenv
import os
load_dotenv()
REDIS_HOST =  os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
CURRENT_LAW = "bgb_test:1"



def xml2json(xml_file, json_file):
    with open(xml_file, "r") as xml:
        xml_content = xml.read()
    json_content = xmltodict.parse(xml_content)
    with open(json_file, "w") as jsons:
        jsons.write(json.dumps(json_content))
    return json_content

def json2redis(json_file):
    redis_client = redis.Redis(
     host=REDIS_HOST,
     port=REDIS_PORT,
     password=REDIS_PASSWORD
 )
    redis_client.ping()
    redis_client.json().set(CURRENT_LAW, '$', json_file)

def ping_redis():
    redis_client = redis.Redis(
     host=REDIS_HOST,
     port=REDIS_PORT,
     password=REDIS_PASSWORD
 )
    redis_client.ping()
    print(redis_client.ping())

#retrieve data from redis
def get_data_from_redis():
    redis_client = redis.Redis(
     host=REDIS_HOST,
     port=REDIS_PORT,
     password=REDIS_PASSWORD
 )
    redis_client.ping()

# for BGB 471/§357b speical case a change in xml is needed 
    length = redis_client.json().arrlen(CURRENT_LAW, Path('.dokumente.norm'))
    for i in range(length-1):
        try:
            paragraph = redis_client.json().get(CURRENT_LAW, Path(f'.dokumente.norm.[{str(i)}].metadaten.enbez'))
            title = redis_client.json().get(CURRENT_LAW, Path(f'.dokumente.norm.[{str(i)}].metadaten.titel.#text'))
            try:
            #replace \n with space
                title = title.replace("\n", " ")
                paragraph = re.sub(r'\(XXXX\)', '',paragraph)
            except Exception as e:
                pass
            content = redis_client.json().get("bgb_test:1", Path(f'.dokumente.norm.[{str(i)}].textdaten.text.Content.P'))
            if len(content[1]) > 1:
                #determine whether it's a single letter
                try:
                    new_content = ""
                    list_content = ""
                    list_contentlvl1 = ""
                    list_contentlvl2 = ""
                    list_contentlvl3 = ""
                    old_intro = "" 
                    for j in range(len(content)):
                        #determine the number of sentences
                        if "#text" in content[j]:
                            satz_intro = content[j]["#text"]
                            if 'DL' not in content[j]:
                                if j == 0:  
                                    list_contentlvl1 += f"{satz_intro}\n"
                        #determine the number of sentences
                        if 'DL' in content[j]:
                            #determine whether there is a speical case of list of sentences
                            if 'DT' not in content[j]['DL']:
                                anzahl_satz = len(content[j]['DL'])
                                # new_content += f"{satz_intro}\n\n"
                                satz_content = content[j]['DL']
                                list_content += f"{satz_intro}\n"

                            elif content[j]['DL']['DT'] == None : #2410 special case
                                anzahl_satz = 0
                                satz_content = content[j]['DL']['DD']['LA']['#text']
                                list_content += f"{satz_intro}\n    {satz_content}\n"


                            else:
                                anzahl_satz = len(content[j]["DL"]["DT"])
                                satz_number = content[j]['DL']['DT']
                                satz_content = content[j]['DL']['DD']

                            for k in range(anzahl_satz):
                                if 'LA' in satz_content[k]:
                                    if '#text' in satz_content[k]['LA']:
                                        satz_introlvl2 = satz_content[k]['LA']['#text']
                                    if 'DL' in satz_content[k]['LA']:
                                        list_contentlvl2 = ""
                                        anzahl_satzlvl2 = len(satz_content[k]['LA']['DL']['DT'])
                                        satz_numberlvl2 = satz_content[k]['LA']['DL']['DT']
                                        satz_contentlvl2 = satz_content[k]['LA']['DL']['DD']
                                        for l in range(anzahl_satzlvl2):
                                            if "#text" in satz_contentlvl2[l]['LA']:
                                                list_contentlvl2 += f"{satz_numberlvl2[l]} {satz_contentlvl2[l]['LA']['#text']}\n"
                                            else:
                                                list_contentlvl2 += f"{satz_numberlvl2[l]} {satz_contentlvl2[l]['LA']}\n"
                                        if k == 0:
                                            list_contentlvl2 = f"{satz_intro}\n{satz_number[k]}{satz_introlvl2} \n{list_contentlvl2}"
                                        else:
                                            list_contentlvl2 = f"{satz_number[k]}{satz_introlvl2} \n{list_contentlvl2}"
                                        list_content += list_contentlvl2
                                    elif "#text" in satz_content[k]['LA']:
                                        list_content += f"{satz_number[k]} {satz_introlvl2}\n"
                                        list_contentlvl2 = "a"
                                        if satz_intro != old_intro:
                                            list_content = f"{satz_intro}\n{satz_number[k]} {satz_introlvl2}\n"
                                    elif 'DL' not in satz_content[k]['LA']:         
                                        list_contentlvl2 = "" 
                                        if type(satz_content[k]['LA']) == list:         
                                            anzahl_satzlvl2 = len(satz_content[k]['LA'])                                                      
                                            for l in range(anzahl_satzlvl2):
                                                if 'DL' in satz_content[k]['LA'][l]:
                                                    anzahl_satzlvl3 = len(satz_content[k]['LA'][l]['DL']['DT'])
                                                    #print(anzahl_satzlvl3)
                                                    satz_numberlvl3 = satz_content[k]['LA'][l]['DL']['DT']
                                                    satz_contentlvl3 = satz_content[k]['LA'][l]['DL']['DD']
                                                    if "#text" in satz_content[k]['LA'][l]:
                                                        satz_introlvl2 = satz_content[k]['LA'][l]['#text']
                                                        list_contentlvl2 += f"{satz_intro}\n{satz_number[k]} {satz_introlvl2}\n"
                                                    
                                                    for p in range(anzahl_satzlvl3):
                                                        if "#text" in satz_contentlvl3[p]['LA']:
                                                            list_contentlvl3 += f"{satz_numberlvl3[p]} {satz_contentlvl3[p]['LA']['#text']}\n"
                                                            # print(list_contentlvl3) 
                                                    if l == 0:
                                                        list_contentlvl2 += f"{list_contentlvl3}"
                                                    # else:
                                                    #     list_contentlvl2 += f"{satz_introlvl2}\n{list_contentlvl3}"
                                                
                                                else:
                                                    if "#text" in satz_content[k]['LA'][l]:
                                                        list_contentlvl2 += f"{satz_content[k]['LA'][l]['#text']}\n"
                                                        # print(list_contentlvl2) 
                                                    elif type(satz_content[k]['LA']) == list:
                                                        list_contentlvl2 += f"{satz_content[k]['LA'][l]['LA']}\n"
                                        else:
                                            if satz_intro != old_intro:
                                                list_content = f"{satz_intro}\n{satz_number[k]} {satz_content[k]['LA']}\n"
                                            else:
                                                list_content += f"{satz_number[k]} {satz_content[k]['LA']}\n"
                                            # print(list_contentlvl2)
                                        list_content += list_contentlvl2                                 
                

                                old_intro = satz_intro
                               
                            
                            list_contentlvl1 += f"{list_content}\n"

                        elif 'FnR' in content[j]:
                            new_content += ""
                        elif '#text' not in content[j]:
                            if j == 0:
                                list_contentlvl1 = f"{content[j]}\n\n"
                            else: 
                                list_contentlvl1 += content[j] + "\n\n"
                            list_contentlvl2 = ""   

                    content = list_contentlvl1
                except Exception as e:  
                    pass

            print(f"{paragraph} {title} \n\n{content} \n\n\n")
    #       #output to file
            with open("output.txt", "a") as f:
                f.write(f"{paragraph} {title} \n\n{content} \n\n\n")
        except IndexError: 
            pass
        except Exception as e:  
            pass

        



    
    # print(length)


if __name__ == "__main__":
    #   xml_file = sys.argv[1]
    #   json_file = sys.argv[2]
    #   json_data = xml2json(xml_file, json_file)
    #   json2redis(json_data)
    #  ping_redis()
    get_data_from_redis()

    