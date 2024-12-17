import requests
from bs4 import BeautifulSoup
import sys
from urllib.parse import urljoin 

s=requests.Session()
s.headers["User-Agent"]="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

def get_forms(url):
   try:
       response = s.get(url)
       response.raise_for_status()  # Raises an HTTPError for bad responses
       soup = BeautifulSoup(response.content, "html.parser")
       return soup.find_all("form")
   except requests.exceptions.RequestException as e:
       print(f"Error fetching URL {url}: {e}")
       return []

def form_details(form):
    detailsOfFrom={}
    action=form.attrs.get("action")
    method=form.attrs.get("method","get")
    inputs=[]

    for input_tag in form.find_all("input"):
        input_type=input_tag.attrs.get("type","text")
        input_name= input_tag.attrs.get("name")
        input_value= input_tag.attrs.get("value","")
        inputs.append({
            "type": input_type,
            "name": input_name,
            "value":input_value
        })
    detailsOfFrom['action']=action
    detailsOfFrom['method']=method
    detailsOfFrom['inputs']=inputs
    return detailsOfFrom

def vulnerable(response):
    errors={"you have error in your sql syntax",
            "toz taz tiiz character string not ooooaa hackkkedd",
            "quoted string not terminated"
            }
    for error in  errors:
        if error in response.content.decode().lower():
            return True
    return False

def sql_injection_scan(url):
    forms = get_forms(url)
    print(f"[+] detected {len(forms)} forms on {url}.")
    for form in forms:
        details = form_details(form)
        for i in "\"'":
            data = {}
            for input_tag in details["inputs"]:
                if input_tag["type"] == "hidden" or input_tag["value"]:
                    data[input_tag['name']] = input_tag["value"] + i
                elif input_tag["type"] != "submit":
                    data[input_tag['name']] = f"test{i}"
            print(url)
            form_details(form)
            if details["method"] == "post":
                res = s.post(url, data=data)
            elif details["method"] == "get":
                res = s.get(url, params=data)
            if vulnerable(res):
                print("SQL injection attack in link:", url)
            else:
                print("No SQL injection attack detected")
                break

if __name__=="__main__":
    urlTobeChecked="https://yahoo.com"
    sql_injection_scan(urlTobeChecked)